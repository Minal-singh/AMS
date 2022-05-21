from django.shortcuts import render, reverse, redirect
from django.http import HttpResponseRedirect
from validate_email import validate_email
from django.contrib import messages
from .filters import StudentFilter
from .utils import validate_session
from .models import Student, CustomUser


def index(request):
    students = Student.objects.all()
    filter = StudentFilter(request.GET, queryset=students)
    students = filter.qs
    context = {"filter": filter, "students": students}
    return render(request, "admin_templates/dashboard.html", context)


def register_student(request):
    if request.GET and request.GET.get("reset", "") == "true":
        return HttpResponseRedirect(reverse("register_student"))
    context = {}
    if request.method == "POST":
        context = {"data": request.POST, "has_error": False}
        # get data from form
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        gender = request.POST.get("gender")
        profile_pic = request.FILES.get("profile_pic", None)
        roll_no = request.POST.get("roll_no")
        course = request.POST.get("course")
        branch = request.POST.get("branch")
        session_start_year = request.POST.get("session_start_year")
        session_end_year = request.POST.get("session_end_year")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        session = ""

        if len(password) < 6:
            messages.add_message(request, messages.ERROR, "Passwords should be atleast 6 characters long")
            context["has_error"] = True

        if password != password2:
            messages.add_message(request, messages.ERROR, "Passwords dont match")
            context["has_error"] = True

        if not validate_email(email):
            messages.add_message(request, messages.ERROR, "Please provide a valid email")
            context["has_error"] = True

        if validate_session(session_start_year, session_end_year):
            session = str(session_start_year) + "-" + str(session_end_year)

        else:
            messages.add_message(request, messages.ERROR, "Please provide a valid session")
            context["has_error"] = True

        try:
            if CustomUser.objects.get(email=email):
                messages.add_message(request, messages.ERROR, "Email is taken")
                context["has_error"] = True

        except Exception:
            pass

        try:
            if Student.objects.get(roll_no=roll_no):
                messages.add_message(request, messages.ERROR, "Roll number already exists")
                context["has_error"] = True

        except Exception:
            pass

        # if form has validation errors retain old data
        if context["has_error"]:
            return render(request, "admin_templates/register.html", context, status=400)

        try:
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                user_type=2,
                first_name=first_name,
                last_name=last_name,
            )
            if profile_pic is not None:
                user.profile_pic = profile_pic
            user.gender = gender
            user.student.session = session
            user.student.roll_no = roll_no
            user.student.course = course
            user.student.branch = branch
            user.save()
            messages.add_message(request, messages.SUCCESS, "Successfully added")
            return redirect(reverse("register_student"))

        except Exception as e:
            messages.add_message(request, messages.ERROR, "Could not add: " + str(e))

    return render(request, "admin_templates/register.html", context)


def students(request):
    students = Student.objects.all()
    context = {"students": students}
    return render(request, "admin_templates/students.html", context)


def edit_student(request, id):
    data = Student.objects.get(user_id=id)
    context = {"data": data}
    return render(request, "admin_templates/edit_student_details.html", context)
