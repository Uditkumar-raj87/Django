from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Lesson, Question, Choice, Submission


@login_required
def course_details(request, lesson_id):
    """Display course details and questions."""
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    questions = lesson.questions.all()
    context = {
        'lesson': lesson,
        'questions': questions,
    }
    return render(request, 'course_details_bootstrap.html', context)


@login_required
@require_http_methods(["POST"])
def submit(request, lesson_id):
    """Handle exam submission and calculate score."""
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    questions = lesson.questions.all()
    
    score = 0
    total_questions = questions.count()
    
    # Calculate score based on submitted answers
    for question in questions:
        question_key = f'question_{question.id}'
        selected_choice_id = request.POST.get(question_key)
        
        if selected_choice_id:
            try:
                selected_choice = Choice.objects.get(id=selected_choice_id)
                if selected_choice.is_correct:
                    score += 1
            except Choice.DoesNotExist:
                pass
    
    # Create submission record
    submission = Submission.objects.create(
        user=request.user,
        lesson=lesson,
        score=score,
        total_questions=total_questions
    )
    
    return redirect('show_exam_result', submission_id=submission.id)


@login_required
def show_exam_result(request, submission_id):
    """Display exam results with score and feedback."""
    submission = get_object_or_404(Submission, pk=submission_id, user=request.user)
    lesson = submission.lesson
    questions = lesson.questions.all()
    percentage = submission.get_percentage()
    
    # Build detailed results
    results_detail = []
    for question in questions:
        question_key = f'question_{question.id}'
        selected_choice_id = request.POST.get(question_key) if request.method == 'POST' else None
        
        result_item = {
            'question': question,
            'choices': question.choices.all(),
            'is_correct': False
        }
        
        # Find the user's answer for this question from the latest submission
        for choice in question.choices.all():
            if choice.is_correct:
                result_item['correct_choice'] = choice
        
        results_detail.append(result_item)
    
    # Determine pass/fail status
    passing_percentage = 70
    is_passed = percentage >= passing_percentage
    
    context = {
        'submission': submission,
        'lesson': lesson,
        'percentage': percentage,
        'is_passed': is_passed,
        'results_detail': results_detail,
        'score': submission.score,
        'total_questions': submission.total_questions,
    }
    return render(request, 'exam_result.html', context)
