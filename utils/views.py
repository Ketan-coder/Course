from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from Tiers.models import Tier, Tournament, LeaderboardEntry
from Courseapp.models import Quiz, Course
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from utils.models import FeedBack
from Users.models import Profile, Student, Instructor
from django.db.models import Sum
import json

# Create your views here.
def quiz_helper(request) -> HttpResponse:
    # mcq_quiz = {
    #     "id": "science_q1",
    #     "title": "Science Quiz!",
    #     "current_question_number": 1,
    #     "total_questions": 5,
    #     "question": "What is H₂O?",
    #     "options": [
    #         {"id": "opt_water", "text": "Water"},
    #         {"id": "opt_acid", "text": "Acid"},
    #         {"id": "opt_salt", "text": "Salt"},
    #     ],
    #     "correct_option_id": "opt_water",
    #     "correct_feedback": "Excellent! That's correct.",
    #     "incorrect_feedback": "Not quite. H₂O is the chemical formula for Water."
    # }

    # imcq_quiz = {
    #     "id": "geo_q1",
    #     "title": "Geography Challenge",
    #     "current_question_number": 1,
    #     "total_questions": 3,
    #     "question": "Which monument is shown in the image?",
    #     "image_to_show_url": "{% static 'path/to/your/image.jpg' %}", # Use Django's static template tag
    #     "image_alt_text": "A famous monument",
    #     "options": [
    #         {"id": "iopt_eiffel", "text": "Eiffel Tower"},
    #         {"id": "iopt_taj", "text": "Taj Mahal"},
    #         {"id": "iopt_colosseum", "text": "Colosseum"},
    #     ],
    #     "correct_option_id": "iopt_eiffel",
    # }

    # dnd_quiz = {
    #     "id": "grammar_q1",
    #     "title": "Complete the Sentence",
    #     "progress_percentage": 33,
    #     "sentence_parts": ["The quick brown ", None, " jumps over the ", None, " dog."],
    #     "draggable_options": [
    #         {"id": "fox", "text": "fox", "icon_class": "bi bi-record-fill"}, # Example icon
    #         {"id": "lazy", "text": "lazy", "icon_class": "bi bi-pause-fill"},
    #         {"id": "quick", "text": "quick"}, # No icon
    #     ],
    #     # blank_index: draggable_option_id (the part after "drag-quiz_id-")
    #     "correct_mapping": { 
    #         "0": "fox",
    #         "1": "lazy"
    #     },
    #     #  "icon_svg_path": "path/to/your/custom_click_icon.svg", # Optional custom icon for modal title
    # }
    # # Calculate progress percentage
    # current_question_number = 1
    # # total_questions = mcq_quiz["total_questions"] + imcq_quiz["total_questions"] + dnd_quiz["total_questions"]
    # total_questions = 3
    # print(f"Total Questions: {total_questions}")
    # print(f"Current Question Number: {current_question_number}")
    # if total_questions > 0:
    #     progress: float = (current_question_number / total_questions) * 100
    # else:
    #     progress = 0

    # context = {
    #     "mcq_data_1": mcq_quiz,
    #     "imcq_data_1": imcq_quiz,
    #     "dnd_data_1": dnd_quiz,
    #     "current_question_number": 1,
    #     "total_questions": total_questions,
    #     "progress_percentage": round(progress),
    # }
    try:
        quiz: Quiz = get_object_or_404(Quiz, id=1)

        # Unpack dynamic questions from JSONField
        raw_questions = quiz.questions or {}
        question_items = list(raw_questions.items())  # List of (qid, question_dict)
        total_questions: int = len(question_items)
        # print(raw_questions)

        # To display all questions, you should iterate through the question_items
        # and build a list of questions, instead of processing only one.
        questions_list = []
        for current_index, (qid, current_question) in enumerate(question_items):

            # Determine question type
            q_type = current_question.get("type", "").upper()
            question_text = current_question.get("question")
            options = current_question.get("options", [])
            answer = current_question.get("answer")  # For validation or feedback

            image_url = current_question.get("image")
            sentence_parts = current_question.get("sentence_parts")
            draggable_options = current_question.get("draggable_options")
            correct_mapping = current_question.get("correct_mapping")
            correct_mapping_json = json.dumps(correct_mapping)

            questions_list.append({
                "id": qid,
                "question_number": current_index + 1,
                "question": question_text,
                "question_type": q_type,
                "options": options,
                "image_url": image_url,
                "sentence_parts": sentence_parts,
                "draggable_options": draggable_options,
                "correct_mapping": correct_mapping_json,
                "correct_answer": answer,
            })
        print(questions_list)
    except Exception as e:
        print(e)

    context = {
        "quiz_data": quiz,
        "quiz": quiz,
        "total_questions": total_questions,
        "questions_list": questions_list, # Pass the list of all questions to the template
    }
    return render(request, 'components/quiz_helper.html', context)

def index(request):
    request.session["page"] = "home"
    # Check if user is authenticated
    if not request.user.is_authenticated:
        # If not authenticated, redirect to the login page
        return redirect('login')
    
    current_user = request.user
    if current_user.is_authenticated:
        context = {} # Initialize context for authenticated users
        try:
            profile = Profile.objects.get(user=current_user)
            if Student.objects.filter(profile=profile).exists():
                enrolled_courses = Course.objects.filter(is_bought_by_users=profile)
                
                student_profile = Student.objects.get(profile=profile)
                request.session['streak'] = student_profile.streak
                request.session['score'] = student_profile.score
                request.session['current_user_type'] = 'student'
            
                course_progress = []
                for course in enrolled_courses:
                    total_lessons = 0
                    completed_lessons = 0

                    for section in course.sections.all():
                        lessons = section.lesson.all()
                        total_lessons += lessons.count()
                        completed_lessons += lessons.filter(completed_by_users=profile).count()

                    progress_percent = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

                    course_progress.append({
                        'course': course,
                        'progress': progress_percent,
                    })
                # Get all active tournaments
                tournaments = Tournament.objects.filter(is_active=True, participants=profile).order_by('-start_date')

                # Get latest active tournament for leaderboard
                current_tournament = tournaments.first() if tournaments.exists() else None

                # Fetch leaderboard entries
                leaderboard_entries = []
                user_rank = None

                if current_tournament:
                    all_entries = LeaderboardEntry.objects.filter(tournament=current_tournament).order_by('-score', 'timestamp')

                    leaderboard_entries = all_entries[:10]

                    for idx, entry in enumerate(all_entries, start=1):
                        if entry.profile == profile:
                            user_rank = idx
                            break
                
                # Fetch user score (from leaderboard)
                entry = LeaderboardEntry.objects.filter(profile=profile).order_by('-timestamp').first()
                user_score = entry.score if entry else 0

                # Get current tier and upcoming tier
                current_tier = Tier.objects.filter(min_score__lte=user_score).order_by('-min_score').first()
                next_tier = Tier.objects.filter(min_score__gt=user_score).order_by('min_score').first()

                # Progress to next tier
                if next_tier:
                    progress_percent = int((user_score - current_tier.min_score) / (next_tier.min_score - current_tier.min_score) * 100) if current_tier else 0
                    score_needed = next_tier.min_score - user_score
                else:
                    progress_percent = 100
                    score_needed = 0
            
                context = {
                    'user_role': 'student',
                    'enrolled_courses': course_progress,
                    'tournaments': tournaments,
                    'leaderboard': leaderboard_entries,
                    'user_rank': user_rank,
                    'current_tournament': current_tournament,
                    'current_tier': current_tier,
                    'next_tier': next_tier,
                    'progress_percent': progress_percent,
                    'score_needed': score_needed,
                    'rewards': {
                        'stocks_earned': 50.00,        # Static for now, can be made dynamic later
                        'stock_growth': '+10%',
                        'vouchers': 2,
                        'voucher_growth': '+1',
                    }
                }
            elif Instructor.objects.filter(profile=profile).exists():
                course = Course.objects.filter(instructor__profile=profile)
                request.session['current_user_type'] = 'instructor'
                course_count = 0
                enrolled_students = 0
                total_earnings = 0
                total_bookmarked_by_students = 0
                if course.exists():
                    course_count = course.count()
                    enrolled_students = sum(c.is_bought_by_users.count() for c in course)
                    total_earnings = 0
                    if course.filter(is_open_to_all=False, course_type='paid').exists():
                        users_who_bought_courses = course.filter(is_open_to_all=False, course_type='paid')
                        if users_who_bought_courses.exists():
                            for c in course:
                                total_earnings += users_who_bought_courses.count() * c.price
                    total_bookmarked_by_students = sum(c.bookmarked_by_users.count() for c in course)

                    for c in course:
                        c.students_count = c.is_bought_by_users.count()
                        c.bookmarked_count = c.bookmarked_by_users.count()
                        users_who_bought_courses = c.is_bought_by_users.all()
                        c.earnings = (users_who_bought_courses.count() if users_who_bought_courses else 0) * c.price if users_who_bought_courses else 0

                context = {
                    'user_role': 'instructor',
                    'course_count': course_count or 0,
                    'enrolled_students': enrolled_students or 0,
                    'total_earnings': total_earnings or 0,
                    'total_bookmarked_by_students': total_bookmarked_by_students or 0,
                    'instructor_name': profile.user.get_full_name() or profile.user.username,
                    'courses': course,
                    'instructor_currency': profile.currency.symbol or 'INR'
                }
        except Profile.DoesNotExist:
            messages.error(request,"Profile Cannot be Found!")
    else:
        return redirect('login')
    return render(request, 'index.html',context)

def landing_page(request) -> HttpResponse:
    request.session["page"] = "home"
    if request.method == "POST":
        print(request.POST)
        name: str = request.POST.get("name")
        email: str = request.POST.get("email")
        message: str = request.POST.get("message")
        if name != '' or email != '' or message != '':
            user = User.objects.filter(email=email)
            if user.exists() or user:
                FeedBack.objects.create(name=name, email=email, message=message, user=user.first())
            else:
                FeedBack.objects.create(name=name, email=email, message=message)
    return render(request, 'landing_page.html')

def custom_404(request, exception):
    return render(request, 'middleware/custom_debug.html', {
        "exception": "Page not found",
        "traceback": "No traceback. URL did not match any pattern.",
        "path": request.path,
        "method": request.method,
        "error_code": 404
    }, status=404)

def custom_500(request):
    return render(request, 'middleware/custom_debug.html', {
        "exception": "Internal Server Error",
        "traceback": "Unhandled server error occurred.",
        "path": request.path,
        "method": request.method,
        "error_code": 500
    }, status=500)