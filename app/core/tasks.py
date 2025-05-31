from venv import logger

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import UserReminder, Goal
from account.models import *



@shared_task(queue='tasks')
def send_daily_reminders():
    """for sending daily reminders"""
    now = timezone.now()
    for reminder in UserReminder.objects.filter(active=True).select_related('user'):
        try:
            user_tz = timezone.get_current_timezone()
            local_time = now.astimezone(user_tz)
            # Check if we should send the reminder
            if not should_send_reminder(reminder, local_time):
                continue
            tasks = Goal.objects.filter(
                user=reminder.user,
                is_completed=False,
                due_date__lte=local_time.date()
            )
            send_reminder_email(reminder.user, tasks, local_time)

            # Update last sent time (UTC time)
            reminder.last_sent = now
            reminder.save()

        except Exception as e:
            # Log error and continue with other users
            logger.error(f"Error sending reminder to {reminder.user.email}: {str(e)}")
            continue


def should_send_reminder(reminder, local_time):
    """check if reminder should be sent"""
    if reminder.last_sent is None:
        return True
    last_sent_local = reminder.last_sent.astimezone(local_time.tzinfo)
    # Check if we've already sent today
    if last_sent_local.date() == local_time.date():
        return False
    return local_time.time() >= reminder.reminder_time


def send_reminder_email(user, tasks, date):
    """Helper function to send email"""
    send_mail(
        subject=f"Daily Tasks Reminder - {date.strftime('%b %d')}",
        message="",
        html_message=render_to_string('email/daily_reminder.html', {
            'tasks': tasks,
            'date': date,
            'site_url': "bitbybit.com"
        }),
        from_email="bitbybit@gmail.coim",
        recipient_list=[user.email],
        fail_silently=True
    )

@shared_task(queue='tasks')
def send_priority_tasks():
    users = CustomUser.objects.all()
    for user in users:
        overdue_tasks = Goal.objects.filter(
            user= user,
            is_completed = False,
            due_date__lt = timezone.now().date()
        )

        if overdue_tasks.exists():
            send_mail(
                subject=f"🚀 Priority Tasks Need Your Attention ({overdue_tasks.count()} pending)",
                message=render_to_string('email/priority_reminder.txt',
                                         {'user': user, 'overdue_tasks': overdue_tasks}),
                html_message=render_to_string('email/priority_reminder.html',
                                              {'user': user, 'overdue_tasks': overdue_tasks}),
                from_email="BitByBit Support <support@bitbybit.com>",
                recipient_list=[user.email]
            )