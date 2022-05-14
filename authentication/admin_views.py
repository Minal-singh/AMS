from django.shortcuts import render
from validate_email import validate_email
from .utils import validate_session
from .models import Student,CustomUser

def index(request):
    return render(request,"admin_templates/index.html")


def register_student(request):

    if request.method == "GET":
        return render(request,"admin_templates/register.html")

    if request.method == "POST":
        context = {
            'data': request.POST,
            'has_error': False
        }

        # get data from form
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        first_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        profile_pic = request.FILES['profile_pic']
        roll_no = request.POST.get('roll_no')
        course = request.POST.get('course')
        branch = request.POST.get('branch')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        session = ""


        if len(password) < 6:
            messages.add_message(request, messages.ERROR,
                                 'passwords should be atleast 6 characters long')
            context['has_error'] = True

        if password != password2:
            messages.add_message(request, messages.ERROR,
                                 'passwords dont match')
            context['has_error'] = True

        if not validate_email(email):
            messages.add_message(request, messages.ERROR,
                                 'Please provide a valid email')
            context['has_error'] = True

        if validate_session(session_start_year,session_end_year):
            session = str(session_start_year)+"-"+str(session_end_year)

        else:
            messages.add_message(request, messages.ERROR,
                                 'Please provide a valid session')
            context['has_error'] = True

        try:
            if CustomUser.objects.get(email=email):
                messages.add_message(request, messages.ERROR, 'Email is taken')
                context['has_error'] = True

        except Exception as identifier:
            pass

        try:
            if Student.objects.get(roll_no=roll_no):
                messages.add_message(
                    request, messages.ERROR, 'Roll number already exists')
                context['has_error'] = True

        except Exception as identifier:
            pass
     
        # if form has validation errors retain old data
        if context['has_error']:
            return render(request, 'admin_templates/register.html', context, status=400)

        try:
            user = CustomUser.objects.create_user(email=email, password=password, user_type=3, first_name=first_name, last_name=last_name, profile_pic=profile_pic)
            user.gender = gender
            user.student.session = session
            user.student.course = course
            user.student.branch = branch
            user.save()
            messages.add_message(
                    request, messages.SUCCESS, 'Successfully added')
            return redirect(reverse('register_student'))
        
        except Exception as e:
            messages.add_message(
                    request, messages.ERROR, 'Could not add: '+str(e))