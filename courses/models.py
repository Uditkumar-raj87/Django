from django.db import models
from django.contrib.auth.models import User


class Lesson(models.Model):
    """Model to represent a lesson in an online course."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lesson"

    def __str__(self):
        return self.title


class Question(models.Model):
    """Model to represent an exam question associated with a lesson."""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=10,
        choices=[('MC', 'Multiple Choice')],
        default='MC'
    )
    order = models.IntegerField(default=0)

    class Meta:
        db_table = "question"
        ordering = ['order']

    def __str__(self):
        return self.question_text[:50]


class Choice(models.Model):
    """Model to represent choice options for multiple choice questions."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = "choice"
        ordering = ['order']

    def __str__(self):
        return self.choice_text[:50]


class Submission(models.Model):
    """Model to represent an exam submission by a student."""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0)
    total_questions = models.IntegerField(default=0)

    class Meta:
        db_table = "submission"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"

    def get_percentage(self):
        """Calculate the percentage score."""
        if self.total_questions == 0:
            return 0
        return (self.score / self.total_questions) * 100
