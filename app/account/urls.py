from django.urls import path

from. import views

app_name = 'account'

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('profile/', views.profile, name="profile"),
    # path('goals/', views.goals, name="goals"),
    path('login/', views.login_view, name="login"),
    path('signup/', views.signup_view, name="signup"),
    path('logout/', views.logout_view, name="logout"),
    path('verification/', views.verification, name="verification_code"),
    path('goal-gruops/', views.goal_groups, name="goal_groups"),


]
