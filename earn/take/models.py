from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
# from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    # other fields...
# Course model
# Lesson model


class User(AbstractUser):
    is_admin = models.BooleanField('is admin', default=False)
    is_instructor = models.BooleanField('is instructor', default=False)
    is_student = models.BooleanField('is student', default=False)


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='course/image', blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    duration = models.DurationField(default=timedelta(hours=0))
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def is_free(self):
        return self.is_paid == 0


class Lesson(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)  # For sorting like Lesson 1, 2, 3

    def __str__(self):
        return f"{self.title} - {self.course.title}"


# Quiz model (optional)
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Lecture(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=50, choices=(('text', 'Text'), ('video', 'Video'), ('pdf', 'Pdf')), default='text')
    text_content = models.TextField(blank=True, null=True)
    video_content = models.FileField(upload_to='lectures', blank=True, null=True)
    pdf = models.FileField(upload_to='pdfs', blank=True, null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='lectures')

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('SA', 'Short Answer'),
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return self.text
    # ... (add fields for question type, choices, correct answer)


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}"


class UserAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.attempt.user.username} answered {self.selected_choice.text}"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='studentprofile')
    is_instructor = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='profile/image', blank=True, null=True)

    def __str__(self):
        return self.user.username
    # ... other student-specific fields


class Enrollment(models.Model):
    is_student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    enrollment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('is_student', 'course')

    def __str__(self):
        return f"{self.is_student} enrolled in {self.course}"


class Certificate(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    date_issued = models.DateTimeField(auto_now_add=True)
    # ... other certificate details (e.g., PDF file)

    def __str__(self):
        return str(self.student)


class CourseDetail(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.course)
# Create your models here.


class LectureProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    watched_video = models.BooleanField(default=False)
    viewed_pdf = models.BooleanField(default=False)
    completed_quiz = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'lecturer')
