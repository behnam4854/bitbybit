from django.shortcuts import render


# Create your views here.
def dashboard(request):
    """simple test dashboard"""
    return render(request, "account/home_dashboard.html")


def profile(request):
    """simple test dashboard"""
    return render(request, "account/profile.html")

def goals(request):
    """simple test dashboard"""
    return render(request, "account/goals.html")

def goal_groups(request):
    """simple test dashboard"""
    return render(request, "account/goal_groups.html")
