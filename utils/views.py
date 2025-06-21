from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from Courseapp.models import Quiz
from django.contrib.auth.models import User
from utils.models import FeedBack
import json

# Create your views here.
def index(request) -> HttpResponse:
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
    return render(request, 'index.html', context)

def landing_page(request) -> HttpResponse:
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