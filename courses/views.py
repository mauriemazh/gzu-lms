# courses/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Course, Enrollment, UserProfile
from .utils import instructor_required, student_required

# Home page redirect based on user type
def home_redirect(request):
    """Smart redirect based on user type after login"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'instructor':
                return redirect('instructor_dashboard')
            else:
                return redirect('student_dashboard')
    return redirect('course_list')

# Public course listing
class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        return Course.objects.filter(is_published=True)

# Course detail page
class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_enrolled'] = Enrollment.objects.filter(
                student=self.request.user, 
                course=self.object
            ).exists()
        return context

# Separate Registration Views
class StudentSignUpView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/student_signup.html'
    
    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        
        # Update existing profile (created by signal)
        profile = UserProfile.objects.get(user=user)
        profile.user_type = 'student'
        profile.save()
        
        messages.success(self.request, 'Student account created successfully!')
        return redirect('student_dashboard')

class InstructorSignUpView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/instructor_signup.html'
    
    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'instructor'
        return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        
        # Update existing profile (created by signal)
        profile = UserProfile.objects.get(user=user)
        profile.user_type = 'instructor'
        profile.save()
        
        messages.success(self.request, 'Instructor account created successfully!')
        return redirect('instructor_dashboard')

# Dashboard Views
class StudentDashboardView(LoginRequiredMixin, ListView):
    template_name = 'courses/student_dashboard.html'
    context_object_name = 'enrollments'
    
    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)

class InstructorDashboardView(LoginRequiredMixin, ListView):
    template_name = 'courses/instructor_dashboard.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)

# Course Management
class CreateCourseView(LoginRequiredMixin, CreateView):
    model = Course
    template_name = 'courses/course_form.html'
    fields = ['title', 'description', 'syllabus', 'is_published']
    success_url = reverse_lazy('instructor_dashboard')
    
    def form_valid(self, form):
        form.instance.instructor = self.request.user
        messages.success(self.request, 'Course created successfully!')
        return super().form_valid(form)

# Enrollment Views
@login_required
@student_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course.')
    else:
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, f'Successfully enrolled in {course.title}')
    
    return redirect('course_detail', pk=course.id)

@login_required
@student_required
def drop_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    enrollment.delete()
    messages.success(request, f'Dropped from {course.title}')
    return redirect('student_dashboard')