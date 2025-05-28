from django.urls import path

from. import views

app_name = 'account'

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('profile/', views.profile, name="profile"),
    path('goals/', views.goals, name="goals"),
    path('goal-gruops/', views.goal_groups, name="goal_groups"),

]
