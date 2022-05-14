from django.urls import path
from . import views,admin_views,student_views

urlpatterns = [
    #main
    path("",views.index,name="homepage"),
    path("login/",views.login_user,name="login"),

    #admin
    path("admin/dashboard/",admin_views.index,name="admin_home"),
    path("admin/register-student/",admin_views.register_student,name="register_student"),

    #student
    path("student/dashboard/",student_views.index,name="student_home")
]