from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import UserReminder, Goal


@shared_task(queue='tasks')
def send_daily_reminders():
    now = timezone.now()
    for reminder in UserReminder.objects.filter(active=True):
        user_tz = timezone.get_current_timezone()
        local_time = now.astimezone(user_tz)

        if local_time.time() >= reminder.reminder_time:
            tasks = Goal.objects.filter(
                user=reminder.user,
                is_completed=False,
                due_date=local_time.date()
            )

            send_mail(
                subject=f"Daily Tasks Reminder - {local_time.date()}",
                message="",
                html_message=render_to_string('email/daily_reminder.html', {
                    'tasks': tasks,
                    'date': local_time.date(),
                    'site_url': "bitbybit.com"
                }),
                from_email="bitbybit@gmail.coim",
                recipient_list=["behnam4854@gmail.com"],
                fail_silently=True
            )

# recipient_list=[reminder.user.email],
