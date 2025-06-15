from django.contrib.auth.decorators import user_passes_test
from django.db.models.manager import BaseManager
# from django.db.models.query import ValuesQuerySet
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from Stock.models import Stock
from .models import FAQ, Course, Language, Quiz, Section, Tag, Lesson
from Users.models import Instructor, Profile
def course_list(request) -> HttpResponse:
    courses: BaseManager[Course] = Course.objects.all()

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
    if request.method == "POST":
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

        # ... Handle other ManyToMany fields similarly

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
    if request.method == "POST":
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

        # ... Handle other ManyToMany fields similarly

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


def search_tags(request) -> JsonResponse:
    search_term = request.GET.get("q")
    if search_term:
        tags= Tag.objects.filter(name__icontains=search_term).values("id", "name")
        return JsonResponse(list(tags), safe=False)
    return JsonResponse([], safe=False)


# ... Add similar views for searching other ManyToMany models


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


@user_passes_test(lambda u: Instructor.objects.filter(profile=u.profile).exists())
def course_delete(request, pk) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    course = get_object_or_404(Course, pk=pk)
    if (
        request.method == "POST"
    ):  # Suggested code may be subject to a license. Learn more: ~LicenseLog:3694217246.
        course.delete()
        return redirect("course_list")
    return render(request, "course/course_confirm_delete.html", {"course": course})


def course_detail(request, pk) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    course = get_object_or_404(Course, pk=pk)
    # lessons = Lesson.objects.filter(course=course)
    return render(request, "course/course_detail.html", {"course": course})


def video_detail_page(request,lesson_id) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    logged_in_profile = Profile.objects.get(user=user)
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    course = get_object_or_404(Course, sections__lesson__id=lesson_id)
    is_completed = lesson.completed_by_users.filter(pk=logged_in_profile.pk).exists()
    stock = Stock.objects.all()
    quizes = Quiz.objects.filter(lesson=lesson)
    # question_list = quizes.values_list('question', flat=True)
    questions_list = []
    for quiz in quizes:
        if quiz.questions:
            for qid, question_data in quiz.questions.items():
                question_data['quiz_id'] = quiz.pk  # optional
                questions_list.append(question_data)
    return render(request, "course/course_video_detail.html", locals())

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

    # rediect the user to the next video or lesson
    section = get_object_or_404(Section, lesson__id=lesson_id)

    next_lesson = section.lesson.filter(id__gt=lesson_id).exclude(completed_by_users=profile,id=lesson_id).first()
    if next_lesson:
        lesson_id = next_lesson.id
        return JsonResponse({"next_lesson_id": lesson_id})
    
    return redirect("video_detail_page", lesson_id=lesson_id)

def create_tag(request) -> HttpResponse:
    if request.method == "POST":
        name = request.POST.get("name")
        tag = Tag.objects.create(name=name)
        return JsonResponse({"id": tag.pk, "name": tag.name})
    return HttpResponse("Invalid request.", status=400)


def create_section(request) -> HttpResponse:
    if request.method == "POST":
        # course_id = request.POST.get("course_id")
        title = request.POST.get("title")
        order = request.POST.get("order")
        is_open = request.POST.get("is_open", False) == "on"
        # course = get_object_or_404(Course, pk=course_id)
        section = Section.objects.create(title=title, order=order, is_open=is_open)
        return JsonResponse({"id": section.pk, "title": section.title})
    return HttpResponse("Invalid request.", status=400)


def create_lesson(request) -> HttpResponse:
    if request.method == "POST":
        # section_id = request.POST.get("section_id")
        title = request.POST.get("title")
        description = request.POST.get("description")
        order = request.POST.get("order")
        section = get_object_or_404(Section, pk=1)
        lesson = Lesson.objects.create(
             title=title, description=description, order=order
        )
        return JsonResponse({"id": lesson.pk, "title": lesson.title})
    return HttpResponse("Invalid request.", status=400)


def create_faq(request) -> HttpResponse:
    if request.method == "POST":
        question = request.POST.get("question")
        answer = request.POST.get("answer")
        faq = FAQ.objects.create(question=question, answer=answer)
        return JsonResponse({"id": faq.pk, "question": faq.question})
    return HttpResponse("Invalid request.", status=400)
