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

def course_list(request) -> HttpResponse:
    courses: BaseManager[Course] = Course.objects.all()
    request.session["page"] = "course"

    if request.method == "POST" and "search_term" in request.POST:
        search_term = request.POST["search_term"]
        courses = courses.filter(
            title__icontains=search_term, language__name__icontains=search_term
        ) # Suggested code may be subject to a license. Learn more: ~LicenseLog:1606362085.
    print(request.GET)
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
    return render(request, "course/course_list.html", {"courses": courses})


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

@user_passes_test(lambda u: Instructor.objects.filter(profile=u.profile).exists())
def course_create(request) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    instructors = Instructor.objects.all()
    request.session["page"] = "course"
    if request.method == "POST":
        print(request.POST)
        # Manually get data from request.POST for each field
        title = request.POST.get("title")
        description = request.POST.get("description")
        course_type = request.POST.get("course_type")
        course_level = request.POST.get("course_level")
        language_id = request.POST.get("language")
        instructor_id = request.POST.get("instructor")
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
            instructor_id=instructor_id,
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
            {"languages": languages, "instructors": instructors},
        )


@user_passes_test(lambda u: Instructor.objects.filter(profile=u.profile).exists())
def course_update(request, pk) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    course: Course = get_object_or_404(Course, pk=pk)
    instructors: BaseManager[Instructor] = Instructor.objects.all()
    lessons = Lesson.objects.all() 
    request.session["page"] = "course"
    if request.method == "POST":
        print(request.POST)
        # Manually get data from request.POST for each field
        course.title = request.POST.get("title")
        course.description = request.POST.get("description")
        course.course_type = request.POST.get("course_type")
        course.course_level = request.POST.get("course_level")
        course.language_id = request.POST.get("language")
        course.instructor_id = request.POST.get("instructor")
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
    if request.method == "POST":
        print(request.POST)
        # Either update or create new quiz
        quiz_id = request.POST.get("quiz_id")
        course_id = request.POST.get("course_id")
        section_id = request.POST.get("selected_sections")
        lesson_id = request.POST.get("lesson_id")
        title = request.POST.get("title", "Untitled Quiz")

        if quiz_id:
            quiz = get_object_or_404(Quiz, id=quiz_id)
        else:
            quiz = Quiz.objects.create(title=title)

        if course_id:
            quiz.course = get_object_or_404(Course, id=course_id)
        if section_id:
            quiz.section = get_object_or_404(Section, id=section_id)
        if lesson_id:
            quiz.lesson = get_object_or_404(Lesson, id=lesson_id)

        # Build JSON structure
        questions = {}
        i = 1
        while request.POST.get(f"question_{i}"):
            q_text = request.POST.get(f"question_{i}")
            q_type = request.POST.get(f"type_{i}")
            q_answer = request.POST.get(f"answer_{i}")
            print(q_text, q_type, q_answer)
            # Collect options
            options = []
            opt_index = 0
            for opt in request.POST.getlist(f"options_{i}")[0].split(','):
                options.append({"id": opt, "text": opt})
                opt_index += 1
            # while request.POST.get(f"options_{i}"):
            #     opt = request.POST.get(f"options_{i}_{opt_index}")
            #     options.append({"id": opt, "text": opt})
            #     opt_index += 1

            questions[str(i)] = {
                "id": str(i),
                "question": q_text,
                "type": q_type,
                "correct_answer": q_answer,
                "options": options
            }
            i += 1

        print(questions)

        quiz.questions = questions
        quiz.save()

        Activity.objects.create(
            user=request.user,
            activity_type="Quiz Creation",
            description=f"Created quiz: {quiz.title} for course: {quiz.course.title if quiz.course else 'N/A'}",
        )
        messages.success(request, "Quiz created successfully.")
        return redirect("course_list")
    return render(request, "course/quiz_form.html",locals())


def search_tags(request) -> JsonResponse:
    search_term = request.GET.get("q")
    if search_term:
        tags= Tag.objects.filter(name__icontains=search_term).values("id", "name")
        return JsonResponse(list(tags), safe=False)
    return JsonResponse([], safe=False)


def search_sections(request) -> JsonResponse:
    search_term = request.GET.get("q")
    if search_term:
        sections= Section.objects.filter(title__icontains=search_term).values(
            "id", "title"
        )
        return JsonResponse(list(sections), safe=False)
    return JsonResponse([], safe=False)

def search_lessons(request) -> JsonResponse:
    search_term = request.GET.get("q")
    if search_term:
        lessons= Lesson.objects.filter(title__icontains=search_term).values(
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
    if search_term:
        articles= Article.objects.filter(title__icontains=search_term).values(
            "id", "title"
        )
        return JsonResponse(list(articles), safe=False)
    return JsonResponse([], safe=False)


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
    course = get_object_or_404(Course, pk=pk)
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    request.session["page"] = "course"
    logged_in_profile = Profile.objects.get(user=user)
    ref = request.GET.get('ref', 'outside')

    if ref != 'outside':
        referrer = User.objects.filter(username=ref).first()
        # Optional: log this or show it
    else:
        referrer = None
    if request.method == 'POST':
        if 'enroll_now' in request.POST or 'buy_now' in request.POST:
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
    return render(request, "course/course_detail.html", locals())


def video_detail_page(request,lesson_id) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    request.session["page"] = "course"
    logged_in_profile = Profile.objects.get(user=user)
    student_profile = Student.objects.filter(profile=logged_in_profile).first() or None
    leaderboard_entry_profile = LeaderboardEntry.objects.filter(profile=logged_in_profile).first() or None
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    
    # Points Check
    required_score = lesson.required_score
    if required_score > 0 and student_profile:
        user_score = student_profile.score if student_profile else 0
        if user_score < required_score:
            messages.error(request,format_html("You need <strong class='text-primary'>{} points</strong> to view this video. Keep learning and earning points!", required_score))
            return('course_list')

    course = get_object_or_404(Course, sections__lesson__id=lesson_id)
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

def mark_lesson_complete(request, lesson_id, user_profile) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    
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
    update_streak(request,profile)

    # Handle Student Score Logic
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
    
    return redirect("video_detail_page", lesson_id=lesson_id)

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

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
        selected_lessons = request.POST.getlist("selected_lesson")
        if selected_lessons:
            selected_lessons = Lesson.objects.filter(id__in=selected_lessons)

        if article:
            article = Article.objects.filter(id=article).first()

        if section_id:
            section = get_object_or_404(Section, id=section_id)
            section.title = title
            section.order = order
            section.is_open = is_open
            section.article = article
            section.lesson.set(selected_lessons)  # Update lessons
            section.save()
            return HttpResponse(
                """<div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>Section <strong>{}</strong> updated successfully.</div>
                </div>""".format(title)
            )
        else:
            section = Section.objects.create(title=title, order=order, is_open=is_open)
            return HttpResponse(
                """<div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>Section <strong>{}</strong> created successfully.</div>
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
        # section_id = request.POST.get("section_id", 1)
        # section = get_object_or_404(Section, pk=section_id)

        if lesson_id:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            lesson.title = title
            lesson.content = description
            if "video" in request.FILES:
                lesson.video = request.FILES["video"]
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
            if "video" in request.FILES:
                lesson.video = request.FILES["video"]
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
            notes = request.POST.get("notes")
            course_notes = CourseNotes.objects.create(user=student,section_id=section_id, course_id=course_id, note_text=notes)
            # return JsonResponse({"id": course_notes.pk, "notes": course_notes.notes})
            return HttpResponse(f"{student.profile.user.first_name} left a note: {notes}")
        return HttpResponse("Invalid request.", status=400)
    except Exception as e:
        print(str(e))
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@login_required
def submit_quiz(request, quiz_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_answer = data.get('answer')

            if not user_answer:
                return JsonResponse({"error": "Answer is required"}, status=400)

            quiz = get_object_or_404(Quiz, id=quiz_id)
            profile = get_object_or_404(Profile, user=request.user)

            for qid, qdata in (quiz.questions or {}).items():
                correct_answer = qdata.get("answer") if qdata.get("type") != 'DRAG_DROP' else qdata.get("correct_mapping")
                if correct_answer and str(user_answer).strip().lower() == str(correct_answer).strip().lower():
                    quiz.completed_by_users.add(profile)
                    update_score(request,profile, 10)
                    update_streak(request,profile)
                    Activity.objects.create(
                        user=request.user,
                        activity_type="Quiz Completion",
                        description=f"Completed quiz: {quiz.title} with answer: {user_answer}",
                    )
                    return JsonResponse({"status": "completed"})

            return JsonResponse({"status": "incorrect"}, status=200)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

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