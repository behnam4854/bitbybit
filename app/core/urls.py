from django.urls import path

from. import views

app_name = 'core'

urlpatterns = [
    path('', views.GoalListView.as_view(), name="goal-list"),
    path('toggle-goal/<int:goal_id>', views.toggle_goal_status, name="toggle-goal-status"),
    path('delete-goal/<int:goal_id>/', views.delete_goal, name="delete-goal"),
    path('sonooze-goal/<int:goal_id>', views.snooze_goal, name="snooze-goal"),
]
