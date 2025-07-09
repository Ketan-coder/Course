from io import BytesIO #A stream implementation using an in-memory bytes buffer
                       # It inherits BufferIOBase
 
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .decorators import *

# xhtml2pdf is a PDF generator using HTML and CSS
# It supports HTML 5 and CSS 2.1 (and some of CSS 3)
# It is completely written in pure Python so it is platform independent
from xhtml2pdf import pisa  
from .decorators import check_load_time
import google.generativeai as genai
import os
import json
import re

# Configure API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

@check_load_time
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    # Use 'utf-8' encoding instead of 'ISO-8859-1'
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


@check_load_time
def send_email(to_email, subject, title, body, anchor_link=None, anchor_text="Click Here"):
    """
    Sends a customizable email with an optional anchor link.
    
    :param to_email: Single email (str) or multiple emails (list)
    :param subject: Email subject
    :param title: Title shown in the email
    :param body: Email body (main text content)
    :param anchor_link: (Optional) Link to include in the email
    :param anchor_text: (Optional) Text for the anchor link (default: 'Click Here')
    """
    
    # Convert single email to list
    if isinstance(to_email, str):
        to_email = [to_email]
    
    # Construct anchor link if provided
    anchor_html = f'<p><a href="{anchor_link}" style="padding: 10px; background-color: #0076d1; color: white; text-decoration: none;">{anchor_text}</a></p>' if anchor_link else ""

    # Email content (HTML)
    html_content = f'''
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{title}</title>
    </head>
    <body style="font-family: 'Poppins', Arial, sans-serif; background: #ffffff; padding: 20px;">
        <h2 style="color: #0076d1;">{title}</h2>
        <p>{body}</p>
        {anchor_html}
        <p>If you did not request this, please ignore this email.</p>
    </body>
    </html>
    '''

    # Plain text fallback
    text_content = f"{title}\n\n{body}\n\n{anchor_link if anchor_link else ''}"

    # Send email
    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@check_load_time
def generate_quiz_from_content(section_title :str, lesson_content:str) -> dict:
    # models = genai.list_models()

    # for m in models:
    #     print(m.name, m.supported_generation_methods)
    prompt = f'''
You are an expert quiz creator.

Generate 5 quiz questions from the lesson below. Vary the question types among these:
- SINGLE_SELECT (one correct option)
- MULTIPLE_SELECT (one correct option but marked as that type)
- TEXT (user types answer)
- IMAGE_MC (multiple choice with an image)
- DRAG_DROP (sentence with blanks and draggable options)

Each question should include:
- id (string)
- question (text)
- type
- options (if applicable)
- correct answer
- for IMAGE_MC include an "image" field
- for DRAG_DROP include sentence_parts, draggable_options, and correct_mapping

Return JSON in this format:
{{
  "1": {{
    "id": "1",
    "question": "...",
    "options": [...],
    "type": "SINGLE_SELECT",
    "answer": "..."
  }},
  "2": {{ ... }},
  ...
}}

Here is an example of a question:
{{"1": {{"id": "1", "question": "What is the capital of France?", "options": [{{"id": "Paris", "text": "Paris"}}, {{"id": "London", "text": "London"}}], "type": "MULTIPLE_SELECT", "answer": "Paris"}}, "2": {{"id": "2", "question": "What is 2 + 2?", "options": [{{"id": "1", "text": "1"}}, {{"id": "2", "text": "2"}}, {{"id": "3", "text": "3"}}, {{"id": "4", "text": "4"}}], "type": "SINGLE_SELECT", "answer": "4"}}, "3": {{"id": "3", "question": "Capital of Nepal?", "options": [], "type": "TEXT", "answer": "Kathmandu"}}, "4": {{"id": "4", "question": "Which monument is shown?", "type": "IMAGE_MC", "image": "media/monuments/eiffel.jpg", "options": [{{"id": "Taj Mahal", "text": "Taj Mahal"}}, {{"id": "Colosseum", "text": "Colosseum"}}, {{"id": "Eiffel Tower", "text": "Eiffel Tower"}}], "answer": "Eiffel Tower"}}, "5": {{"id": "5", "question": "Complete the sentence", "type": "DRAG_DROP", "sentence_parts": ["The quick brown ", null, " jumps over the ", null, " dog."], "draggable_options": [{{"id": "fox", "text": "fox"}}, {{"id": "lazy", "text": "lazy"}}, {{"id": "quick", "text": "quick"}}], "correct_mapping": {{"0": "fox", "1": "lazy"}}}}}}

Output **only valid JSON**, with no comments or markdown.

Section Title: {section_title}

Lesson Content:
{lesson_content}
'''

    # response = model.generate_content(prompt)
    # print("Gemini Response:", response)
    try:
        response = model.generate_content(prompt)
        print("Gemini Response:", response)

        # Get the raw text from first candidate part
        raw_text = response.candidates[0].content.parts[0].text

        # Extract JSON from code block using regex
        match = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
        if not match:
            raise ValueError("Could not find JSON block in the response.")

        quiz_json = match.group(1)
        parsed_data = json.loads(quiz_json)
        print("Quiz Data given from AI ==>", parsed_data)
        return parsed_data

    except Exception as e:
        print("Error parsing Gemini response:", e)
        return {}
