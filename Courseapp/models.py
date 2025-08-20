from typing import Literal
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from requests import Response
from utils.media_handler import MediaHandler
from decimal import Decimal
from utils.utils import generate_quiz_from_content
from utils.decorators import check_load_time, retry_on_failure
from .model_manager import *
from django.utils import timezone

def validate_discount(value) -> None:
    if value < 0:
        raise ValidationError("Discount price must be non-negative.")
    
class Language(models.Model):
    name = models.CharField(max_length=20, unique=True)
    symbol = models.CharField(max_length=5, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Course(models.Model):
    course_uuid = models.UUIDField(unique=True, editable=False, blank=True, null=True)
    course_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course_type = models.CharField(max_length=10, choices=[('free', 'Free'), ('paid', 'Paid')], default='free')
    course_level = models.CharField(
        max_length=15,
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced'), ('all', 'All')],
        default='beginner'
    )
    learning_objectives = models.JSONField(default=list, blank=True, null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='courses', blank=True, null=True)
    instructor = models.ForeignKey('Users.Instructor', on_delete=models.CASCADE, related_name='courses') # Circular import fixed by using string
    thumbnail = models.ImageField(upload_to='course_thumbnails', blank=True, null=True)
    sections = models.ManyToManyField('Section', related_name='courses', blank=True)
    intro_video = models.FileField(upload_to='intro_videos', blank=True, null=True)
    tags = models.ManyToManyField('Tag', related_name='courses', blank=True)
    prerequisites = models.TextField(blank=True, null=True)
    circulam = models.TextField(blank=True, null=True)
    faqs = models.ManyToManyField('FAQ', related_name='courses', blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    discount_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, validators=[validate_discount])
    is_published = models.BooleanField(default=False)
    is_open_to_all = models.BooleanField(default=True)
    required_points = models.PositiveIntegerField(default=0, help_text="Required Points to Unlock the scores")
    is_bought_by_users = models.ManyToManyField('Users.Profile', related_name='bought_courses', blank=True)
    bookmarked_by_users = models.ManyToManyField('Users.Profile', related_name='bookmarked_courses', blank=True)
    completed_by_users = models.ManyToManyField('Users.Profile', related_name='completed_courses', blank=True)
    reviews = models.ManyToManyField('CourseReview', related_name='courses', blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    referred_by = models.ManyToManyField('Users.Profile', related_name='referred_courses', blank=True)
    is_deleted = models.BooleanField(default=False)
    is_class_room_course = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    objects = CourseManager()  # Default manager
    all_objects = models.Manager()  # Optional: to access deleted too

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    @check_load_time
    @retry_on_failure(retries=3, delay=2)
    def generate_qr(self, ref="outside", auto_save=False):
        import qrcode
        from io import BytesIO
        from django.core.files.base import ContentFile
        from django.conf import settings

        if self.instructor:
            ref = self.instructor.profile.user.username

        # if settings.DEBUG:
        #     url = f"http://127.0.0.1/courses/{self.pk}/?ref={ref}"
        # else:
        # https://calsie.com.au/course/course/1/?ref=sajan_giri
        url = f"https://calsie.com.au/course/course/{self.pk}/?ref={ref}"
        qr = qrcode.make(url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        filename = f"{self.title[:10]}-qr.png"
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

        if auto_save:
            super(Course, self).save(update_fields=['qr_code'])

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('course_detail', kwargs={'pk': self.pk})


    @check_load_time
    @retry_on_failure(retries=3, delay=2)
    def save(self, create_qr=False, enable_ad_revenue = False,*args, **kwargs):
        self.extra_fields['last_updated'] = str(self.updated_at)
        self.extra_fields['is_active'] = self.is_published

        try:
            price = Decimal(self.price)
            discount_price = Decimal(self.discount_price)
            if price > 0:
                discount_percentage: Decimal = round(((price - discount_price) / price) * 100, 2)
            else:
                discount_percentage = 0
            self.extra_fields['discount_percentage'] = float(discount_percentage)
        except Exception as e:
            print(f"Error calculating discount percentage: {e}")
            self.extra_fields['discount_percentage'] = 0  # Or handle it as needed

        if self.intro_video and ('_resized' not in self.intro_video.name or '_optimized' not in self.intro_video.name):
            resized_path = MediaHandler.optimize_video(self.intro_video)
            if resized_path:
                self.intro_video = resized_path

        # Removed MediaHandler import and usage to fix circular import issue
        # from utils.media_handler import MediaHandler
        if self.thumbnail and '_resized' not in self.thumbnail.name:
            resized_path = MediaHandler.resize_image(self.thumbnail, size=(150, 150))
            if resized_path:
                self.thumbnail = resized_path

        if not self.qr_code and create_qr:
            self.generate_qr(auto_save=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the associated media files when the model instance is deleted
        # Removed MediaHandler import and usage to fix circular import issue
        # from utils.media_handler import MediaHandler
        if self.thumbnail:
            MediaHandler.delete_media_file(self.thumbnail.name)
        if self.video:
            MediaHandler.delete_media_file(self.video.name)
        if self.qr_code:
            MediaHandler.delete_media_file(self.qr_code.name)
        super().delete(*args, **kwargs)


class Section(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_open = models.BooleanField(default=True)
    article = models.ForeignKey('Article', on_delete=models.SET_NULL, related_name='sections', blank=True, null=True)
    lesson = models.ManyToManyField('Lesson', related_name='sections', blank=True)
    is_deleted = models.BooleanField(default=False)
    instructor = models.ForeignKey('Users.Instructor', on_delete=models.CASCADE, related_name='sections', default=1)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SectionManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.title + " - Open? " + str(self.is_open)
    
    class Meta:
        ordering: list[str] = ['order']
    
    @check_load_time
    @retry_on_failure(retries=3, delay=2)
    def save(self, prompt='', is_generate_content_using_ai=False,*args, **kwargs):
        self.extra_fields['last_updated'] = str(self.updated_at)
        if not self.instructor:
            raise ValueError("Instructor is required")
        # Generate quiz from the first lesson's content if it exists
        if is_generate_content_using_ai:
            related_quizes = Quiz.objects.filter(section=self)
            if not related_quizes.exists():
                quiz_data = generate_quiz_from_content(self.title, self.lesson.first().content if self.lesson.exists() else '', prompt=prompt)
                if quiz_data:
                        quiz = Quiz.objects.create(
                            section=self,
                            title=f"{self.title} Quiz",
                            questions=quiz_data,
                            is_inside_video=False,
                            max_score=Decimal('100.0'),
                            passing_score=Decimal('50.0'),
                            required_score=5
                        )
                        print(f"Quiz created for section {self.title}: {quiz.title}")
                else:
                    print(f"No quiz data generated for section {self.title}. Please check the lesson content.")
            else:
                print(f"Quiz already exists for section {self.title}. No new quiz created.")
        super().save(*args, **kwargs)


class Lesson(models.Model):
    # course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    # section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    video = models.FileField(upload_to='lesson_videos', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='lesson_thumbnails', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_open = models.BooleanField(default=True)
    completed_by_users = models.ManyToManyField('Users.Profile', related_name='completed_lessons', blank=True)
    bookmarked_by_users = models.ManyToManyField('Users.Profile', related_name='bookmarked_lessons', blank=True)
    content = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    required_score = models.PositiveIntegerField(default=0)
    instructor = models.ForeignKey('Users.Instructor', on_delete=models.CASCADE, related_name='lesson', default=1)
    is_deleted = models.BooleanField(default=False)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = LessonManager()
    all_objects = models.Manager()

    class Meta:
        ordering: list[str] = ['order']

    def __str__(self):
        return f"{self.title}"

    @check_load_time
    @retry_on_failure(retries=3, delay=2)
    def save(self, *args, **kwargs):
        self.extra_fields['last_updated'] = str(self.updated_at)
        if not self.instructor:
            raise ValueError("Instructor is required")
        if self.video and '_resized' not in self.video.name:
            resized_path = MediaHandler.optimize_video(self.video)
            if resized_path:
                self.video = resized_path
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the associated media files when the model instance is deleted
        # Removed MediaHandler import and usage to fix circular import issue
        # from utils.media_handler import MediaHandler
        if self.thumbnail:
            MediaHandler.delete_media_file(self.thumbnail.name)
        if self.video:
            MediaHandler.delete_media_file(self.video.name)
        super().delete(*args, **kwargs)


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, related_name='quizzes', blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, related_name='quizzes', blank=True, null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, related_name='quizzes', blank=True, null=True)
    title = models.CharField(max_length=200)
    questions = models.JSONField(blank=True, null=True)
    is_inside_video = models.BooleanField(default=False)
    completed_by_users = models.ManyToManyField('Users.Profile', related_name='completed_quizzes', blank=True)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))
    passing_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'))
    required_score = models.PositiveIntegerField(default=0)
    instructor = models.ForeignKey('Users.Instructor', on_delete=models.CASCADE, related_name='quiz', default=1)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    objects = QuizManager()
    all_objects = models.Manager()

    class Meta:
        ordering: list[str] = ['-created_at'] 

    def __str__(self) -> str:
        if self.section:
            return f"{self.section.title} - {self.title}"
        if self.course:
            return f"{self.course.title} - {self.title}"
        if self.lesson:
            return f"{self.lesson.title} - {self.title}"
        else:
            return f"{self.title}"

    def save(self, *args, **kwargs):
        self.extra_fields['last_updated'] = str(self.updated_at)
        if not self.instructor:
            raise ValueError("Instructor is required")
        if not self.questions:
            self.questions = {  
                "1": {"id":"1","question": "What is the capital of France?", "options": [{"id": "Paris", "text": "Paris"}, {"id": "London", "text": "London"}], "type": "MULTIPLE_SELECT", "answer": "Paris", "is_completed": False , "score_on_completion" : 10},
                "2": {"id":"2","question": "What is 2 + 2?", "options": [{"id": "1", "text": "1"}, {"id": "2", "text": "2"}, {"id": "3", "text": "3"}, {"id": "4", "text": "4"}], "type": "SINGLE_SELECT", "answer": "4", "is_completed": False, "score_on_completion" : 10},
                "3": {"id":"3","question": "Capital of Nepal?", "options": [], "type": "TEXT", "answer": "Kathmandu","is_completed": False, "score_on_completion" : 10},
                "4": {
                    "id":"4",
                    "question": "Which monument is shown?",
                    "type": "IMAGE_MC",
                    "image": "media/monuments/eiffel.jpg",
                    "options": [{"id": "Taj Mahal","text": "Taj Mahal",},{"id": "Colosseum","text": "Colosseum",},{"id": "Eiffel Tower","text": "Eiffel Tower",}],
                    "answer": "Eiffel Tower",
                    "is_completed": False,
                    "score_on_completion" : 10
                },
                "5": {
                    "id":"5",
                    "question": "Complete the sentence",
                    "type": "DRAG_DROP",
                    "sentence_parts": ["The quick brown ", None, " jumps over the ", None, " dog."],
                    "draggable_options": [
                        {"id": "fox", "text": "fox"},
                        {"id": "lazy", "text": "lazy"},
                        {"id": "quick", "text": "quick"}
                    ],
                    "correct_mapping": { "0": "fox", "1": "lazy" },
                    "is_completed": False,
                    "score_on_completion" : 10
                }
            }
        super().save(*args, **kwargs)

class QuizSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('in_progress', 'In Progress'),
        ('not_attempted', 'Not Attempted'),
        ('not_started', 'Not Started'),
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey('Users.Profile', on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    passed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    submitted_at = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField(default=dict)

    def calculate_score(self) -> float | Literal[0]:
        correct = 0
        total_questions = len(self.quiz.questions or {})

        for qid, question in (self.quiz.questions or {}).items():
            correct_answer = question.get("answer")
            user_answer = self.answers.get(qid)
            if str(user_answer).strip().lower() == str(correct_answer).strip().lower():
                correct += 1

        self.total: int = total_questions
        self.score: float | Literal[0] = round((correct / total_questions) * 100, 2) if total_questions else 0
        self.passed: bool = self.score >= float(self.quiz.passing_score)
        self.save()
        return self.score


class Tag(models.Model):
    icon_image = models.ImageField(upload_to='tag_icons', blank=True, null=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True, max_length=200)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    objects = TagManager()
    all_objects = models.Manager()

    class Meta:
        ordering: list[str] = ['name']

    def __str__(self) -> str:
            return self.name
        
    def save(self, emoji='📊', icon="chart-line", bgColor="#00e5ff", color="#000", iconColor = "#000" ,*args, **kwargs) -> None:
        self.extra_fields.setdefault('emoji', emoji)
        self.extra_fields.setdefault('icon', icon)
        self.extra_fields.setdefault('bgColor', bgColor)
        self.extra_fields.setdefault('color', color)
        self.extra_fields.setdefault('iconColor', iconColor)
        self.extra_fields['last_updated'] = str(self.updated_at)
        self.extra_fields.setdefault('search_terms', [self.name, 'Active' if self.is_active else 'Inactive'])
        if self.icon_image and '_resized' not in self.icon_image.name:
            resized_path = MediaHandler.resize_image(self.icon_image, size=(50, 50))
            if resized_path:
                self.icon_image = resized_path
        super().save(*args, **kwargs)


class FAQ(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    instructor = models.ForeignKey('Users.Instructor', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    objects = FaqManager()
    all_objects = models.Manager()

    class Meta:
        ordering: list[str] = ['-created_at']

    def __str__(self) -> str:
        return self.question + " \n- " + self.answer[:20]

class CourseReview(models.Model):
    user = models.ForeignKey('Users.Profile', on_delete=models.CASCADE, related_name='course_reviews')
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering: list[str] = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user.user.username} - {self.rating}"

class CourseComment(models.Model):
    user = models.ForeignKey('Users.Profile', on_delete=models.CASCADE, related_name='course_comments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering: list[str] = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user.username} - {self.course.title} - {self.comment_text[:20]}"
    
class CourseSubComment(models.Model):
    user = models.ForeignKey('Users.Profile', on_delete=models.CASCADE, related_name='course_sub_comments')
    course_comment = models.ForeignKey(CourseComment, on_delete=models.CASCADE, related_name='sub_comments')
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering: list[str] = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course_comment.course.title} - {self.comment_text[:20]}"

class PaymentHistory(models.Model):
    payment_uuid = models.UUIDField(unique=True, editable=False, blank=True, null=True)
    user = models.ForeignKey('Users.Profile', on_delete=models.CASCADE, related_name='payment_history')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payment_history')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=50)  # e.g., 'Credit Card', 'PayPal'
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=[('completed', 'Completed'), ('pending', 'Pending'), ('failed', 'Failed')], default='completed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering: list[str] = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user.username} - {self.course.title} - {self.amount} - {self.status}"
    
    def save(self, *args, **kwargs) -> None:
        import socket
        import requests

        # Get device-specific details
        device_name: str = socket.gethostname()
        device_ip: str = socket.gethostbyname(device_name)

        # Get location details using an external service
        try:
            response: Response = requests.get(f"https://ipinfo.io/{device_ip}/json")
            location_data = response.json()
            location: str = f"{location_data.get('city')}, {location_data.get('region')}, {location_data.get('country')}"
        except requests.RequestException as e:
            print(f"Error fetching location data: {e}")
            location = "Unknown"

        self.extra_fields['device_name'] = device_name
        self.extra_fields['device_ip'] = device_ip
        self.extra_fields['location'] = location

        self.extra_fields['last_updated'] = str(self.updated_at)
        super().save(*args, **kwargs)

class CourseCertificate(models.Model):
    user = models.ForeignKey('Users.Profile', on_delete=models.CASCADE, related_name='course_certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    required_score = models.PositiveIntegerField(default=0)
    certificate_code = models.CharField(max_length=100, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering: list[str] = ['-issued_at']

    def __str__(self) -> str:
        return f"{self.user.username} - {self.course.title} - {self.certificate_code}"
    
    def save(self, *args, **kwargs) -> None:
        if not self.certificate_code:
            import uuid
            self.certificate_code = str(uuid.uuid4())
            self.extra_fields['last_updated'] = timezone.now()
        super().save(*args, **kwargs)


class CourseNotes(models.Model):
    user = models.ForeignKey('Users.Student', on_delete=models.CASCADE, related_name='course_notes')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=True, null=True)
    note_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: list[str] = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user.profile.user.first_name} left a note on {self.section.title} - {self.note_text[:20]}"
    
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('Users.Instructor', on_delete=models.CASCADE, related_name='articles')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    objects = ArticleManager()
    all_objects = models.Manager()

    class Meta:
        ordering: list[str] = ['-created_at']

    def __str__(self) -> str:
        return self.title