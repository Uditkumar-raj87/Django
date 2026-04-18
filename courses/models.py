from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pub_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "course"

    def __str__(self):
        return self.name


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField(default=0)
    courses = models.ManyToManyField(Course, related_name="instructors", blank=True)

    class Meta:
        db_table = "instructor"

    def __str__(self):
        return self.user.username


class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    occupation = models.CharField(max_length=200, blank=True)
    social_link = models.URLField(blank=True)

    class Meta:
        db_table = "learner"

    def __str__(self):
        return self.user.username


class Lesson(models.Model):
    """Model to represent a lesson in an online course."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", null=True, blank=True)
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
    grade = models.IntegerField(default=1)
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

    def is_get_score(self, selected_ids):
        correct_choice_ids = set(self.choices.filter(is_correct=True).values_list("id", flat=True))
        selected_for_question = set(
            self.choices.filter(id__in=selected_ids).values_list("id", flat=True)
        )
        return self.grade if selected_for_question == correct_choice_ids else 0


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
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="submissions", null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    selected_choices = models.ManyToManyField(Choice, related_name="submissions", blank=True)
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
