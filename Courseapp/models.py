from django.db import models
from django.core.exceptions import ValidationError

# Utility function

def validate_discount(value):
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
    # language = models.CharField(max_length=20, choices=[('english', 'English'), ('nepali', 'Nepali')], default='english')
    language = models.OneToOneField(Language, on_delete=models.CASCADE, default=1, related_name='courses', blank=True, null=True)
    instructor = models.ForeignKey('Users.Profile', on_delete=models.CASCADE, related_name='courses')
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    sections = models.ManyToManyField('Section', related_name='courses', blank=True)
    intro_video = models.FileField(upload_to='intro_videos/', blank=True, null=True)
    tags = models.ManyToManyField('Tag', related_name='courses', blank=True)
    prerequisites = models.TextField(blank=True, null=True)
    circulam = models.TextField(blank=True, null=True)
    faqs = models.ManyToManyField('FAQ', related_name='courses', blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    discount_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, validators=[validate_discount])
    is_published = models.BooleanField(default=False)
    is_open_to_all = models.BooleanField(default=True)
    is_bought_by_users = models.ManyToManyField('Users.Profile', related_name='bought_courses', blank=True)
    bookmarked_by_users = models.ManyToManyField('Users.Profile', related_name='bookmarked_courses', blank=True)
    completed_by_users = models.ManyToManyField('Users.Profile', related_name='completed_courses', blank=True)
    reviews = models.ManyToManyField('CourseReview', related_name='courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.extra_fields['last_updated'] = str(self.updated_at)
        self.extra_fields['is_active'] = self.is_published
        self.extra_fields['discount_percentage'] = (
            round(((self.price - self.discount_price) / self.price) * 100, 2)
            if self.price else 0
        )
        super().save(*args, **kwargs)


class Section(models.Model):
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    is_open = models.BooleanField(default=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    video = models.FileField(upload_to='lesson_videos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_open = models.BooleanField(default=True)
    completed_by_users = models.ManyToManyField('Users.Profile', related_name='completed_lessons', blank=True)
    bookmarked_by_users = models.ManyToManyField('Users.Profile', related_name='bookmarked_lessons', blank=True)
    content = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.section.title} - {self.title}"

    def save(self, *args, **kwargs):
        self.extra_fields['last_updated'] = str(self.updated_at)
        super().save(*args, **kwargs)


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='quizzes')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    questions = models.JSONField(blank=True, null=True)
    completed_by_users = models.ManyToManyField('Users.Profile', related_name='completed_quizzes', blank=True)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    passing_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    def save(self, *args, **kwargs):
        self.extra_fields['last_updated'] = str(self.updated_at)
        if not self.questions:
            self.questions = {  # Remove in production, sample only
                "1": {"question": "What is the capital of France?", "options": ["Paris", "London"], "type": "MULTIPLE_SELECT", "answer": "Paris"},
                "2": {"question": "What is 2 + 2?", "options": ["3", "4"], "type": "SINGLE_SELECT", "answer": "4"},
                "3": {"question": "Capital of Nepal?", "options": [], "type": "TEXT", "answer": "Kathmandu"},
            }
        super().save(*args, **kwargs)

class QuizSubmission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey('Users.Profile', on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    passed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField(default=dict)

    def calculate_score(self):
        correct = 0
        total_questions = len(self.quiz.questions or {})

        for qid, question in (self.quiz.questions or {}).items():
            correct_answer = question.get("answer")
            user_answer = self.answers.get(qid)
            if str(user_answer).strip().lower() == str(correct_answer).strip().lower():
                correct += 1

        self.total = total_questions
        self.score = round((correct / total_questions) * 100, 2) if total_questions else 0
        self.passed = self.score >= float(self.quiz.passing_score)
        self.save()
        return self.score


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FAQ(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.question

class CourseReview(models.Model):
    user = models.ForeignKey('Users.Profile', on_delete=models.CASCADE, related_name='course_reviews')
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.rating}"

class CourseComment(models.Model):
    user = models.ForeignKey('Users.Profile', on_delete=models.CASCADE, related_name='course_comments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.comment_text[:20]}"

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
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.amount} - {self.status}"
    
    def save(self, *args, **kwargs):
        import socket
        import requests

        # Get device-specific details
        device_name = socket.gethostname()
        device_ip = socket.gethostbyname(device_name)

        # Get location details using an external service
        try:
            response = requests.get(f"https://ipinfo.io/{device_ip}/json")
            location_data = response.json()
            location = f"{location_data.get('city')}, {location_data.get('region')}, {location_data.get('country')}"
        except requests.RequestException as e:
            location = "Unknown"

        self.extra_fields['device_name'] = device_name
        self.extra_fields['device_ip'] = device_ip
        self.extra_fields['location'] = location

        self.extra_fields['last_updated'] = str(self.updated_at)
        super().save(*args, **kwargs)