from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Course, Lesson, Question, Submission


@login_required
def course_details(request, lesson_id):
    """Display course details and all related lessons/questions."""
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    course = lesson.course
    lessons = course.lessons.all() if course else Lesson.objects.filter(pk=lesson_id)
    questions = Question.objects.filter(lesson__in=lessons).order_by("lesson_id", "order")
    context = {
        'course': course,
        'lesson': lesson,
        'lessons': lessons,
        'questions': questions,
    }
    return render(request, 'course_details_bootstrap.html', context)


@login_required
@require_http_methods(["POST"])
def submit(request, lesson_id):
    """Handle exam submission and store selected choices."""
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    course = lesson.course

    selected_ids = []
    for key, value in request.POST.items():
        if key.startswith('question_'):
            try:
                selected_ids.append(int(value))
            except ValueError:
                continue

    submission = Submission.objects.create(
        user=request.user,
        course=course,
        lesson=lesson,
    )
    submission.selected_choices.set(selected_ids)

    return redirect('show_exam_result', submission_id=submission.id)


@login_required
def show_exam_result(request, submission_id):
    """Display exam results and detailed grading."""
    submission = get_object_or_404(Submission, pk=submission_id, user=request.user)
    lesson = submission.lesson
    course = submission.course or lesson.course
    selected_ids = list(submission.selected_choices.values_list('id', flat=True))

    questions = Question.objects.filter(lesson__course=course).order_by('lesson_id', 'order')
    total_score = 0
    possible_score = 0
    for question in questions:
        total_score += question.is_get_score(selected_ids)
        possible_score += question.grade

    submission.score = total_score
    submission.total_questions = questions.count()
    submission.save(update_fields=['score', 'total_questions'])

    percentage = (total_score / possible_score * 100) if possible_score else 0
    is_passed = percentage >= 70

    context = {
        'course': course,
        'selected_ids': selected_ids,
        'grade': total_score,
        'possible': possible_score,
        'submission': submission,
        'lesson': lesson,
        'questions': questions,
        'percentage': percentage,
        'is_passed': is_passed,
        'score': total_score,
        'total_questions': possible_score,
    }
    return render(request, 'exam_result_bootstrap.html', context)
