# courses/forms.py
from django import forms

from . import admin
from .models import Course, Lecture, Quiz, Question, StudentProfile, Category, Lesson, Enrollment, Choice, QuizAttempt, \
    UserAnswer, CourseDetail, Certificate


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'image', 'description', 'instructor', 'category', 'price','is_paid', 'duration']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholders': 'Enter the name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholders': 'Enter the details'}),
            'instructor': forms.Select(attrs={'class': 'form-control', 'placeholders': 'choose category'}),
            'category': forms.Select(attrs={'class': 'form-control', 'placeholders': 'choose category'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'choose a image'})
        }


class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['course', 'title', 'lesson', 'content_type', 'text_content', 'video_content', 'pdf']

    # Optionally, you can add custom validation or clean methods if needed
    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        text_content = cleaned_data.get('text_content')
        video_content = cleaned_data.get('video_content')
        pdf = cleaned_data.get('pdf')

        # Ensure that only one of the content fields is filled based on content_type

        if content_type:  # check if content type exists.
            if content_type == 'text_content' and not text_content:
                self.add_error('text_content', "Text content is required for this type.")
            elif content_type == 'video_content' and not video_content:
                self.add_error('video_content', "Video is required for this type.")
            elif content_type == 'image_content' and not pdf:
                self.add_error('pdf', "File is required for this type.")

        return cleaned_data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'course', 'order']


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['is_student', 'course', 'is_paid']


# @admin.register(Course)
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ('title', 'instructor', 'price', 'duration', 'created_at')

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'lesson']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['quiz', 'text', ]


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['question', 'text', 'is_correct']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['user', 'is_student', 'is_instructor', 'email', 'image']


class QuizAttemptForm(forms.ModelForm):
    class Meta:
        model = QuizAttempt
        fields = ['user', 'quiz', 'score']


class UserAnswerForm(forms.ModelForm):
    class Meta:
        model = UserAnswer
        fields = ['attempt', 'question']


class CourseDetailForm(forms.ModelForm):
    class Meta:
        model = CourseDetail
        fields = ['course', 'instructor', 'category']


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['student', 'course', 'description']