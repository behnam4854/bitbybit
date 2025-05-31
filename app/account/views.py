from datetime import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from core.models import *
from .models import *
from django.utils.crypto import get_random_string

from .forms import *
import time

from django.conf import settings
from django.contrib import messages

from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def dashboard(request):
    """simple test dashboard"""

    goal_groups = []
    # groups = TaskGroup.objects.filter(user=request.user)
    # todo refactor the code to the currect one that filter user after editing the model
    groups = TaskGroup.objects.all()

    for group in groups:
        total_goals = group.goal_set.count()
        completed_goals = group.goal_set.filter(is_completed=True).count()

        goal_groups.append({
            'title': group.title,
            'total_goals': total_goals,
            'completed_goals': completed_goals,
            'completion_percentage': (completed_goals / total_goals * 100) if total_goals > 0 else 0
        })

    total_tasks = Goal.objects.filter(user=request.user).count()
    completed_tasks = Goal.objects.filter(is_completed=True, user=request.user).count()
    in_progress_tasks = Goal.objects.filter(is_completed=False, user=request.user, due_date__lte=datetime.now()).count()
    over_due_tasks = Goal.objects.filter(is_completed=False, user=request.user, due_date__gte=datetime.now()).count()
    return render(request, "account/home_dashboard.html", {"completed_tasks": completed_tasks,
                                                           "total_tasks": total_tasks,
                                                           "in_progress_tasks": in_progress_tasks,
                                                           "over_due_tasks": over_due_tasks,
                                                           "goal_groups": goal_groups})


def login_view(request):  # Renamed function
    """User login view"""
    if request.user.is_authenticated:
        return redirect("account:dashboard")

    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember = form.cleaned_data.get('remember', False)
            user = authenticate(request, username=email, password=password)

            if user is not None:
                if user.is_verified:
                    login(request, user)  # Use renamed auth_login
                    return redirect("account:dashboard")
                else:
                    code = get_random_string(length=6, allowed_chars='1234567890')
                    VerificationCode.objects.update_or_create(
                        user=user,
                        defaults={'code': code, 'created_at': time.time()}
                    )
                    send_mail(
                        'Your Verification Code',
                        f'Your verification code is: {code}',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    request.session["verification_user_id"] = user.id
                    return redirect("account:verification_code")
            else:
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Form is invalid")

    return render(request, "account/login.html", {"form": form})


def signup_view(request):
    """sign up view"""
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            if password == confirm_password:
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=name,
                )
                code = get_random_string(length=6, allowed_chars='1234567890')
                VerificationCode.objects.update_or_create(
                    user=user,
                    code=code
                )
                send_mail(
                    'Your Verification Code',
                    f'Your verification code is: {code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

                request.session['verification_user_id'] = user.id
                messages.success(request, 'Account created! Please verify your email')
                return redirect("account:verification_code")
            else:
                messages.error(request, "Passwords does not match")
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Form is invalid")
    return render(request, "account/login.html", {"form": form})


def verification(request):
    """Email verification view"""
    user_id = request.session.get("verification_user_id")
    if not user_id:
        return redirect("account:login_view")  # Update redirect

    try:
        user = User.objects.get(id=user_id)
        verification_code = VerificationCode.objects.get(user=user)
    except (User.DoesNotExist, VerificationCode.DoesNotExist):
        messages.error(request, "Invalid verification session")
        return redirect("account:login_view")

    if request.method == 'POST':
        submitted_code = ''.join([
            request.POST.get('digit1', ''),
            request.POST.get('digit2', ''),
            request.POST.get('digit3', ''),
            request.POST.get('digit4', ''),
            request.POST.get('digit5', ''),
            request.POST.get('digit6', ''),
        ])

        if submitted_code == verification_code.code:
            if time.time() - verification_code.created_at <= 300:
                user.is_verified = True
                user.save()
                verification_code.delete()
                del request.session["verification_user_id"]
                login(request, user)
                return redirect("account:dashboard")
            else:
                messages.error(request, "The verification code has expired")
        else:
            messages.error(request, "The verification code is invalid")

    context = {
        'email': user.email,
        'verification_sent_at': verification_code.created_at,
    }
    return render(request, "account/verification_code.html", context)


def profile(request):
    """simple test dashboard"""
    return render(request, "account/profile.html")


def goals(request):
    """simple test dashboard"""
    return render(request, "account/goals.html")


def goal_groups(request):
    """simple test dashboard"""
    return render(request, "account/goal_groups.html")
