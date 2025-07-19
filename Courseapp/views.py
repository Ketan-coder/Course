from django.contrib.auth.decorators import user_passes_test
from django.db.models.manager import BaseManager
import json
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from utils.models import Activity
from Stock.models import Stock
from .models import FAQ, Course, Language, Quiz, Section, Tag, Lesson, CourseNotes, Article
from Users.models import Instructor, Profile, Student
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from .utils import * 
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

def course_list(request) -> HttpResponse:
    courses: BaseManager[Course] = Course.objects.all()
    request.session["page"] = "course"
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        student_profile = Student.objects.filter(profile=profile).first() or None
        instructor_profile = Instructor.objects.filter(profile=profile).first() or None
        if student_profile:
            request.session['streak'] = student_profile.streak
            request.session['score'] = student_profile.score
            request.session['current_user_type'] = 'student'
        elif instructor_profile:
            request.session['current_user_type'] = 'instructor'

    if request.method == "POST" and "search_term" in request.POST:
        search_term = request.POST["search_term"]
        courses = courses.filter(
            title__icontains=search_term, language__name__icontains=search_term
        ) # Suggested code may be subject to a license. Learn more: ~LicenseLog:1606362085.
    if "course_level" in request.GET:
        filter_by_level = request.GET["course_level"]
        if filter_by_level != "any":
            courses = courses.filter(course_level=filter_by_level)

    if "course_type" in request.GET:
        filter_by_type = request.GET["course_type"]
        if filter_by_type == "any":
            courses = Course.objects.all()
        else:
            courses = courses.filter(course_type=filter_by_type)
    return render(request, "course/course_list.html", locals())


# @user_passes_test(lambda u: Instructor.objects.filter(profile=u.profile).exists())
# def course_create(request):
#     if request.method == 'POST':
#         form = CourseForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('course_list')
#     else:
#         form = CourseForm()
#     return render(request, 'course/course_form.html', {'form': form})

# @user_passes_test(lambda u: Instructor.objects.filter(profile=u.profile).exists())
# def course_update(request, pk):
#     course = get_object_or_404(Course, pk=pk)
#     if request.method == 'POST':
#         form = CourseForm(request.POST, instance=course)
#         if form.is_valid():
#             form.save()
#             return redirect('course_list')
#     else:
#         form = CourseForm(instance=course)
#     return render(request, 'course/course_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: Instructor.objects.filter(profile=u.profile).exists())
def course_create(request) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    instructors = Instructor.objects.all()
    logined_profile = Profile.objects.get(user=request.user)
    logined_instructor = Instructor.objects.filter(profile=logined_profile).first()
    request.session["page"] = "course"
    if request.method == "POST":
        # Manually get data from request.POST for each field
        title = request.POST.get("title")
        description = request.POST.get("description")
        course_type = request.POST.get("course_type")
        course_level = request.POST.get("course_level")
        language_id = request.POST.get("language")
        # instructor_id = request.POST.get("instructor")
        price = request.POST.get("price")
        discount_price = request.POST.get("discount_price")
        is_published = request.POST.get("is_published", False) == "on"
        is_open_to_all = request.POST.get("is_open_to_all", False) == "on"
        prerequisites = request.POST.get("prerequisites")
        circulam = request.POST.get("circulam")

        # Handle file uploads
        thumbnail = request.FILES.get("thumbnail")
        intro_video = request.FILES.get("intro_video")

        # Create the Course instance
        course = Course(
            title=title,
            description=description,
            course_type=course_type,
            course_level=course_level,
            language_id=language_id,
            instructor_id=logined_instructor.id,
            price=price,
            discount_price=discount_price,
            is_published=is_published,
            is_open_to_all=is_open_to_all,
            prerequisites=prerequisites,
            circulam=circulam,
            thumbnail=thumbnail,
            intro_video=intro_video,
        )
        course.save()

        # Handle ManyToMany fields (example for tags)
        selected_tag_ids = request.POST.getlist(
            "selected_tags"
        )  # Assuming hidden inputs named 'selected_tags'
        course.tags.set(selected_tag_ids)

        # handle faq selection
        selected_faq_ids = request.POST.getlist("selected_faqs")
        if selected_faq_ids:
            faqs = FAQ.objects.filter(id__in=selected_faq_ids)
            course.faqs.set(faqs)

        # Handle sections selection
        selected_section_ids = request.POST.getlist("selected_sections")
        if selected_section_ids:
            sections = Section.objects.filter(id__in=selected_section_ids)
            course.sections.set(sections)

        Activity.objects.create(
            user=request.user,
            activity_type="Course Creation",
            description=f"Created course: {title}",
        )

        messages.success(request, "Course created successfully.")

        return redirect("course_list")
    else:
        # You'll need to pass necessary data for dropdowns (languages, instructors)
        languages: BaseManager[Language] = Language.objects.all()
        instructors: BaseManager[Instructor] = Instructor.objects.all()
        return render(
            request,
            "course/course_form.html",
            {"languages": languages, "instructors": instructors,'logined_profile': logined_profile },
        )


@user_passes_test(lambda u: Instructor.objects.filter(profile=u.profile).exists())
def course_update(request, pk) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    print("pk:", pk)
    course: Course = get_object_or_404(Course, pk=pk)
    instructors: BaseManager[Instructor] = Instructor.objects.all()
    logined_profile = Profile.objects.get(user=request.user)
    logined_instructor = Instructor.objects.filter(profile=logined_profile).first()
    lessons = Lesson.objects.all() 
    request.session["page"] = "course"
    if request.method == "POST":
        print("request.POST:", request.POST)
        # Manually get data from request.POST for each field
        course.title = request.POST.get("title")
        course.description = request.POST.get("description")
        course.course_type = request.POST.get("course_type")
        course.course_level = request.POST.get("course_level")
        course.language_id = request.POST.get("language")
        # course.instructor_id = request.POST.get("instructor")
        course.price = request.POST.get("price")
        course.discount_price = request.POST.get("discount_price")
        course.is_published = request.POST.get("is_published", False) == "on"
        course.is_open_to_all = request.POST.get("is_open_to_all", False) == "on"
        course.prerequisites = request.POST.get("prerequisites")
        course.circulam = request.POST.get("circulam")

        # Handle file uploads (check if new files are uploaded)
        thumbnail = request.FILES.get("thumbnail")
        if thumbnail:
            course.thumbnail = thumbnail
        intro_video = request.FILES.get("intro_video")
        if intro_video:
            course.intro_video = intro_video

        course.save()

        # Handle ManyToMany fields (example for tags)
        selected_tag_ids = request.POST.getlist("selected_tags")
        course.tags.set(selected_tag_ids)

        # handle faq selection
        selected_faq_ids = request.POST.getlist("selected_faqs")
        if selected_faq_ids:
            faqs = FAQ.objects.filter(id__in=selected_faq_ids)
            course.faqs.set(faqs)

        # Handle sections selection
        selected_section_ids = request.POST.getlist("selected_sections")
        if selected_section_ids:
            sections = Section.objects.filter(id__in=selected_section_ids)
            course.sections.set(sections)

        Activity.objects.create(
            user=request.user,
            activity_type="Course Update",
            description=f"Updated course: {course.title}",
        )

        messages.success(request, "Course updated successfully.")

        return redirect("course_list")
    else:
        # Pass existing course data and data for dropdowns
        languages: BaseManager[Language] = Language.objects.all()
        instructors = Instructor.objects.all()
        lessons = Lesson.objects.all()
        return render(
            request,
            "course/course_form.html",
            {"course": course, "languages": languages, "instructors": instructors, 'lessons': lessons},
        )

@user_passes_test(lambda u: Instructor.objects.filter(profile=u.profile).exists())
def create_quiz(request) -> HttpResponse:
    request.session["page"] = "course"

    # If editing: Preload quiz for editing
    quiz_id = request.GET.get("quiz_id") or request.POST.get("quiz_id")
    quiz = None
    if quiz_id:
        quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "POST":
        course_id = request.POST.get("course_id")
        section_id = request.POST.get("selected_sections")
        lesson_id = request.POST.get("lesson_id")
        title = request.POST.get("title", "Untitled Quiz")

        # If editing, reuse; else create new
        if not quiz:
            quiz = Quiz.objects.create(title=title)
        else:
            quiz.title = title  # update title if editing

        if course_id:
            quiz.course = get_object_or_404(Course, id=course_id)
        if section_id:
            quiz.section = get_object_or_404(Section, id=section_id)
        if lesson_id:
            quiz.lesson = get_object_or_404(Lesson, id=lesson_id)

        # Parse questions
        questions = {}
        i = 1
        while request.POST.get(f"question_{i}"):
            q_text = request.POST.get(f"question_{i}")
            q_type = request.POST.get(f"type_{i}")
            q_answer = request.POST.get(f"answer_{i}")
            options = []
            for opt in request.POST.getlist(f"options_{i}")[0].split(','):
                options.append({"id": opt, "text": opt})
            questions[str(i)] = {
                "id": str(i),
                "question": q_text,
                "type": q_type,
                "correct_answer": q_answer,
                "options": options
            }
            i += 1

        quiz.questions = questions
        quiz.save()

        Activity.objects.create(
            user=request.user,
            activity_type="Quiz Creation",
            description=f"{'Updated' if quiz_id else 'Created'} quiz: {quiz.title} for section: {quiz.section.title if quiz.section else 'N/A'}",
        )
        messages.success(request, f"Quiz {'updated' if quiz_id else 'created'} successfully.")
        return redirect("course_list")

    return render(request, "course/quiz_form.html", {"quiz": quiz})


def search_tags(request) -> JsonResponse:
    search_term = request.GET.get("q")
    if search_term:
        tags= Tag.objects.filter(name__icontains=search_term).values("id", "name")
        return JsonResponse(list(tags), safe=False)
    return JsonResponse([], safe=False)


def search_sections(request) -> JsonResponse:
    search_term = request.GET.get("q")
    used_sections = Course.objects.values_list('sections__id', flat=True).distinct()
    if search_term:
        sections= Section.objects.filter(title__icontains=search_term).exclude(id__in=used_sections).values(
            "id", "title"
        )
        return JsonResponse(list(sections), safe=False)
    return JsonResponse([], safe=False)

def search_lessons(request) -> JsonResponse:
    search_term = request.GET.get("q")
    used_lessons = Course.objects.values_list('sections__lesson__id', flat=True).distinct()
    if search_term:
        lessons= Lesson.objects.filter(title__icontains=search_term).exclude(id__in=used_lessons).values(
            "id", "title"
        )
        return JsonResponse(list(lessons), safe=False)
    return JsonResponse([], safe=False)


def search_faqs(request) -> JsonResponse:
    search_term = request.GET.get("q")
    if search_term:
        faqs= FAQ.objects.filter(question__icontains=search_term).values(
            "id", "question"
        )
        return JsonResponse(list(faqs), safe=False)
    return JsonResponse([], safe=False)

def search_article(request) -> JsonResponse:
    search_term = request.GET.get("q")
    used_articles = Section.objects.values_list('article__id', flat=True).distinct()
    if search_term:
        articles= Article.objects.filter(title__icontains=search_term).exclude(id__in=used_articles).values(
            "id", "title"
        )
        return JsonResponse(list(articles), safe=False)
    return JsonResponse([], safe=False)

def search_courses_htmx(request):
    try:
        query = request.GET.get("q", "")
        courses = Course.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(language__name__icontains=query) | Q(tags__name__icontains=query) | Q(sections__title__icontains=query) | Q(prerequisites__icontains=query)).distinct()[:10]
        html = render_to_string("components/_search_results.html", {"courses": courses})
        return HttpResponse(html)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

@user_passes_test(lambda u: Instructor.objects.filter(profile=u.profile).exists())
def course_delete(request, pk) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    request.session["page"] = "course"
    course = get_object_or_404(Course, pk=pk)
    if (
        request.method == "POST"
    ): 
        course.delete()
        Activity.objects.create(
            user=request.user,
            activity_type="Course Deletion",
            description=f"Deleted course: {course.title}",
        )
        messages.success(request, "Course deleted successfully.")
        return redirect("course_list")
    return render(request, "course/course_confirm_delete.html", {"course": course})


def course_detail(request, pk) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    course = Course.objects.filter(pk=pk).first()
    if not course:
        return render(request, "course/course_not_found.html")
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    request.session["page"] = "course"
    logged_in_profile = Profile.objects.get(user=user)
    user_review = course.reviews.filter(user=logged_in_profile).first()
    ref = request.GET.get('ref', 'outside')

    if ref != 'outside' and ref != None and ref != '':
        referrer = User.objects.filter(username=ref).first()
        if referrer:
            # Add the course to the referrer's referred courses
            referrer_profile = Profile.objects.get(user=referrer)
            course.referred_by.add(referrer_profile)
            # Log the referral activity
            Activity.objects.create(
                user=user,
                activity_type="Course Referral",
                description=f"Referred by {referrer.username} for course: {course.title}",
            )
            if referrer_profile:
                # Update the referrer profile with bonus points
                bonus_points = 35
                student_profile = Student.objects.filter(profile=referrer_profile).first()
                if student_profile:
                    student_profile.score += bonus_points
                    student_profile.save()
                    # Log the bonus points activity
                    Activity.objects.create(
                        user=referrer,
                        activity_type="Bouns Points Earned",
                        description=f"Earned {bonus_points} bonus points for referring {course.title}",
                    )
    else:
        referrer = None
    if request.method == 'POST':
        if 'submit_review' in request.POST:
            # Handle course review submission
            review_text = request.POST.get('review_text', '').strip()
            rating = request.POST.get('rating', 0)
            if review_text:
                existing_review = course.reviews.filter(user=logged_in_profile).first()
                if existing_review:
                    existing_review.review_text = review_text
                    existing_review.rating = rating
                    existing_review.save()
                    messages.success(request, "Your review has been updated successfully.")
                else:
                    course.reviews.create(
                        user=logged_in_profile,
                        review_text=review_text,
                        rating=rating
                    )
                    messages.success(request, "Your review has been submitted successfully.")
            else:
                messages.error(request, "Review text cannot be empty.")
            return redirect("course_detail", pk=pk)

        elif 'enroll_now' in request.POST or 'buy_now' in request.POST:
            # Enroll the user in the course
            student_profile = Student.objects.filter(profile=logged_in_profile).first()
            if student_profile:
                course.is_bought_by_users.add(logged_in_profile)
                Activity.objects.create(
                    user=user,
                    activity_type="Course Enroll",
                    description=f"Enrolled in course: {course.title}",
                )
                messages.success(request, f"You have successfully enrolled in {course.title}.")
                return redirect("course_detail", pk=pk)
            else:
                return render(request, "course/course_detail.html", {"course": course, "error": "You must have a student profile to enroll."})
        elif 'continue_now' in request.POST:
            # Redirect to the first lesson of the course
            first_section = course.sections.filter(lesson__isnull=False).exclude(lesson__completed_by_users=logged_in_profile).first()
            if first_section:
                first_lesson = first_section.lesson.first()
                if first_lesson:
                    return redirect("video_detail_page", lesson_id=first_lesson.id)
                else:
                    messages.error(request, "No lessons available in this course.")
                    return redirect("course_detail", pk=pk)
            return redirect("course_detail", pk=pk)
    return render(request, "course/course_detail_new_page.html", locals())


def video_detail_page(request,lesson_id) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    request.session["page"] = "course"
    logged_in_profile = Profile.objects.get(user=user)
    student_profile = Student.objects.filter(profile=logged_in_profile).first() or None
    # leaderboard_entry_profile = LeaderboardEntry.objects.filter(profile=logged_in_profile).first() or None
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    
    # Points Check
    required_score = lesson.required_score
    if required_score > 0 and student_profile:
        user_score = student_profile.score if student_profile else 0
        if user_score < required_score:
            messages.error(request,format_html("You need <strong class='text-primary'>{} points</strong> to view this video. Keep learning and earning points!", required_score))
            return redirect('course_list')

    # course = get_object_or_404(Course, sections__lesson__id=lesson_id)
    course = Course.objects.filter(sections__lesson__id=lesson_id).first()
    to_search_sections = course.sections.all().values_list('id', flat=True)
    section = get_object_or_404(Section, id__in=to_search_sections)
    is_completed = lesson.completed_by_users.filter(pk=logged_in_profile.pk).exists()
    stock = Stock.objects.all()
    quizes = Quiz.objects.filter(Q(lesson=lesson) | Q(course=course) | Q(section=section)).distinct()
    course_notes = CourseNotes.objects.filter(course_id=course.id, section_id=section.id)
    questions_list = []
    for quiz in quizes:
        if quiz.questions:
            for qid, question_data in quiz.questions.items():
                question_data['quiz_id'] = quiz.pk  # optional
                questions_list.append(question_data)
    return render(request, "course/course_video_detail.html", locals())

def bookmarked_courses(request) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    request.session["page"] = "course"
    profile = get_object_or_404(Profile, user=user)
    bookmarked_courses = Course.objects.filter(bookmarked_by_users=profile).all()
    return render(request, "course/bookmarked_courses.html", {"bookmarked_courses": bookmarked_courses})

def bookmark_course(request, course_id) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse | JsonResponse:
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"redirect": "/login"}, status=401)

    course = get_object_or_404(Course, pk=course_id)
    profile = get_object_or_404(Profile, user=user)

    is_bookmarked = course.bookmarked_by_users.filter(pk=profile.pk).exists()

    if is_bookmarked:
        course.bookmarked_by_users.remove(profile)
        # Return HTML for "Save" button
        html = format_html('''
            <div id="save-button">
                <button class="btn btn-outline-success btn-sm"
                    hx-post="{}"
                    hx-target="#save-button"
                    hx-swap="outerHTML">
                    <i class="ph ph-floppy-disk"></i> Save
                </button>
            </div>
        ''', reverse("bookmark_course", args=[course.pk]))
    else:
        course.bookmarked_by_users.add(profile)
        actual_added_points = update_score(request,profile, 15)
        # Return HTML for "Remove" button
        html = format_html('''
            <div id="save-button">
                <button class="btn btn-outline-danger btn-sm"
                    hx-post="{}"
                    hx-target="#save-button"
                    hx-swap="outerHTML">
                    <i class="ph ph-x-circle"></i> Remove
                </button>
            </div>
        ''', reverse("bookmark_course", args=[course.pk]))
    Activity.objects.create(
        user=user,
        activity_type="Course Update",
        description=f"{'Bookmarked' if not is_bookmarked else 'Removed bookmark from'} course: {course.title}",
    )
    return HttpResponse(html)

@csrf_exempt
def mark_lesson_complete(request, lesson_id, user_profile) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    user = request.user
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    try:
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        profile = get_object_or_404(Profile, pk=user_profile)

        # Check if the lesson is already completed by the user
        if lesson.completed_by_users.filter(pk=profile.pk).exists():
            # If already completed, remove the user from completed users
            return JsonResponse({"message": "Lesson already completed."}, status=400)
        else:
            # If not completed, add the user to completed users
            lesson.completed_by_users.add(profile)
    
        

        # Handle Student Streak Logic
        if Student.objects.filter(profile=profile).exists():
            update_streak(request,profile)

        # Handle Student Score Logic
        if Student.objects.filter(profile=profile).exists():
            update_score(request,profile)

        # rediect the user to the next video or lesson
        section = get_object_or_404(Section, lesson__id=lesson_id)

        next_lesson = section.lesson.filter(id__gt=lesson_id).exclude(completed_by_users=profile,id=lesson_id).first()
        if next_lesson:
            lesson_id = next_lesson.id
            return JsonResponse({"next_lesson_id": lesson_id})
        
        Activity.objects.create(
            user=user,
            activity_type="Lesson Completion",
            description=f"Completed lesson: {lesson.title}",
        )
        
        url = reverse("video_detail_page", kwargs={"lesson_id": lesson_id})
        return JsonResponse({"next_lesson_url": url})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def create_tag(request) -> HttpResponse:
    if request.method != "POST":
        return HttpResponse(
            """<div class="alert alert-danger border-0 rounded-0 d-flex align-items-center" role="alert">
                <i class="fa-light fa-exclamation-circle text-danger-emphasis me-2"></i>
                <div>Invalid request method.</div>
            </div>""",
            status=405
        )

    name = request.POST.get("name")
    if not name:
        return HttpResponse(
            """<div class="alert alert-danger border-0 rounded-0 d-flex align-items-center" role="alert">
                <i class="fa-light fa-exclamation-circle text-danger-emphasis me-2"></i>
                <div>Tag name is required.</div>
            </div>""",
            status=400
        )

    try:
        tag_id = request.POST.get("id")
        if tag_id:
            tag = get_object_or_404(Tag, id=tag_id)
            tag.name = name
            tag.save()
            
            Activity.objects.create(
                user=request.user,
                activity_type="Course Update",
                description=f"Created tag: {tag.name}",  
            )
            return HttpResponse(
                """<div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>Tag <strong>{}</strong> updated successfully.</div>
                </div>""".format(name)
            )
        else:
            tag = Tag.objects.create(name=name)
            
            Activity.objects.create(
                user=request.user,
                activity_type="Course Update",
                description=f"Created tag: {tag.name}",
            )
            return HttpResponse(
                """<div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>Tag <strong>{}</strong> created successfully.</div>
                </div>""".format(name),
                status=201
            )
    except ValidationError as e:
        return HttpResponse(
            """<div class="alert alert-danger border-0 rounded-0 d-flex align-items-center" role="alert">
                <i class="fa-light fa-exclamation-circle text-danger-emphasis me-2"></i>
                <div>Validation error: {}</div>
            </div>""".format(', '.join(e.messages)),
            status=400
        )
    except Exception as e:
        return HttpResponse(
            """<div class="alert alert-danger border-0 rounded-0 d-flex align-items-center" role="alert">
                <i class="fa-light fa-exclamation-circle text-danger-emphasis me-2"></i>
                <div>Error: {}</div>
            </div>""".format(str(e)),
            status=500
        )

def create_section(request) -> HttpResponse:
    if request.method != "POST":
        return HttpResponse(
            """<div class="alert alert-danger border-0 rounded-0 d-flex align-items-center" role="alert">
                <i class="fa-light fa-exclamation-circle text-danger-emphasis me-2"></i>
                <div>Invalid request method.</div>
            </div>""",
            status=405
        )

    title = request.POST.get("title")
    if not title:
        return HttpResponse(
            """<div class="alert alert-danger border-0 rounded-0 d-flex align-items-center" role="alert">
                <i class="fa-light fa-exclamation-circle text-danger-emphasis me-2"></i>
                <div>Title is required.</div>
            </div>""",
            status=400
        )

    try:
        print("Request POST ==>" + str(request.POST))
        section_id = request.POST.get("id")
        order = request.POST.get("order", 0)
        is_open = request.POST.get("is_open", False) == "on"
        article = request.POST.get("article", "")
        content = request.POST.get("content", "")
        is_generate_content_using_ai = request.POST.get("is_generate_quiz", False) == "on"
        prompt = request.POST.get("prompt", "")

        selected_lessons = request.POST.getlist("selected_lesson")
        if selected_lessons:
            selected_lessons = Lesson.objects.filter(id__in=selected_lessons)

        if article:
            article = Article.objects.filter(id=article).first()

        if section_id:
            section = get_object_or_404(Section, id=section_id)
            section.title = title
            section.order = order or 0
            section.is_open = is_open or False
            section.content = content

            if selected_lessons:
                section.lesson.set(selected_lessons)  
            
            if article:
                section.article = article
            
            section.save(prompt=prompt, is_generate_content_using_ai=is_generate_content_using_ai)  # Save prompt if needed
            return HttpResponse(
                """<div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>Section <strong>{}</strong> updated successfully.</div>
                </div>""".format(title)
            )
        else:
            section = Section.objects.create(title=title, order=order, is_open=is_open)
            if content:
                section.content = content
            if article:
                section.article = article
            if selected_lessons:
                section.lesson.set(selected_lessons)  # Update lessons
            section.save(prompt=prompt)
            return HttpResponse(
                """<div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>Section <strong>{}</strong> created successfully.</div>
                </div>""".format(title),
                status=201
            )
    except Exception as e:
        print(e)
        return HttpResponse(
            """<div class="alert alert-danger border-0 rounded-0 d-flex align-items-center" role="alert">
                <i class="fa-light fa-exclamation-circle text-danger-emphasis me-2"></i>
                <div>Error: {}</div>
            </div>""".format(str(e)),
            status=500
        )


def create_lesson(request) -> HttpResponse:
    if request.method != "POST":
        return HttpResponse(
            """<div class="alert alert-danger border-0 rounded-0 d-flex align-items-center" role="alert">
                <i class="fa-light fa-exclamation-circle text-danger-emphasis me-2"></i>
                <div>Invalid request method.</div>
            </div>""",
            status=405
        )

    title = request.POST.get("title")
    if not title:
        return HttpResponse(
            """<div class="alert alert-danger border-0 rounded-0 d-flex align-items-center" role="alert">
                <i class="fa-light fa-exclamation-circle text-danger-emphasis me-2"></i>
                <div>Title is required.</div>
            </div>""",
            status=400
        )

    try:
        lesson_id = request.POST.get("id")
        description = request.POST.get("description", "")
        order = request.POST.get("order", 0)
        required_score = request.POST.get("required-score", 0)
        video_url = request.POST.get("video-url", "")
        # section_id = request.POST.get("section_id", 1)
        # section = get_object_or_404(Section, pk=section_id)

        if lesson_id:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            lesson.title = title
            lesson.content = description
            if "thumbnail" in request.FILES:
                lesson.thumbnail = request.FILES["thumbnail"]
            if "video" in request.FILES:
                lesson.video = request.FILES["video"]
            else:
                lesson.video_url = video_url
            lesson.order = order
            lesson.required_score = required_score
            lesson.save()
            return HttpResponse(
                """<div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>Lesson <strong>{}</strong> updated successfully.</div>
                </div>""".format(title)
            )
        else:
            lesson = Lesson.objects.create(
                title=title,
                content=description,
                order=order,
                required_score=required_score,
            )
            if "thumbnail" in request.FILES:
                lesson.thumbnail = request.FILES["thumbnail"]
            if "video" in request.FILES:
                lesson.video = request.FILES["video"]
            else:
                lesson.video_url = video_url
            lesson.save()
            return HttpResponse(
                """<div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>Lesson <strong>{}</strong> created successfully.</div>
                </div>""".format(title),
                status=201
            )
    except Exception as e:
        return HttpResponse(
            """<div class="alert alert-danger border-0 rounded-0 d-flex align-items-center" role="alert">
                <i class="fa-light fa-exclamation-circle text-danger-emphasis me-2"></i>
                <div>Error: {}</div>
            </div>""".format(str(e)),
            status=500
        )


def create_faq(request) -> HttpResponse:
    if request.method != "POST":
        return HttpResponse(
            """<div class="alert alert-danger border-0 rounded-0 d-flex align-items-center" role="alert">
                <i class="fa-light fa-exclamation-circle text-danger-emphasis me-2"></i>
                <div>Invalid request method.</div>
            </div>""",
            status=405
        )

    question = request.POST.get("question")
    if not question:
        return HttpResponse(
            """<div class="alert alert-danger border-0 rounded-0 d-flex align-items-center" role="alert">
                <i class="fa-light fa-exclamation-circle text-danger-emphasis me-2"></i>
                <div>Question is required.</div>
            </div>""",
            status=400
        )

    try:
        faq_id = request.POST.get("id")
        answer = request.POST.get("answer", "")

        if faq_id:
            faq = get_object_or_404(FAQ, id=faq_id)
            faq.question = question
            faq.answer = answer
            faq.save()
            return HttpResponse(
                """<div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>FAQ <strong>{}</strong> updated successfully.</div>
                </div>""".format(question)
            )
        else:
            faq = FAQ.objects.create(question=question, answer=answer)
            return HttpResponse(
                """<div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>FAQ <strong>{}</strong> created successfully.</div>
                </div>""".format(question),
                status=201
            )
    except Exception as e:
        return HttpResponse(
            """<div class="alert alert-danger border-0 rounded-0 d-flex align-items-center" role="alert">
                <i class="fa-light fa-exclamation-circle text-danger-emphasis me-2"></i>
                <div>Error: {}</div>
            </div>""".format(str(e)),
            status=500
        )

def create_course_notes(request) -> HttpResponse:
    try:
        if request.method == "POST":
            student_id = request.POST.get("student_id")
            if student_id:
                student = Student.objects.get(pk=student_id)
            else:
                return JsonResponse({"error": "Student not found."}, status=400)
            course_id = request.POST.get("course_id")
            section_id = request.POST.get("section_id")
            lesson_id = request.POST.get("lesson_id")
            notes = request.POST.get("notes")
            course_notes = CourseNotes.objects.create(user=student,section_id=section_id, course_id=course_id, lesson_id=lesson_id, note_text=notes)
            # return JsonResponse({"id": course_notes.pk, "notes": course_notes.notes})
            return HttpResponse(
                f"""
                <div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>{student.profile.user.first_name} left a note: <strong>{notes}</strong></div>
                </div>
                """
            )
        return HttpResponse("Invalid request.", status=400)
    except Exception as e:
        print(str(e))
        return JsonResponse({"error": str(e)}, status=400)
    
def get_course_notes_htmx(request, course_id, section_id=None, lesson_id=None):
    try:
        if request.method != "GET":
            return JsonResponse({"error": "Invalid request method."}, status=400)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated."}, status=401)

        lesson = None
        if lesson_id:
            try:
                lesson = Lesson.objects.get(id=lesson_id)
            except Lesson.DoesNotExist:
                return JsonResponse({"error": "Lesson not found"}, status=404)

        course_notes = CourseNotes.objects.filter(course_id=course_id)
        if section_id:
            course_notes = course_notes.filter(section_id=section_id)
        if lesson:
            course_notes = course_notes.filter(lesson=lesson)

        return render(
            request,
            "course/components/course_notes_list.html",
            {"course_notes": course_notes, "lesson": lesson},
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@login_required
def submit_quiz(request, quiz_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_answer = data.get('answer')
            quiz_type = data.get('quiz_type')
            quiz_score = data.get('quiz_score')

            if not user_answer:
                return JsonResponse({"error": "Answer is required"}, status=400)
            
            print("request.POST ==> ",request.POST)
            print("quiz_id ==> ",quiz_id)

            quiz = get_object_or_404(Quiz, id=quiz_id)
            profile = get_object_or_404(Profile, user=request.user)

            for qid, qdata in (quiz.questions or {}).items():
                correct_answer = qdata.get("answer") if qdata.get("type") != 'DRAG_DROP' else qdata.get("correct_mapping")
                # FIX DRAG AND DROP SUBMISSION
                # if qdata.get("type") == 'DRAG_DROP':
                #     if correct_answer and str(user_answer).strip().lower() == str(correct_answer).strip().lower():
                #         qdata["is_completed"] = True
                #         quiz.questions[qid] = qdata
                #         quiz.save(update_fields=["questions"])
                #         quiz.completed_by_users.add(profile)
                #         update_score(request, profile, 10)
                #         update_streak(request, profile)
                #         Activity.objects.create(
                #             user=request.user,
                #             activity_type="Quiz Completion",
                #             description=f"Completed quiz: {quiz.title} with answer: {user_answer}",
                #         )
                #         return JsonResponse({"status": "completed"})
                

                print("user_answer ==> ",user_answer)
                print("correct_answer ==> ",correct_answer)
                print("quiz_type ==> ",quiz_type)
                print("qdata.get('type') ==> ",qdata.get('type'))
                if isinstance(correct_answer, str) and ',' in correct_answer:
                    correct_set = set(map(str.strip, correct_answer.lower().split(',')))
                    user_set = set(map(str.strip, [x.lower() for x in user_answer])) if isinstance(user_answer, list) else set(map(str.strip, user_answer.lower().split(',')))
                    if correct_set == user_set:
                        if qdata.get("type") == quiz_type:
                            print("quiz_type ==> ",quiz_type)
                            print("qdata.get('type') ==> ",qdata.get('type'))
                            qdata["is_completed"] = True
                            quiz.questions[qid] = qdata
                            print("quiz.questions[qid] ==> ",quiz.questions[qid])
                            print("quiz ==> ",quiz)
                            quiz.save(update_fields=["questions"])
                            quiz.completed_by_users.add(profile)
                            update_score(request, profile, 10)
                            update_streak(request, profile)
                            Activity.objects.create(
                                user=request.user,
                                activity_type="Quiz Completion",
                                description=f"Completed quiz: {quiz.title} with answer: {user_answer}",
                            )
                            return JsonResponse({"status": "completed"})
                # Handle non-multiple cases as before
                
                elif str(user_answer).strip().lower() == str(correct_answer).strip().lower() and qdata.get("type") != 'DRAG_DROP':
                    if qdata.get("type") == quiz_type:
                        print("quiz_type ==> ",quiz_type)
                        print("qdata.get('type') ==> ",qdata.get('type'))
                        qdata["is_completed"] = True
                        quiz.questions[qid] = qdata
                        print("quiz.questions[qid] ==> ",quiz.questions[qid])
                        print("quiz ==> ",quiz)
                        quiz.save(update_fields=["questions"])
                        print("quiz.questions[qid] ==> ",quiz.questions[qid])
                        quiz.completed_by_users.add(profile)
                        update_score(request, profile, 10)
                        update_streak(request, profile)
                        Activity.objects.create(
                            user=request.user,
                            activity_type="Quiz Completion",
                            description=f"Completed quiz: {quiz.title} with answer: {user_answer}",
                        )
                        return JsonResponse({"status": "completed"})


            return JsonResponse({"status": "incorrect"}, status=200)

        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)}, status=400)
        
@csrf_exempt
def submit_drag_and_drop_quiz(request, quiz_id):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed."}, status=405)

    try:
        data = json.loads(request.body)
        user_answer = data.get("user_answer")  # expected as a dict of "0": "value", ...

        if not user_answer or not isinstance(user_answer, dict):
            return JsonResponse({"error": "Invalid or missing user answer"}, status=400)

        quiz = get_object_or_404(Quiz, id=quiz_id)
        profile = get_object_or_404(Profile, user=request.user)
        questions = quiz.questions

        for qid, qdata in questions.items():
            if qdata.get("type") != "DRAG_DROP":
                continue

            correct_mapping = qdata.get("correct_mapping")
            if not correct_mapping:
                continue

            # Normalize both dicts as strings for key-wise comparison
            correct_items = sorted(correct_mapping.items())
            user_items = sorted(user_answer.items())

            if correct_items == user_items:
                qdata["is_completed"] = True
                quiz.questions[qid] = qdata
                quiz.save(update_fields=["questions"])
                quiz.completed_by_users.add(profile)

                update_score(request, profile, qdata.get("score_on_completion", 10))
                update_streak(request, profile)

                Activity.objects.create(
                    user=request.user,
                    activity_type="Quiz Completion",
                    description=f"Completed drag-and-drop quiz: {quiz.title} with answer: {user_answer}",
                )

                return JsonResponse({"status": "completed", "question_id": qid})

        return JsonResponse({"status": "incorrect", "message": "No match found"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
def quiz_warmup_start(request):
    quiz = Quiz.objects.filter(course__isnull=True, section__isnull=True, lesson__isnull=True).first()  # or filter by course/lesson if needed
    if not quiz:
        return redirect("signup")  # fallback

    return redirect("quiz_warmup_question", quiz_id=quiz.pk, qid=1)

# views.py
def quiz_warmup_question(request, quiz_id, qid):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions or {}
    current_q = str(qid)
    request.session["page"] = "course"
    if current_q not in questions:
        return redirect("signup")

    qdata = questions[current_q]
    total = len(questions)
    qdata.update({
        "id": current_q,
        "progress_percentage": int((int(current_q) / total) * 100),
        "current_question_number": int(current_q),
        "total_questions": total,
        "type": qdata.get("type") or "SINGLE_SELECT",
        "correct_mapping": qdata.get("correct_mapping", {})
    })

    return render(request, "components/quiz_warmup_page.html", {
        "quiz_data": qdata,
        "quiz_id": quiz_id,
        "next_qid": int(current_q) + 1
    })


def edit_tag(request, tag_id):
    if request.method != "POST":
        return HttpResponse("Invalid request method.", status=405)
    tag = get_object_or_404(Tag, id=tag_id)
    tag.name = request.POST.get("name")
    tag.save()

    # Return updated tag UI or just a success message
    return render(request, "components/updated_tag_list.html", {"tags": Tag.objects.all()})


def create_or_edit_article(request):
    request.session["page"] = "course"
    if not request.user.is_authenticated:
        return redirect("login")
    
    user = request.user
    instructor = Instructor.objects.filter(profile__user=user).first() or None
    if not instructor:
        return HttpResponse("You must be an instructor to create or edit articles.", status=403)
    
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        article_id = request.POST.get("article_id", None)
        if not title or not content:
            return HttpResponse("Title and content are required.", status=400)

        if article_id:
            article = get_object_or_404(Article, id=article_id)
            article.title = title
            article.content = content
            article.author = instructor
            article.save()
        else:
            article = Article.objects.create(title=title, content=content, author=instructor)

        return redirect("course_list")

    else:
        if request.method == "GET":
            article_id = request.GET.get("article_id", None)
            if article_id:
                article = get_object_or_404(Article, id=article_id)
                # If article_id is provided, fetch the article for editing
                if not article:
                    return HttpResponse("Article not found.", status=404)
            else:
                article = None
        return render(request, "course/article_form.html", {"article": article})
    
def article_detail(request, article_id):
    request.session["page"] = "course"
    article = get_object_or_404(Article, id=article_id)
    if not request.user.is_authenticated:
        return redirect("login")
    
    user = request.user
    student = Student.objects.filter(profile__user=user).first() or None
    # if not student:
    #     return HttpResponse("You must be an instructor to view articles.", status=403)

    return render(request, "course/article_detail.html", locals())

def lesson_form(request, lesson_id=None) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    request.session["page"] = "course"
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    instructor = Instructor.objects.filter(profile__user=user).first()
    if not instructor:
        return HttpResponse("You must be an instructor to create lessons.", status=403)
    
    lesson = None

    if lesson_id:
        lesson = get_object_or_404(Lesson, id=lesson_id)
        # Fetch existing lesson data for editing
        if not lesson:
            messages.error(request, "Lesson not found.")
            return redirect("course_list")

    if request.method == "POST":

        # Form Fields
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        order = request.POST.get("order") or 0
        required_score = request.POST.get("required_score") or 0
        video_url = request.POST.get("video_url", "").strip()
        video_path = request.POST.get("video_path", "")
        # section_id = request.POST.get("section_id")

        if not title:
            return JsonResponse({"error": "Title is required"}, status=400)

        # section = get_object_or_404(Section, pk=section_id) if section_id else None
        # lesson_id = request.POST.get("lesson_id")

        # Create or update
        if lesson_id:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            message = "updated"
        else:
            lesson = Lesson(title=title)
            message = "created"

        # Assign all fields
        lesson.title = title
        lesson.description = description
        lesson.order = order
        lesson.required_score = required_score

        if video_path:
            lesson.video = video_path
            lesson.video_url = ""  # Clear URL if uploading file
        elif video_url:
            lesson.video_url = video_url

        if "thumbnail" in request.FILES:
            lesson.thumbnail = request.FILES["thumbnail"]

        lesson.save()

        # Log activity
        Activity.objects.create(
            user=user,
            activity_type="Lesson Creation",
            description=f"{message.capitalize()} lesson: {lesson.title}"
        )

        # Return for Uppy (XHRUpload expects status 200)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": True, "redirect": "/courses/"})

        messages.success(request, f"Lesson '{lesson.title}' {message} successfully.")
        return redirect("course_list")

    return render(request, "course/lesson_form.html", locals())