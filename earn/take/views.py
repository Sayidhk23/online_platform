from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, AbstractUser
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse

from .models import User, StudentProfile, Lesson, QuizAttempt, Choice, UserAnswer, Category, Question, Certificate, \
    LectureProgress
# courses/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Course, Lecture, Quiz, Enrollment, CourseDetail
from .forms import CourseForm, LectureForm, ProfileForm, CategoryForm, LessonForm, EnrollmentForm, QuizForm, \
    QuestionForm, ChoiceForm, QuizAttemptForm, UserAnswerForm, CourseDetailForm, CertificateForm
from .decoraters import instructor_required


def student(request):
    student_profile = get_object_or_404(StudentProfile, user=request.user)

    #Get courses the student is enrolled in
    enrollments = Enrollment.objects.filter(is_student=student_profile)
    courses = [enrollment.course for enrollment in enrollments]

    context = {
        'user': request.user,
        'student_profile': student_profile,
        'courses': courses,
    }
    return render(request, 'dashboard.html', context)


def home(request):
    course = Course.objects.all()
    print(course)

    return render(request, 'home.html',{'form': course})


def lecture(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    lectures = Lecture.objects.filter(course=course)
    lessons = Lesson.objects.filter(course=course).prefetch_related('lectures', 'quizzes').order_by('order')
    progress = {
        lecturer.id: LectureProgress.objects.filter(user=request.user, lecturer=lecturer).first()
        for lecturer in lectures
    }

    context ={
        'course': course,
        'course_id': course_id,
        'lectures': lectures,
        'lessons': lessons,
        'progress': progress,
    }
    return render(request, 'lectures.html', context)


# blue tick function
@login_required
def mark_video_watched(request, lecture_id):
    lecturer = get_object_or_404(Lecture, pk=lecture_id)
    progress, _ = LectureProgress.objects.get_or_create(user=request.user, lecturer=lecturer)
    progress.watched_video = True
    progress.save()
    return JsonResponse({'status': 'ok'})

@login_required
def mark_pdf_viewed(request, lecture_id):
    lecturer = get_object_or_404(Lecture, pk=lecture_id)
    progress, _ = LectureProgress.objects.get_or_create(user=request.user, lecturer=lecturer)
    progress.viewed_pdf = True
    progress.save()
    return JsonResponse({'status': 'ok'})


# @instructor_required
def is_instructor(user):
    return user.is_authenticated and getattr(user, 'is_instructor', False)


def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('course_create')
    com = CourseForm()
    return render(request, 'add_course.html', {'com': com})


@login_required
def course_create(request):
    if request.method == 'POST':
        # Include course information when creating the lecture
        form = LectureForm(request.POST, request.FILES, request.user)
        if form.is_valid():
            form.save()
        return redirect('home')
    lom = LectureForm()
    return render(request, 'course_create.html', {'form': lom})


def edit_lecture(request, lecture_id):
    lectures = get_object_or_404(Lecture, id=lecture_id)
    if request.method == 'POST':
        form = LectureForm(request.POST, request.FILES, instance=lectures)
        if form.is_valid():
            form.save()
            return redirect('home')
    form = LectureForm(instance=lectures)
    return render(request, 'edit_lecture.html', {'form': form})



from django.contrib.auth.decorators import login_required




@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.user.is_superuser:
        return redirect('lecture', course_id=course_id)
    elif request.user.is_instructor:
        return redirect('lecture', course_id=course_id)

    # Get the logged-in user's StudentProfile
    student_profile = get_object_or_404(StudentProfile, user=request.user)

    # Check if already enrolled
    already_enrolled = Enrollment.objects.filter(is_student=student_profile, course=course).exists()
    if already_enrolled:
        return redirect('lecture', course_id=course_id)

    if request.method == 'POST':
        if course.is_free():
            # Auto enroll for free course
            Enrollment.objects.create(is_student=student_profile, course=course, is_paid=True)
            return redirect('lecture', course_id=course_id)
        else:
            # For paid courses, redirect to payment page
            return redirect('course_payment', course_id=course_id)

    return render(request, 'course_enroll.html', {'course': course})



@login_required
def course_payment(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.method == 'POST':
        # In real app, add Stripe, Razorpay, etc.

        Enrollment.objects.create(is_student=request.user.is_student, course=course, is_paid=True)
        return redirect('lecture', course_id=course_id)

    return render(request, 'payment.html', {'course': course})


def course_list(request):
    cours = Course.objects.all()  # Or filter as needed
    if request.user.is_authenticated:
     # Dynamically adding the attribute (as a quick fix, but not ideal for long-term)
        if hasattr(request.user, 'is_instructor'):
            if request.user.is_instructor:
                print("User is an instructor")
            else:
                print("User is a student")
        else:
            print("User doesn't have 'is_instructor' attribute")
    else:
        print("User is not logged in")
    return render(request, 'course_list.html', {'cours': cours})


@login_required
def profile_view(request):
    student_profile = get_object_or_404(StudentProfile, user=request.user)

    # Get courses the student is enrolled in
    enrollments = Enrollment.objects.filter(is_student=student_profile)
    courses = [enrollment.course for enrollment in enrollments]

    context = {
        'user': request.user,
        'student_profile': student_profile,
        'courses': courses,
    }
    return render(request, 'profile.html', context)


@login_required
def delete_lecture(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    course_id = lecture.course.id
    lecture.delete()
    return redirect('lecture', course_id=course_id)


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        confirm_password = request.POST['confirm_password']
        email = request.POST['email']
        full_name = request.POST['full_name']

        if password1 != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        try:
            user = User.objects.create_user(username=username, password=password1, email=email)
            user.first_name = full_name
            user.is_student = True
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('signup')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('register')

    return render(request, 'register.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            user.save()
            login(request, user)  # Log the user in
            return redirect('student')  # Redirect to home page or dashboard
        else:
            # If authentication fails, show an error message
            messages.error(request, 'Invalid credentials, please try again.')

    return render(request, 'signin.html')


def signout(request):
    logout(request)
    return render(request, 'home.html')


def in_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        confirm_password = request.POST['confirm_password']
        email = request.POST['email']
        full_name = request.POST['full_name']

        if password1 != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('in_register')

        try:
            user = User.objects.create_user(username=username, password=password1, email=email)
            # instructor_group = Group.objects.get(name='is_instructor')
            # user.groups.add(instructor_group)
            user.first_name = full_name
            user.is_instructor = True
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('signup')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('in_register')

    return render(request, 'in_register.html')


def mlog(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            user.save()
            login(request, user)  # Log the user in
            return redirect('admin')  # Redirect to home page or dashboard
        else:
            # If authentication fails, show an error message
            messages.error(request, 'Invalid credentials, please try again.')

    return render(request, 'inlog.html')


def admin_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        confirm_password = request.POST['confirm_password']
        email = request.POST['email']
        full_name = request.POST['full_name']

        if password1 != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('in_register')

        try:
            user = User.objects.create_user(username=username, password=password1, email=email)
            # instructor_group = Group.objects.get(name='is_instructor')
            # user.groups.add(instructor_group)
            user.first_name = full_name
            user.is_admin = True
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('inlog')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('admin_register')

    return render(request, 'admin_sign.html')


def details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    lessons = Lesson.objects.filter(course=course).order_by('order')

    context = {
        'course': course,
        'lessons': lessons,
    }
    return render(request, 'course_detail.html', context)


def admin(request):
    # student_profile = get_object_or_404(StudentProfile, is_student=request.user)
    #
    # context = {
    #     'user': request.user,
    #     'student_profile': student_profile,
    # }
    return render(request, 'dashboard_ad.html')

# Create your views here.



# Quiz Quize

# @login_required
# def quiz_list(request):
#     lessons = Lesson.objects.prefetch_related('lectures', 'quizzes').all()
#     return render(request, 'lectures.html', {'lessons': lessons})

# Show quiz with questions and choices
@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    questions = quiz.questions.prefetch_related('choices')
    return render(request, 'quiz_detail.html', {'quiz': quiz, 'questions': questions})

# Submit quiz answers
@login_required
@transaction.atomic
def submit_quiz(request, quiz_id):
    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        questions = quiz.questions.all()
        correct_count = 0

        attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz, score=0)

        for question in questions:
            selected_choice_id = request.POST.get(str(question.id))
            if selected_choice_id:
                selected_choice = get_object_or_404(Choice, pk=selected_choice_id)
                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_choice=selected_choice
                )
                if selected_choice.is_correct:
                    correct_count += 1

        total_questions = questions.count()
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        attempt.score = score
        attempt.save()

        messages.success(request, f'Quiz submitted! You scored {score:.2f}%.')
        return redirect('quiz_result', attempt_id=attempt.id)

    return redirect('quiz_detail', quiz_id=quiz_id)

@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    user_answers = UserAnswer.objects.filter(attempt=attempt).select_related('question', 'selected_choice')

    return render(request, 'quiz_result.html', {
        'attempt': attempt,
        'user_answers': user_answers,
    })


def courses(request):
    course = Course.objects.all()
    cate = Category.objects.all()
    print(course)
    return render(request, 'course.html', {'course': course, 'cate': cate})

@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return redirect('course')


def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course')
    course = CourseForm(instance=course)
    return render(request, 'edit_course.html', {'course': course})


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('course')
    cate = CategoryForm()
    return render(request, 'add_category.html', {'cate': cate})

def delete_category(request, category_id):
    cate = get_object_or_404(Category, id=category_id)
    cate.delete()
    return redirect('course')


def lesson_ad(request):
    lesson = Lesson.objects.all()
    lectures = Lecture.objects.all()
    return render(request, 'lesson.html', {'lesson': lesson, 'lectures': lectures})


def add_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('lessons')

    lesson = LessonForm()
    return render(request, 'add_lesson.html', {'lesson': lesson})


def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    lesson.delete()
    return redirect('lessons')


def enrollment(request):
    enroll = Enrollment.objects.all()
    return render(request, 'enroll.html',{'enroll': enroll})


def add_enroll(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('enrollment')

    enroll = EnrollmentForm()
    return render(request, 'add_enroll.html', {'enroll': enroll})


def delete_enroll(request, enrollment_id):
    enroll = get_object_or_404(Enrollment, id=enrollment_id)
    enroll.delete()
    return redirect('enrollment')


def candidate_pf(request):

    profiles = StudentProfile.objects.all()
    return render(request, 'candidate_pf.html', {'profiles': profiles})


def add_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('profiles')
    profile = ProfileForm()
    return render(request, 'pf_form.html', {'profile': profile})


def edit_profile(request, profile_id):
    profiles = get_object_or_404(StudentProfile, pk=profile_id)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profiles)
        if form.is_valid():
            form.save()
            return redirect('profiles')
    profile = ProfileForm(instance=profiles)
    return render(request, 'edit_profile.html', {'profile': profile})


def delete_candidate(request, profile_id):
    profile = get_object_or_404(StudentProfile, pk=profile_id)
    profile.delete()
    return redirect('profiles')

def quiz_ad(request):
    quiz = Quiz.objects.all()
    question = Question.objects.all()
    choice = Choice.objects.all()

    context = {
        'quiz': quiz,
        'question': question,
        'choice': choice,
    }
    return render(request, 'quiz.html', context)


def add_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            if request.user.is_superuser:
                return redirect('quiz')
            else:
                return redirect('quiz_instructor')
    else:
        quiz = QuizForm()
    return render(request, 'add_quiz.html', {'quiz': quiz})


def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        form = QuizForm(request.POST, request.FILES, instance=quiz)
        if form.is_valid():
            form.save()
            if request.user.is_superuser:
                return redirect('quiz')
            else:
                return redirect('quiz_instructor')
        else:
            quiz = QuizForm(instance=quiz)
    return render(request, 'edit_quiz.html', {'quiz': quiz})


def add_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            if request.user.is_superuser:
                return redirect('quiz')
            else:
                return redirect('quiz_instructor')
    else:
        quiz = QuestionForm()
        return render(request, 'add_question.html', {'quiz': quiz})


def edit_question(request, question_id):
    quiz = get_object_or_404(Quiz, id=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES, instance=quiz)
        if form.is_valid():
            form.save()
            if request.user.is_superuser:
                return redirect('quiz')
            else:
                return redirect('quiz_instructor')
        else:
            quiz = QuestionForm(instance=quiz)
    return render(request, 'edit_question.html', {'quiz': quiz})


def add_choice(request):
    if request.method == 'POST':
        form = ChoiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            if request.user.is_superuser:
                return redirect('quiz')
            else:
                return redirect('quiz_instructor')
    else:
        quiz = ChoiceForm()
    return render(request, 'add_choice.html', {'quiz': quiz})


def edit_choice(request, choice_id):
    choice = get_object_or_404(Choice, id=choice_id)
    if request.method == 'POST':
        form = ChoiceForm(request.POST, request.FILES, instance=choice)
        if form.is_valid():
            form.save()
            if request.user.is_superuser:
                return redirect('quiz')
            else:
                return redirect('quiz_instructor')
        else:
            choice = ChoiceForm(instance=choice)
    return render(request, 'edit_choice.html', {'choice': choice})


def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.delete()
    if request.user.is_superuser:
        return redirect('quiz')
    else:
        return redirect('quiz_instructor')


def delete_question(request, question_id):
    quiz = get_object_or_404(Question, id=question_id)
    quiz.delete()
    if request.user.is_superuser:
        return redirect('quiz')
    else:
        return redirect('quiz_instructor')


def delete_choice(request, choice_id):
    quiz = get_object_or_404(Choice, id=choice_id)
    quiz.delete()
    if request.user.is_superuser:
        return redirect('quiz')
    else:
        return redirect('quiz_instructor')


def qu_attempt(request):
    ans = QuizAttempt.objects.all()
    use = UserAnswer.objects.all()
    return render(request, 'qu_attempt.html', {'ans': ans, 'use': use})


def add_attempt(request):
    if request.method == 'POST':
        form = QuizAttemptForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('qu_attempt')
    ans = QuizAttemptForm()
    return render(request, 'add_attempt.html', {'ans': ans})


def add_use(request):
    if request.method == 'POST':
        form = UserAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('qu_attempt')
    use = UserAnswerForm
    return render(request, 'add_use.html', {'use': use})


def delete_attempt(request, attempt_id):
    ans = get_object_or_404(QuizAttempt, id=attempt_id)
    ans.delete()
    return redirect('qu_attempt')


def delete_use(request, use_id):
    use = get_object_or_404(UserAnswer, id=use_id)
    use.delete()
    return redirect('qu_attempt')


def course_detail(request):
    detail = CourseDetail.objects.all()
    return render(request, 'detail.html', {'detail': detail})


def add_detail(request):
    if request.method == 'POST':
        form = CourseDetailForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('course_detail')
    detail = CourseDetailForm()
    return render(request, 'add_detail.html', {'detail': detail})


def edit_detail(request, detail_id):
    detail = get_object_or_404(CourseDetail, id=detail_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=detail)
        if form.is_valid():
            form.save()
            return redirect('course_detail')
    detail = CourseDetailForm(instance=detail)
    return render(request, 'edit_detail.html', {'detail': detail})


def delete_detail(request, detail_id):
    detail = get_object_or_404(UserAnswer, id=detail_id)
    detail.delete()
    return redirect('course_detail')


def certification(request):
    cert = Certificate.objects.all()
    return render(request, 'certificate.html', {'cert': cert})


def add_certificate(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('certification')
    cert = CertificateForm()
    return render(request, 'add_certificate.html', {'cert': cert})


def edit_certificate(request, certificate_id):
    cert = get_object_or_404(Certificate, id=certificate_id)
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES, instance=cert)
        if form.is_valid():
            form.save()
            return redirect('certification')
    cert = CertificateForm(instance=cert)
    return render(request, 'edit_certificate.html', {'cert': cert})


def delete_certificate(request, certificate_id):
    cert = get_object_or_404(Certificate, id=certificate_id)
    cert.delete()
    return redirect('certification')


def quiz_instructor(request):
    quiz = Quiz.objects.all()
    question = Question.objects.all()
    choice = Choice.objects.all()

    context = {
        'quiz': quiz,
        'question': question,
        'choice': choice,
    }
    return render(request, 'quiz_instructor.html', context)


def quiz_st(request):
    ans = QuizAttempt.objects.all()
    use = UserAnswer.objects.all()
    return render(request, 'quiz_st.html', {'ans': ans, 'use': use})


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def search_courses(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Course.objects.filter(title__icontains=query)

    return render(request, 'search_result.html', {
        'query': query,
        'results': results,
    })


def sorted_course(request):
    sort_by = request.GET.get('sort','title')
    valid_sort_fields = ['title','price','created_at']

    if sort_by not in valid_sort_fields:
        sort_by = 'title'

    courses = Course.objects.all().order_by(sort_by)

    return render(request, 'sorted_courses.html',{
        'courses': courses,
        'sort_by': sort_by,
    })