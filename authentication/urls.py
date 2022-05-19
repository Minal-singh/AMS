from django.urls import path
from . import views, admin_views, student_views, face_recognition_views

urlpatterns = [
    # main
    path("", views.index, name="homepage"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    # admin
    path("admin/dashboard/", admin_views.index, name="admin_home"),
    path("admin/students/", admin_views.students, name="students"),
    path("admin/register-student/", admin_views.register_student, name="register_student"),
    path("admin/edit-student/<str:id>/", admin_views.edit_student, name="edit_student"),
    # face_recognition
    path(
        "admin/create-dataset/",
        face_recognition_views.create_dataset,
        name="create_dataset",
    ),
    path(
        "admin/create-dataset/<str:id>/",
        face_recognition_views.create_dataset_for_student,
        name="create_dataset_for_student",
    ),
    path("admin/train-model/", face_recognition_views.train_model, name="train_model"),
    path(
        "admin/mark-attendance/",
        face_recognition_views.mark_attendance,
        name="mark_attendance",
    ),
    # student
    path("student/dashboard/", student_views.index, name="student_home"),
]
