# courses/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Home and course listings
    path('', views.home_redirect, name='home'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    
    # Authentication URLs
    path('accounts/login/', 
         auth_views.LoginView.as_view(template_name='registration/login.html'), 
         name='login'),
    path('accounts/logout/', 
         auth_views.LogoutView.as_view(), 
         name='logout'),
    
    # Separate registration URLs
    path('accounts/student/signup/', views.StudentSignUpView.as_view(), name='student_signup'),
    path('accounts/instructor/signup/', views.InstructorSignUpView.as_view(), name='instructor_signup'),
    
    # Separate dashboard URLs
    path('student/dashboard/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('instructor/dashboard/', views.InstructorDashboardView.as_view(), name='instructor_dashboard'),
    
    # Course URLs
    path('course/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/drop/', views.drop_course, name='drop_course'),
    path('course/create/', views.CreateCourseView.as_view(), name='create_course'),
]