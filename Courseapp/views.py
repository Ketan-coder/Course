from django.contrib.auth.decorators import user_passes_test
from django.db.models.manager import BaseManager
import json
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from Stock.models import Stock
from .models import FAQ, Course, Language, Quiz, Section, Tag, Lesson, CourseNotes
from Users.models import Instructor, Profile, Student
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.html import format_html
from django.urls import reverse

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
    request.session["page"] = "course"
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


@user_passes_test(lambda u: Instructor.objects.filter(profile=u.profile).exists())
def course_delete(request, pk) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    request.session["page"] = "course"
    course = get_object_or_404(Course, pk=pk)
    if (
        request.method == "POST"
    ):  # Suggested code may be subject to a license. Learn more: ~LicenseLog:3694217246.
        course.delete()
        return redirect("course_list")
    return render(request, "course/course_confirm_delete.html", {"course": course})


def course_detail(request, pk) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    course = get_object_or_404(Course, pk=pk)
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    request.session["page"] = "course"
    logged_in_profile = Profile.objects.get(user=user)
    return render(request, "course/course_detail.html", {"course": course})


def video_detail_page(request,lesson_id) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    request.session["page"] = "course"
    logged_in_profile = Profile.objects.get(user=user)
    student_profile = Student.objects.filter(profile=logged_in_profile).first() or None
    lesson = get_object_or_404(Lesson, pk=lesson_id)
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
