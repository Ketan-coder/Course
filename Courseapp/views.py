from django.contrib.auth.decorators import user_passes_test
from django.db.models.manager import BaseManager
import json
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from utils.models import Activity
from Stock.models import Stock
from .models import FAQ, Course, Language, Quiz, Section, Tag, Lesson, CourseNotes, Article, QuizSubmission
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
from django.db.models import Avg
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from difflib import get_close_matches
import re
# def course_list(request) -> HttpResponse:
#     courses: BaseManager[Course] = Course.objects.all()
#     request.session["page"] = "course"
#     if request.user.is_authenticated:
#         profile = Profile.objects.filter(user=request.user).first()
#         student_profile = Student.objects.filter(profile=profile).first() or None
#         instructor_profile = Instructor.objects.filter(profile=profile).first() or None
#         if student_profile:
#             request.session['streak'] = student_profile.streak
#             request.session['score'] = student_profile.score
#             request.session['current_user_type'] = 'student'
#         elif instructor_profile:
#             request.session['current_user_type'] = 'instructor'

#     if request.method == "POST" and "search_term" in request.POST:
#         search_term = request.POST["search_term"]
#         courses = courses.filter(
#             title__icontains=search_term, language__name__icontains=search_term
#         ) # Suggested code may be subject to a license. Learn more: ~LicenseLog:1606362085.
#     if "course_level" in request.GET:
#         filter_by_level = request.GET["course_level"]
#         if filter_by_level != "any":
#             courses = courses.filter(course_level=filter_by_level)

#     if "course_type" in request.GET:
#         filter_by_type = request.GET["course_type"]
#         if filter_by_type == "any":
#             courses = Course.objects.all()
#         else:
#             courses = courses.filter(course_type=filter_by_type)
#     return render(request, "course/course_list.html", locals())

from collections import defaultdict

def course_list(request, category='') -> HttpResponse:
    category_object = ''
    if category:
        try:
            category_object = Tag.objects.get(name=category)
            courses = Course.objects.filter(tags=category_object)
        except Tag.DoesNotExist:
            courses = Course.objects.none()
        except:
            courses = Course.objects.all()
    else:
        courses = Course.objects.all()
    categories = Tag.objects.all()
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

    if "course_level" in request.GET:
        filter_by_level = request.GET["course_level"]
        if filter_by_level != "any":
            courses = courses.filter(course_level=filter_by_level)

    if "course_type" in request.GET:
        filter_by_type = request.GET["course_type"]
        if filter_by_type != "any":
            courses = courses.filter(course_type=filter_by_type)

    #  Group courses by tag
    grouped_courses = defaultdict(list)
    seen_courses = set()

    # for course in courses:
    #     tags = course.tags.values_list('name', flat=True)
    #     for tag in tags:
    #         if course.id not in seen_courses:
    #             grouped_courses[tag].append(course)
    #             seen_courses.add(course.id)
    #             break

    for course in courses:
        tags = course.tags.all() # Get full Tag objects instead of just names
        for tag in tags:
            if course.id not in seen_courses:
                # Use the tag object as the key to include icon information
                grouped_courses[tag].append(course)
                seen_courses.add(course.id)
                break

    grouped_courses = dict(grouped_courses)

    print(grouped_courses)
    print(categories)

    return render(request, "course/course_list.html", {
        "grouped_courses": grouped_courses, 
        'categories' : categories, 
        'category' : category if category else '',
        'category_object' : category_object if category_object else ''
    })


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
    course: Course = get_object_or_404(Course, pk=pk)
    instructors: BaseManager[Instructor] = Instructor.objects.all()
    logined_profile = Profile.objects.get(user=request.user)
    logined_instructor = Instructor.objects.filter(profile=logined_profile).first()
    lessons = Lesson.objects.all() 
    request.session["page"] = "course"
    if request.method == "POST":
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
        tags= Tag.objects.filter(name__icontains=search_term).values("id", "name", "icon_image", "extra_fields")
        return JsonResponse(list(tags), safe=False)
    return JsonResponse([], safe=False)


def search_sections(request) -> JsonResponse:
    try:
        search_term = request.GET.get("q")
        profile = Profile.objects.filter(user=request.user).first()
        instructor_profile = Instructor.objects.filter(profile=profile).first()
        used_sections = Course.objects.filter(sections__isnull=False, instructor_id=instructor_profile.id).values_list('sections__id', flat=True).distinct()
        if search_term:
            sections= Section.objects.filter(title__icontains=search_term, instructor_id=instructor_profile.id).exclude(id__in=used_sections).values(
                "id", "title"
            )
            return JsonResponse(list(sections), safe=False)
        return JsonResponse([], safe=False)
    except Exception as e:
        print(f"Error searching sections: {e}")
        return JsonResponse([], safe=False)

def search_lessons(request) -> JsonResponse:
    search_term = request.GET.get("q")
    instructor_profile = Instructor.objects.filter(profile=request.user.profile).first()
    used_lessons = Course.objects.filter(sections__isnull=False, sections__lesson__isnull=False, instructor_id=instructor_profile.id).values_list('sections__lesson__id', flat=True).distinct()
    if search_term:
        lessons= Lesson.objects.filter(title__icontains=search_term, instructor_id=instructor_profile.id).exclude(id__in=used_lessons).values(
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
    instructor_profile = Instructor.objects.filter(profile=request.user.profile).first()
    used_articles = Section.objects.filter(instructor_id=instructor_profile.id).values_list('article__id', flat=True).distinct()
    if search_term:
        articles= Article.objects.filter(title__icontains=search_term, author_id=instructor_profile.id).exclude(id__in=used_articles).values(
            "id", "title"
        )
        return JsonResponse(list(articles), safe=False)
    return JsonResponse([], safe=False)

# def search_courses_htmx(request):
#     try:
#         query = request.GET.get("q", "")
#         courses = Course.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(language__name__icontains=query) | Q(tags__name__icontains=query) | Q(sections__title__icontains=query) | Q(prerequisites__icontains=query)).distinct()[:10]
#         html = render_to_string("components/_search_results.html", {"courses": courses})
#         return HttpResponse(html)
#     except Exception as e:
#         return HttpResponse(f"Error: {str(e)}", status=500)

def search_courses_htmx(request):
    try:
        query = request.GET.get("q", "").strip().lower()
        attribute_matches = Course.objects.none()
        normal_matches = Course.objects.none()
        suggestion_text = None

        if query:
            filters = Q()

            # --- Keyword-based attributes ---
            if "free" in query:
                filters |= Q(course_type="free")
            if "paid" in query:
                filters |= Q(course_type="paid")
            if "beginner" in query:
                filters |= Q(course_level="beginner")
            if "intermediate" in query:
                filters |= Q(course_level="intermediate")
            if "advanced" in query:
                filters |= Q(course_level="advanced")
            if "all level" in query:
                filters |= Q(course_level="all")
            if "classroom" in query:
                filters |= Q(is_class_room_course=True)
            if "open" in query:
                filters |= Q(is_open_to_all=True)
            if "discount" in query:
                filters |= Q(discount_price__lt=F('price'))

            # --- Price filter: e.g., "under 50", "less than 100" ---
            price_match = re.search(r"(under|less than)\s*\$?(\d+)", query)
            if price_match:
                max_price = float(price_match.group(2))
                filters |= Q(price__lte=max_price)

            # --- Price filter: e.g., "over 50", "greater than 100, above 200" ---
            price_match = re.search(r"(over|greater than|above)\s*\$?(\d+)", query)
            if price_match:
                max_price = float(price_match.group(2))
                filters |= Q(price__gte=max_price)

            # --- Star ratings: "4 star", "5 star rated" ---
            star_match = re.search(r"(\d)\s*star", query)
            if star_match:
                star_value = int(star_match.group(1))
                filters |= Q(reviews__rating=star_value)

            # --- Points requirement: "under 500 points" ---
            points_match = re.search(r"(under|less than)\s*(\d+)\s*points?", query)
            if points_match:
                max_points = int(points_match.group(2))
                filters |= Q(required_points__lte=max_points)

            # If we found attribute filters, get distinct results
            if filters:
                attribute_matches = Course.objects.filter(filters).annotate(
                    avg_rating=Avg("reviews__rating")
                ).distinct()

            # --- Normal keyword search ---
            normal_matches = Course.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(language__name__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(sections__title__icontains=query) |
                Q(prerequisites__icontains=query)
            ).annotate(
                avg_rating=Avg("reviews__rating")
            ).distinct()

            # Remove duplicates so attribute results don't repeat
            if attribute_matches.exists():
                normal_matches = normal_matches.exclude(id__in=attribute_matches.values_list("id", flat=True))

            # --- Suggestions for typos ---
            if not attribute_matches.exists() and not normal_matches.exists():
                all_titles = list(Course.objects.values_list("title", flat=True))
                close_matches = get_close_matches(query, all_titles, n=5, cutoff=0.6)
                if close_matches:
                    suggestion_text = f"You might be looking for: {', '.join(close_matches)}"

        # Merge results with attribute matches on top
        courses = list(attribute_matches) + list(normal_matches)

        html = render_to_string("components/_search_results.html", {
            "courses": courses[:10],  # limit top 10
            "suggestion": suggestion_text
        })
        return HttpResponse(html)

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
    
def course_like_htmx(request, course_id):
    if request.method == "GET":
        course = get_object_or_404(Course, pk=course_id)
        if request.user.is_authenticated:
            if request.user.profile in course.bookmarked_by_users.all():
                course.bookmarked_by_users.remove(request.user.profile)
            else:
                course.bookmarked_by_users.add(request.user.profile)
            return JsonResponse({"success": True})
        return JsonResponse({"success": False})

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
    student_enrolled_count = course.is_bought_by_users.count()
    reviews_count = course.reviews.count()
    avg_reviews =  course.reviews.all().aggregate(Avg('rating'))['rating__avg'] or 0
    ref = request.GET.get('ref', 'outside')

    if course:
        instructor_related_courses = Course.objects.filter(instructor=course.instructor, is_published=True, is_deleted=False)
        course_list = Course.objects.all()
    else:
        instructor_related_courses = Course.objects.none()
        course_list = Course.objects.all()

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
                    # student_profile.score += bonus_points
                    # student_profile.save()
                    update_score(request,logged_in_profile, bonus_points)
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
                return render(request, "course/course_detail_page.html", {"course": course, "error": "You must have a student profile to enroll."})
        elif 'continue_now' in request.POST:
            # Get the first uncompleted lesson in the course, respecting section order
            first_uncompleted_lesson = None
            for section in course.sections.filter(lesson__isnull=False).order_by('order'):
                # Filter lessons in this section that the user hasn't completed
                uncompleted_lesson = section.lesson.exclude(completed_by_users=logged_in_profile).order_by('order').first()
                if uncompleted_lesson:
                    first_uncompleted_lesson = uncompleted_lesson
                    break
            
            if first_uncompleted_lesson:
                return redirect("video_detail_page", lesson_id=first_uncompleted_lesson.id)
            else:
                messages.error(request, "All lessons are completed or no lessons are available in this course.")
                return redirect("course_detail", pk=pk)
    return render(request, "course/course_detail_page.html", locals())


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
    # section = get_object_or_404(Section, id__in=to_search_sections)
    section = Section.objects.filter(id__in=to_search_sections).first()
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
        print(request.POST)
        section_id = request.POST.get("section_id", None)
        order = request.POST.get("order", 0)
        is_open = request.POST.get("is_open", False) == "on"
        article = request.POST.get("article", "")
        content = request.POST.get("content", "")
        is_generate_content_using_ai = request.POST.get("is_generate_quiz", False) == "on"
        prompt = request.POST.get("prompt", "")
        course_id = request.POST.get("course_id")
        profile = request.user.profile
        instructor = Instructor.objects.filter(profile=profile).first()

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

            section.instructor_id = instructor.id
            
            section.save(prompt=prompt, is_generate_content_using_ai= True if 'is_generate_quiz' in request.POST else False)  # Save prompt if needed
            # if course_id:
            #     course = get_object_or_404(Course, id=course_id)
            #     course.sections.add(section)
            #     course.save()
            return HttpResponse(
                """<div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>Section <strong>{}</strong> updated successfully.</div>
                </div>""".format(title)
            )
        else:
            section = Section.objects.create(title=title, order=order, is_open=is_open, instructor=instructor)
            if content:
                section.content = content
            if article:
                section.article = article
            if selected_lessons:
                section.lesson.set(selected_lessons)  # Update lessons
            section.save(prompt=prompt, is_generate_content_using_ai=True if 'is_generate_quiz' in request.POST else False)
            if course_id:
                course = get_object_or_404(Course, id=course_id)
                course.sections.add(section)
                course.save()
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
        lesson_id = request.POST.get("lesson_id", None)
        description = request.POST.get("description", "")
        order = request.POST.get("order", 0)
        required_score = request.POST.get("required-score", 0)
        video_url = request.POST.get("video_url", "")
        video_path = request.POST.get("video_path", "")
        profile = request.user.profile
        instructor = Instructor.objects.filter(profile=profile).first()
        section_id = request.POST.get("section_id", 1)
        section = get_object_or_404(Section, pk=section_id)

        if lesson_id:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            lesson.title = title
            lesson.content = description
            if "thumbnail" in request.FILES:
                lesson.thumbnail = request.FILES["thumbnail"]
            if "video" in request.FILES:
                lesson.video = request.FILES["video"]
            else:
                if video_path:
                    lesson.video = video_path
                    lesson.video_url = ""  # Clear URL if uploading file
                elif video_url:
                    lesson.video_url = video_url
            lesson.order = order
            lesson.required_score = required_score
            lesson.instructor = instructor
            lesson.save()
            # if section:
            #     section.lesson.add(lesson)
            #     section.save()
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
                instructor=instructor
            )
            if "thumbnail" in request.FILES:
                lesson.thumbnail = request.FILES["thumbnail"]
            if "video" in request.FILES:
                lesson.video = request.FILES["video"]
            else:
                lesson.video_url = video_url
            lesson.save()
            if section:
                section.lesson.add(lesson)
                section.save()
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
    
def create_article_ajax(request) -> HttpResponse:
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
        article_id = request.POST.get("article_id")
        content = request.POST.get("content", "")
        section_id = request.POST.get("section_id")
        if section_id:
            section = get_object_or_404(Section, id=section_id)
        else:
            section = None
        author = Instructor.objects.filter(profile=request.user.profile).first()

        if article_id:
            article = get_object_or_404(Article, id=article_id)
            article.title = title
            article.content = content
            article.author = author
            article.save()
            if section:
                section.article = article
                section.save()
            return HttpResponse(
                """<div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>Article <strong>{}</strong> updated successfully.</div>
                </div>""".format(title)
            )
        else:
            article = Article.objects.create(title=title, content=content, author=author)
            if section:
                section.article = article
                section.save()
            return HttpResponse(
                """<div class="alert alert-success border-0 rounded-0 d-flex align-items-center" role="alert">
                    <i class="fa-light fa-check-circle text-success-emphasis me-2"></i>
                    <div>Article <strong>{}</strong> created successfully.</div>
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
    
def create_quiz_ajax(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        # Extract basic quiz fields
        quiz_id = request.POST.get("quiz_id")
        title = request.POST.get("title", "")
        course_id = request.POST.get("course_id")
        section_id = request.POST.get("section_id")
        lesson_id = request.POST.get("lesson_id")
        questions_json = request.POST.get("questions_json", "[]")

        # Parse the JSON string into a list of dicts
        questions = json.loads(questions_json)

        # Build quiz.question JSON-like object with keys: 1, 2, 3...
        formatted_questions = {}
        for index, q in enumerate(questions, start=1):
            raw_options = q.get("options", [])
            print(f"Raw options: {raw_options}")
            
            # Generate option objects with ids: a, b, c, ...
            option_objs = [
                {"id": chr(97 + i), "text": option}
                for i, option in enumerate(raw_options)
            ] if raw_options else []

            print(f"Formatted options: {option_objs}")

            formatted_questions[str(index)] = {
                "id": str(index),
                "question": q["question"],
                "type": q["type"],
                "options": option_objs,
                "answer": ",".join(q["answer"]) if isinstance(q["answer"], list) else q["answer"],
                "is_completed": False,
                "score_on_completion": q.get("score_on_completion", 10)
            }


        if quiz_id:
            quiz = get_object_or_404(Quiz, id=quiz_id)
            quiz.title = title
            quiz.questions = formatted_questions
        else:
            quiz = Quiz.objects.create(title=title, questions=formatted_questions)

        # Optional: Link related objects
        if course_id:
            quiz.course = get_object_or_404(Course, id=course_id)
        if section_id:
            quiz.section = get_object_or_404(Section, id=section_id)
        if lesson_id:
            quiz.lesson = get_object_or_404(Lesson, id=lesson_id)

        quiz.save()
        return JsonResponse({'success': True, 'message': 'Quiz saved successfully.'}, status=200)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
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
    
def fetch_lesson_api(request, lesson_id):
    try:
        lesson = get_object_or_404(Lesson, id=lesson_id)
        data = {
            "id": lesson.id,
            "title": lesson.title,
            "content": lesson.content,
            "video_url": lesson.video_url,
            "video_path": lesson.video.url if lesson.video else None,
            "thumbnail": lesson.thumbnail.url if lesson.thumbnail else None,
            "required_score": lesson.required_score,
            "order": lesson.order,
        }
        return JsonResponse(data)
    except Lesson.DoesNotExist:
        return JsonResponse({"error": "Lesson not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def get_section_details(request, section_id):
    try:
        section = get_object_or_404(Section, id=section_id)
        data = {
            "id": section.id,
            "title": section.title,
            "content": section.content,
            "is_open": section.is_open,
            "order": section.order,
            "article": section.article.title if section.article else None,
            "lessons": list(section.lesson.values("id", "title", "content", "video_url", "thumbnail", "required_score", "order")),
        }
        return JsonResponse(data)
    except Section.DoesNotExist:
        return JsonResponse({"error": "Section not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def get_quiz_details(request, quiz_id):
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        data = {
            "id": quiz.id,
            "title": quiz.title,
            "questions": quiz.questions,
            "course_id": quiz.course.id if quiz.course else None,
            "section_id": quiz.section.id if quiz.section else None,
            "lesson_id": quiz.lesson.id if quiz.lesson else None,
        }
        return JsonResponse(data)
    except Quiz.DoesNotExist:
        return JsonResponse({"error": "Quiz not found"}, status=404)
    except Exception as e:
        print(str(e))
        return JsonResponse({"error": str(e)}, status=500)
    
def get_article_details(request, article_id):
    try:
        article = get_object_or_404(Article, id=article_id)
        data = {
            "id": article.id,
            "title": article.title,
            "content": article.content,
            "author": article.author.profile.user.username if article.author else None,
            "created_at": article.created_at.isoformat(),
            "updated_at": article.updated_at.isoformat(),
        }
        return JsonResponse(data)
    except Article.DoesNotExist:
        return JsonResponse({"error": "Article not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def update_section_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body)
        section_id = data.get("section_id")
        new_order = data.get("new_order")

        if not section_id or new_order is None:
            return JsonResponse({"error": "Section ID and new order are required."}, status=400)

        section = get_object_or_404(Section, id=section_id, is_deleted=False)
        section.order = int(new_order)
        section.save()

        return JsonResponse({"message": "Section order updated successfully."})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def update_lesson_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body)
        lesson_id = data.get("lesson_id")
        new_order = data.get("new_order")
        section_id = data.get("section_id")

        if not lesson_id or new_order is None or not section_id:
            return JsonResponse({"error": "Lesson ID, section ID, and new order are required."}, status=400)

        lesson = get_object_or_404(Lesson, id=lesson_id, is_deleted=False)
        target_section = get_object_or_404(Section, id=section_id, is_deleted=False)

        # Update lesson's order
        lesson.order = int(new_order)

        # Update ManyToMany relationship: add to target section, remove from others
        lesson.sections.clear()  # Remove from all current sections
        lesson.sections.add(target_section)  # Add to the target section

        # Update extra_fields with last_updated timestamp
        lesson.extra_fields['last_updated'] = str(lesson.updated_at)
        lesson.save()

        # Optionally, normalize order for other lessons in the target section
        for index, l in enumerate(target_section.lesson.filter(is_deleted=False).order_by('order'), start=0):
            if l.id != lesson.id:  # Skip the lesson we just moved
                l.order = index + (1 if index >= new_order else 0)
                l.extra_fields['last_updated'] = str(l.updated_at)
                l.save()

        return JsonResponse({"message": "Lesson order and section updated successfully."})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
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
            
            if not request.user.is_authenticated:
                return JsonResponse({"error": "User is not authenticated"}, status=401)
            
            if Instructor.objects.filter(profile=request.user.profile).exists():
                return JsonResponse({"error": "Instructors are not allowed to submit quizzes"}, status=403)
            

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
                

                if isinstance(correct_answer, str) and ',' in correct_answer:
                    correct_set = set(map(str.strip, correct_answer.lower().split(',')))
                    user_set = set(map(str.strip, [x.lower() for x in user_answer])) if isinstance(user_answer, list) else set(map(str.strip, user_answer.lower().split(',')))
                    if correct_set == user_set:
                        if qdata.get("type") == quiz_type:
                            qdata["is_completed"] = True
                            quiz.questions[qid] = qdata
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
                        qdata["is_completed"] = True
                        quiz.questions[qid] = qdata
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

        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated"}, status=401)
        
        if Instructor.objects.filter(profile=request.user.profile).exists():
            return JsonResponse({"error": "Instructors are not allowed to submit drag-and-drop quizzes"}, status=403)

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
        lesson.instructor = instructor

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


def delete_lesson_api(request, lesson_id):
    """
    API endpoint to delete a lesson.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must be logged in to delete a lesson."}, status=403)
    if lesson_id is None:
        return JsonResponse({"error": "Lesson ID is required."}, status=400)
    profile = request.user.profile
    author = Instructor.objects.filter(profile=profile).first()
    if not author:
        return JsonResponse({"error": "You must be an author to delete a lesson."}, status=403)
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not lesson:
        return JsonResponse({"error": "Lesson not found."}, status=404)
    if lesson.instructor_id != author.id:
        return JsonResponse({"error": "You must be the author of the lesson to delete it."}, status=403)
    
    lesson = get_object_or_404(Lesson, id=lesson_id)
    # lesson.is_deleted = True
    # lesson.save()
    lesson.delete()
    return JsonResponse({"success": True})

def delete_article_api(request, article_id):
    """
    API endpoint to delete an article.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must be logged in to delete an article."}, status=403)
    if article_id is None:
        return JsonResponse({"error": "Article ID is required."}, status=400)
    profile = request.user.profile
    author = Instructor.objects.filter(profile=profile).first()
    if not author:
        return JsonResponse({"error": "You must be an author to delete an article."}, status=403)
    article = get_object_or_404(Article, id=article_id)
    if not article:
        return JsonResponse({"error": "Article not found."}, status=404)
    if article.author_id != author.id:
        return JsonResponse({"error": "You must be the author of the article to delete it."}, status=403)
    
    article = get_object_or_404(Article, id=article_id)
    # article.is_deleted = True
    # article.save()
    article.delete()
    return JsonResponse({"success": True})

def delete_section_api(request, section_id):
    """
    API endpoint to delete a section.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must be logged in to delete a section."}, status=403)
    if section_id is None:
        return JsonResponse({"error": "Section ID is required."}, status=400)
    profile = request.user.profile
    instructor = Instructor.objects.filter(profile=profile).first()
    if not instructor:
        return JsonResponse({"error": "You must be an instructor to delete a section."}, status=403)
    section = get_object_or_404(Section, id=section_id)
    if not section:
        return JsonResponse({"error": "Section not found."}, status=404)
    if section.instructor_id != instructor.id:
        return JsonResponse({"error": "You must be the instructor of the section to delete it."}, status=403)
    
    # section.is_deleted = True
    # section.save()
    section.delete()
    return JsonResponse({"success": True})

def delete_course_api(request, course_id):
    """
    API endpoint to delete a course.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must be logged in to delete a course."}, status=403)
    if course_id is None:
        return JsonResponse({"error": "Course ID is required."}, status=400)
    profile = request.user.profile
    instructor = Instructor.objects.filter(profile=profile).first()
    if not instructor:
        return JsonResponse({"error": "You must be an instructor to delete a course."}, status=403)
    if course.instructor_id != instructor.id:
        return JsonResponse({"error": "You must be the instructor of the course to delete it."}, status=403)
    course = get_object_or_404(Course, id=course_id)
    course.is_deleted = True
    course.save()
    # course.delete()
    return JsonResponse({"success": True})

def delete_quiz_api(request, quiz_id):
    """
    API endpoint to delete a quiz.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must be logged in to delete a quiz."}, status=403)
    if quiz_id is None:
        return JsonResponse({"error": "Quiz ID is required."}, status=400)
    profile = request.user.profile
    instructor = Instructor.objects.filter(profile=profile).first()
    if not instructor:
        return JsonResponse({"error": "You must be an instructor to delete a quiz."}, status=403)
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not quiz:
        return JsonResponse({"error": "Quiz not found."}, status=404)
    
    # quiz.is_deleted = True
    # quiz.save()
    quiz.delete()
    return JsonResponse({"success": True})

def delete_article_api(request, article_id):
    """
    API endpoint to delete an article.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must be logged in to delete an article."}, status=403)
    if article_id is None:
        return JsonResponse({"error": "Article ID is required."}, status=400)
    profile = request.user.profile
    instructor = Instructor.objects.filter(profile=profile).first()
    if not instructor:
        return JsonResponse({"error": "You must be an instructor to delete an article."}, status=403)
    article = get_object_or_404(Article, id=article_id)
    if not article:
        return JsonResponse({"error": "Article not found."}, status=404)
    if article.author_id != instructor.id:
        return JsonResponse({"error": "You must be the author of the article to delete it."}, status=403)
    
    # article.is_deleted = True
    # article.save()
    article.delete()
    return JsonResponse({"success": True})



def course_create_step_one(request, course_id=None) -> HttpResponse:
    """
    Handles the first step of course creation or editing.
    If course_id is provided, it fetches the course for editing.
    If not, it initializes a new course creation form.
    """
    request.session["page"] = "course"
    step = "1"
    step_one_done = False
    if not request.user.is_authenticated:
        return redirect("login")
    user = request.user
    instructor = Instructor.objects.filter(profile__user=user).first()
    if not instructor:
        return HttpResponse("You must be an instructor to create a course.", status=403)
    languages = Language.objects.all()
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        if course.instructor_id != instructor.id:
            return HttpResponse("You are not authorized to edit this course.", status=403)
    else:
        course = None

    if request.method == "POST":
        print("Creating or updating course..." + str(request.POST))
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        course_type = request.POST.get("course_type", "").strip()
        course_level = request.POST.get("course_level", "").strip()
        price = request.POST.get("price", "").strip()
        discount_price = request.POST.get("discount_price", "").strip()
        if not course_level or course_level.upper() not in ["BEGINNER", "INTERMEDIATE", "ADVANCED", "ALL"]:
            return HttpResponse("Invalid difficulty level.", status=400)
        if not course_type:
            return HttpResponse("Course type is required.", status=400)
        if course_type.upper() not in ["FREE", "PAID"]:
            return HttpResponse("Invalid course type.", status=400)
        if course_type.upper() == "PAID":
            price = request.POST.get("price", "").strip()
            if not price or not price.isdigit():
                return HttpResponse("Price must be a valid number.", status=400)
            price = int(price)
        language_id = request.POST.get("language")
        if not title or not description or not language_id:
            return HttpResponse("Name, description, and language are required.", status=400)
        
        if request.FILES.get("thumbnail"):
            thumbnail = request.FILES["thumbnail"]
        if request.FILES.get("intro_video"):
            video = request.FILES["intro_video"]

        try:
            language = get_object_or_404(Language, id=language_id)
            if course_id:
                course.title = title
                course.description = description
                course.language = language
                course.instructor = instructor
                course.course_type = course_type
                course.course_level = course_level
                course.price = price
                course.discount_price = discount_price
                if thumbnail:
                    course.thumbnail = thumbnail
                if video:
                    course.intro_video = video
                course.save()
                # Log activity
                Activity.objects.create(
                    user=user,
                    activity_type="Course Update",
                    description=f"Updated course: {course.title}"
                )
                step_one_done = True
            else:
                course = Course.objects.create(
                    title=title,
                    description=description,
                    instructor=instructor,
                    language=language,
                    course_type=course_type,
                    course_level=course_level,
                    price=price,
                    discount_price=discount_price
                )
                if thumbnail:
                    course.thumbnail = thumbnail
                if video:
                    course.intro_video = video
                course.save()
                # Log activity
                # Activity.objects.create(
                #     user=user,
                #     activity_type="Course Creation",
                #     description=f"Created course: {course.title}"
                # )
                step_one_done = True
            if step_one_done:
                request.session['step_one_done'] = True 
            return redirect("course_create_step_two", course_id=course.id)
        except Exception as e:
            return HttpResponse(f"Error creating course: {str(e)}", status=500)
    return render(request, "course/creation/step_1.html", locals())


def course_create_step_two(request, course_id=None) -> HttpResponse:
    """
    Handles the second step of course creation or editing.
    If course_id is provided, it fetches the course for editing.
    If not, it initializes a new course creation form.
    """
    request.session["page"] = "course"
    step = "2"
    step_two_done = False
    if not request.user.is_authenticated:
        return redirect("login")
    user = request.user
    instructor = Instructor.objects.filter(profile__user=user).first()
    # default_objectives = [
    #     "Understand the basic concepts of the course",
    #     "Apply learned skills in practical scenarios",
    #     "Analyze and evaluate course materials",
    #     "Create projects or assignments based on course content",
    #     "Collaborate with peers on course-related tasks",
    #     "Demonstrate mastery of key concepts through assessments",
    #     "Reflect on learning outcomes and areas for improvement"
    # ]
    if not instructor:
        return HttpResponse("You must be an instructor to create a course.", status=403)
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        if course.instructor_id != instructor.id:
            return HttpResponse("You are not authorized to edit this course.", status=403)
    else:
        course = None
    if request.method == "POST":
        print("Creating or updating course sections..." + str(request.POST))
        prerequisites = request.POST.get("prerequisites", "").strip()
        circulam = request.POST.get("circulam", "").strip()
        objectives_json = request.POST.get('learning_objectives', '[]')
        if not circulam and not prerequisites:
            return HttpResponse("Prerequisites or circulam is required.", status=400)
        
        try:
            if course_id:
                course = get_object_or_404(Course, id=course_id)
                course.prerequisites = prerequisites
                course.circulam = circulam
                course.save()
                
                try:
                    objectives = json.loads(objectives_json)
                    if not isinstance(objectives, list) or len(objectives) > 8:
                        messages.error(request, "Invalid learning objectives format or too many objectives.")
                        return render(request, 'course/step_2.html', {'course': course, 'step': 2})
                    course.learning_objectives = objectives
                    course.save()
                    step_two_done = True
                    request.session['step_two_done'] = step_two_done
                    return redirect('course_create_step_three', course_id=course.id)
                except json.JSONDecodeError:
                    request.session['step_two_done'] = step_two_done
                    messages.error(request, "Invalid learning objectives format.")
                    return render(request, 'course/step_2.html', {'course': course, 'step': 2})
                
            else:
                return HttpResponse("Course ID is required to create a section.", status=400)
            return redirect("course_create_step_three", course_id=course.id)
        except Exception as e:
            return HttpResponse(f"Error creating section: {str(e)}", status=500)
    return render(request, "course/creation/step_2.html", locals())


def course_create_step_three(request, course_id=None) -> HttpResponse:
    """
    Handles the third step of course creation or editing.
    If course_id is provided, it fetches the course for editing.
    If not, it initializes a new course creation form.
    """
    request.session["page"] = "course"
    step = "3"
    step_three_done = False
    if not request.user.is_authenticated:
        return redirect("login")
    user = request.user
    instructor = Instructor.objects.filter(profile__user=user).first()
    if not instructor:
        return HttpResponse("You must be an instructor to create a course.", status=403)
    if course_id and course_id != "":
        course = get_object_or_404(Course, id=course_id)
        if course.instructor_id != instructor.id:
            return HttpResponse("You are not authorized to edit this course.", status=403)
    else:
        course = None
    if request.method == "POST":
        print("Creating or updating course sections..." + str(request.POST))
        try:
            if course_id and course_id != "":
                course = get_object_or_404(Course, id=course_id)
                course.save()
                # Log activity
                # Activity.objects.create(
                #     user=user,
                #     activity_type="Course Update",
                #     description=f"Updated course sections for: {course.title}"
                # )
                step_three_done = True
                request.session['step_three_done'] = step_three_done
                return redirect("course_create_step_four", course_id=course.id)
            else:
                return HttpResponse("Course ID is required to create a section.", status=400)
        except Exception as e:
            return HttpResponse(f"Error creating section: {str(e)}", status=500)
    return render(request, "course/creation/step_3.html", locals())


def course_create_step_four(request, course_id=None) -> HttpResponse:
    """
    Handles the fourth step of course creation or editing.
    If course_id is provided, it fetches the course for editing.
    If not, it initializes a new course creation form.
    """
    request.session["page"] = "course"
    step = "4"
    step_four_done = False
    if not request.user.is_authenticated:
        return redirect("login")
    user = request.user
    instructor = Instructor.objects.filter(profile__user=user).first()
    section_ids = Course.objects.filter(id=course_id).values_list('sections__id', flat=True) if course_id else []
    quizzes = Quiz.objects.filter(section__id__in=section_ids) if course_id else Quiz.objects.none()
    article_ids = Section.objects.filter(id__in=section_ids).values_list('article__id', flat=True) if course_id else []
    articles = Article.objects.filter(id__in=article_ids) if course_id else Article.objects.none()
    if not instructor:
        return HttpResponse("You must be an instructor to create a course.", status=403)
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        if course.instructor_id != instructor.id:
            return HttpResponse("You are not authorized to edit this course.", status=403)
    else:
        course = None
    if request.method == "POST":
        print("Creating or updating course sections..." + str(request.POST))
        try:
            if course_id:
                course = get_object_or_404(Course, id=course_id)
                course.save()
                # Log activity
                # Activity.objects.create(
                #     user=user,
                #     activity_type="Course Update",
                #     description=f"Updated course sections for: {course.title}"
                # )
                step_four_done = True
                request.session['step_four_done'] = step_four_done
                return redirect("course_create_step_five", course_id=course.id)
            else:
                return HttpResponse("Course ID is required to create a section.", status=400)
        except Exception as e:
            return HttpResponse(f"Error creating section: {str(e)}", status=500)
    return render(request, "course/creation/step_4.html", locals())

def course_create_step_five(request, course_id=None) -> HttpResponse:
    """
    Handles the fifth step of course creation or editing.
    If course_id is provided, it fetches the course for editing.
    If not, it initializes a new course creation form.
    """
    request.session["page"] = "course"
    step = "5"
    if not request.user.is_authenticated:
        return redirect("login")
    user = request.user
    instructor = Instructor.objects.filter(profile__user=user).first()
    if not instructor:
        return HttpResponse("You must be an instructor to create a course.", status=403)
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        if course.instructor_id != instructor.id:
            return HttpResponse("You are not authorized to edit this course.", status=403)
    else:
        course = None
    if request.method == "POST":
        try:
            # Handle ManyToMany fields (example for tags)
            selected_tag_ids = request.POST.getlist("selected_tags")

            # handle faq selection
            selected_faq_ids = request.POST.getlist("selected_faqs")
            create_qr_code = 'create_qr_code' in request.POST
            
            if course_id:
                course = get_object_or_404(Course, id=course_id)
                if selected_tag_ids:
                    tags = Tag.objects.filter(id__in=selected_tag_ids)
                    course.tags.set(tags)
                if selected_faq_ids:
                    faqs = FAQ.objects.filter(id__in=selected_faq_ids)
                    course.faqs.set(faqs)
                course.is_published = 'is_published' in request.POST
                course.is_open_to_all = 'is_open_to_all' in request.POST
                course.is_class_room_course = 'is_class_room_course' in request.POST

                course.save(create_qr=create_qr_code)
                # Log activity
                Activity.objects.create(
                    user=user,
                    activity_type="Course Update",
                    description=f"Updated course sections for: {course.title}"
                )
                messages.success(request, "Course created successfully!")
                request.session['step_one_done'] = False
                request.session['step_two_done'] = False
                request.session['step_three_done'] = False
                request.session['step_four_done'] = False
                request.session['step_five_done'] = False
                return redirect("course_list")
            else:
                return HttpResponse("Course ID is required to create a section.", status=400)
        except Exception as e:
            return HttpResponse(f"Error creating section: {str(e)}", status=500)
    return render(request, "course/creation/step_5.html", locals())

def get_quiz_questions(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    return JsonResponse(quiz.questions, safe=False)


def quiz_detail(request, quiz_id):
    request.session["page"] = "course"
    quiz = get_object_or_404(Quiz, id=quiz_id)
    rediect_url = ""
    if not request.user.is_authenticated:
        return redirect("login")

    # This logic seems correct
    profile = request.user.profile
    if Instructor.objects.filter(profile=profile).exists():
        return HttpResponse("Instructors cannot take quizzes.", status=403)
    
    #  Ensure the quiz is linked to a section/course/lesson
    if not (quiz.section or quiz.course or quiz.lesson):
        return HttpResponse("This quiz is not linked to any section, course, or lesson.", status=404)
    
    if not quiz.questions:
        return HttpResponse("This quiz has no questions.", status=404)
    
    if quiz.is_deleted:
        return HttpResponse("This quiz has been deleted.", status=404)
    
    if quiz.course:
        rediect_url = quiz.course.get_absolute_url()
    elif quiz.section:
        rediect_url = Course.objects.filter(sections=quiz.section).first().get_absolute_url()
    elif quiz.lesson:
        filtered_section = Section.objects.filter(lessons=quiz.lesson).first()
        rediect_url = Course.objects.filter(sections=filtered_section).first().get_absolute_url()

    # 1. Get the questions dictionary from your model.
    questions_dict = quiz.questions or {}

    # 2. Build the exact data structure the JavaScript expects.
    #    The JavaScript expects 'questions' to be an array of objects.
    quiz_data_for_js = {
        "id": quiz.id,
        "title": quiz.title,
        "passing_marks": quiz.passing_score, # Make sure your Quiz model has this field
        "questions": list(questions_dict.values()) # Convert the questions dictionary to a list
    }
    print("Quiz Data for JS:", quiz_data_for_js)

    # 3. Pass this complete structure to the template.
    return render(request, "components/quiz_detail.html", {
        "quiz": quiz,
        "quiz_data": quiz_data_for_js, # Pass the newly created object
        "quiz_id": quiz_id,
        "is_completed": quiz.completed_by_users.filter(id=profile.id).exists(),
        "redirect_url": rediect_url
    })

@require_POST
@csrf_exempt
def submit_quiz_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    try:
        data = json.loads(request.body)
        quiz_id = data.get('quiz_id')
        submission_data = data.get('submission')

        if not quiz_id or not submission_data:
            return JsonResponse({'status': 'error', 'message': 'Missing quiz_id or submission data.'}, status=400)
    except (json.JSONDecodeError, KeyError) as e:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)

    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions or {}

    final_score = 0
    total_possible_score = 0
    backend_results = {}

    for question_id, submitted_answer_details in submission_data.items():
        question_info = questions.get(str(question_id))
        if not question_info:
            print(f"Question {question_id} not found in quiz questions.")
            continue

        # Pull score from question metadata
        question_score = question_info.get('score_on_completion', 0)
        total_possible_score += question_score

        # Pull correctness and score from frontend submission
        is_correct = submitted_answer_details.get("is_correct", False)
        score_awarded = submitted_answer_details.get("score_awarded", 0)

        # Validate score on backend just in case
        if is_correct:
            score_awarded = question_score
            final_score += question_score
        else:
            score_awarded = 0

        backend_results[question_id] = {
            "is_correct": is_correct,
            "score_awarded": score_awarded,
            "user_answer": submitted_answer_details.get("user_answer"),
            "question_text": submitted_answer_details.get("question_text"),
            "human_answers": submitted_answer_details.get("human_answers"),
            "question_type" : submitted_answer_details.get("question_type"),
        }

    # Save attempt
    try:
        profile = request.user.profile
        quiz_submission, created = QuizSubmission.objects.get_or_create(
            user=profile,
            quiz=quiz
        )
        quiz_submission.score = final_score
        quiz_submission.total = total_possible_score
        quiz_submission.passed = bool(final_score >= quiz.passing_score)
        quiz_submission.answers = backend_results
        quiz_submission.save()

        all_correct = all(result['is_correct'] for result in backend_results.values())
        if all_correct and created:
            quiz.completed_by_users.add(profile)
            quiz.save()
    except Exception as e:
        print("Could not save quiz attempt:", str(e))
        return JsonResponse({'status': 'error', 'message': 'Could not save quiz attempt. Error: ' + str(e)}, status=500)

    return JsonResponse({
        'status': 'success',
        'message': 'Quiz submitted successfully.',
        'final_score': final_score,
        'total_possible_score': total_possible_score,
        'backend_results': backend_results
    })

def student_update_status(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

        if request.method != 'POST':
            return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

        data = json.loads(request.body)
        quiz_submission_id = data.get('quiz_submission_id')
        status = data.get('status')

        if not quiz_submission_id or not status:
            return JsonResponse({'status': 'error', 'message': 'Missing quiz_submission_id or status.'}, status=400)
        
        try:
            quiz_submission = QuizSubmission.objects.get(id=quiz_submission_id)
        except QuizSubmission.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Quiz submission not found.'}, status=404)

        if status == 'passed':
            quiz_submission.passed = True
            quiz_submission.save()
            return JsonResponse({'status': 'success', 'message': 'Status marked Passed successfully.'})
        else:
            quiz_submission.status = status.lower()
            quiz_submission.save()
            return JsonResponse({'status': 'success', 'message': 'Status updated successfully.'}, status=403)

    except Exception as e:
        print("Error updating status:", str(e))
        return JsonResponse({'status': 'error', 'message': 'Error updating status: ' + str(e)}, status=500)