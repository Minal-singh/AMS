from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user  # Who is the current user ?
        if user.is_authenticated:
            if user.user_type == "1":  # Is it the Admin
                if modulename == "authentication.student_views":
                    return redirect(reverse("admin_home"))
            elif user.user_type == "2":  # ... or Student ?
                if (
                    modulename == "authentication.admin_views"
                    or modulename == "authentication.face_recognition_views"
                ):
                    return redirect(reverse("student_home"))
            else:  # None of the aforementioned ? Please take the user to login page
                return redirect(reverse("login"))
        else:
            if (
                request.path == reverse("home")
                or modulename == "django.contrib.auth.views"
                or request.path == reverse("login")
            ):  # If the path is homepage or login or has anything to do with authentication, pass
                pass
            else:
                return redirect(reverse("home"))
