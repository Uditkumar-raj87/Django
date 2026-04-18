import os
import re
import requests
from weasyprint import HTML
import fitz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onlinecourse.settings")
import django  # noqa: E402

django.setup()

from django.contrib.auth.models import User  # noqa: E402
from courses.models import Question, Submission  # noqa: E402

BASE_URL = "http://localhost:8000"
OUTPUT_ADMIN = "/workspaces/Django/03-admin-site.png"
OUTPUT_RESULT = "/workspaces/Django/07-final.png"


def html_to_png(html_text, base_url, output_path):
    temp_pdf = output_path.replace(".png", ".pdf")
    HTML(string=html_text, base_url=base_url).write_pdf(temp_pdf)
    doc = fitz.open(temp_pdf)
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    pix.save(output_path)
    doc.close()
    os.remove(temp_pdf)


def login(session, username, password):
    login_url = f"{BASE_URL}/admin/login/"
    response = session.get(login_url, timeout=15)
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
    token = match.group(1) if match else ""
    payload = {
        "username": username,
        "password": password,
        "csrfmiddlewaretoken": token,
        "next": "/admin/",
    }
    headers = {"Referer": login_url}
    session.post(login_url, data=payload, headers=headers, timeout=15)


def create_passing_submission(user):
    questions = Question.objects.order_by("lesson_id", "order")
    first_question = questions.first()
    if not first_question:
        raise RuntimeError("No questions found. Seed data first.")

    lesson = first_question.lesson
    course = lesson.course

    submission = Submission.objects.create(user=user, course=course, lesson=lesson)
    correct_choices = []
    total_score = 0
    total_possible = 0
    for q in questions:
        selected = list(q.choices.filter(is_correct=True).values_list("id", flat=True))
        correct_choices.extend(selected)
        total_possible += q.grade
        total_score += q.is_get_score(selected)

    submission.selected_choices.set(correct_choices)
    submission.score = total_score
    submission.total_questions = questions.count()
    submission.save(update_fields=["score", "total_questions"])
    return submission.id


def main():
    admin_user = User.objects.get(username="admin")
    result_submission_id = create_passing_submission(admin_user)

    session = requests.Session()
    login(session, "admin", "admin123")

    admin_html = session.get(f"{BASE_URL}/admin/", timeout=15).text
    html_to_png(admin_html, BASE_URL, OUTPUT_ADMIN)

    result_html = session.get(f"{BASE_URL}/result/{result_submission_id}/", timeout=15).text
    html_to_png(result_html, BASE_URL, OUTPUT_RESULT)

    print("Created screenshots:")
    print(OUTPUT_ADMIN)
    print(OUTPUT_RESULT)


if __name__ == "__main__":
    main()
