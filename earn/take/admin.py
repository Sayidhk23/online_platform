from django.contrib import admin

from .models import Course, Lecture, Quiz, Question, StudentProfile, Enrollment, Certificate, Lesson, Category, \
    CourseDetail, Choice, QuizAttempt, UserAnswer

admin.site.register(Lesson)
admin.site.register(Course)
admin.site.register(Lecture)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(StudentProfile)
admin.site.register(Enrollment)
admin.site.register(Certificate)
admin.site.register(Category)
admin.site.register(CourseDetail)
admin.site.register(Choice)
admin.site.register(QuizAttempt)
admin.site.register(UserAnswer)

# admin.site.register(Course, CourseAdmin)


# Register your models here.
