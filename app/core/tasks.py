from venv import logger

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import UserReminder, Goal, GoalInstance
from account.models import *

from datetime import datetime, timedelta

import logging
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY

logger = logging.getLogger(__name__)


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
            user=user,
            is_completed=False,
            due_date__lt=timezone.now().date()
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


@shared_task(queue='tasks')
def recurring_task_creation(goal_id):
    """Create GoalInstance records for a recurring goal's next occurrences."""
    try:
        goal = Goal.objects.get(id=goal_id)
        logger.debug(f"Processing recurring task for goal {goal.id}: {goal.title}")
        today = timezone.now().date()

        if not goal.is_recurring or goal.recurrence is None:
            logger.debug(f"Goal {goal.id} is not recurring or has no recurrence rule.")
            return

        # Map recurrence_rule to rrule frequency and validate
        recurrence_map = {
            'DAILY': DAILY,
            'WEEKLY': WEEKLY,
            'MONTHLY': MONTHLY
        }
        freq = recurrence_map.get(goal.recurrence)
        if not freq:
            logger.error(f"Invalid recurrence rule for goal {goal.id}: {goal.recurrence_rule}")
            return

        # Determine end date
        end_date = goal.recurrence_end if goal.recurrence_end else today + timedelta(days=365)
        if end_date < today:
            logger.debug(f"Recurrence ended for goal {goal.id} on {end_date}")
            goal.is_recurring = False
            goal.save()
            return

        # Set horizon based on recurrence type
        if goal.recurrence == 'DAILY':
            horizon = today + timedelta(days=7)
        else:
            horizon = today + timedelta(days=30)

        # Calculate instance dates
        rule = rrule(
            freq=freq,
            dtstart=today + timedelta(days=1),
            until=min(end_date, horizon)
        )

        # Create GoalInstance records, avoiding duplicates
        created_count = 0
        for instance_date in rule:
            instance_date = instance_date.date()
            if not GoalInstance.objects.filter(goal=goal, instance_date=instance_date).exists():
                GoalInstance.objects.create(
                    goal=goal,
                    instance_date=instance_date,
                    current_value=0,
                    is_completed=False
                )
                created_count += 1
                logger.debug(f"Created GoalInstance for goal {goal.id} on {instance_date}")

        # Update next_occurrence
        next_horizon = horizon + timedelta(days=1)
        next_rule = rrule(freq=freq, dtstart=next_horizon, count=1, until=end_date)
        next_dates = list(next_rule)
        goal.next_occurrence = next_dates[0].date() if next_dates else None
        goal.save()
        logger.info(f"Created {created_count} GoalInstance(s) for goal {goal.id}, next_occurrence: {goal.next_occurrence}")

    except Goal.DoesNotExist:
        logger.error(f"Goal {goal_id} does not exist.")
    except Exception as e:
        logger.error(f"Error in recurring_task_creation for goal {goal_id}: {str(e)}")
        raise

@shared_task(queue='tasks')
def process_recurring_goals():
    """Manually process recurring goals to create GoalInstance records."""
    logger.info("Starting manual recurring goal processing")
    today = timezone.now().date()
    goals = Goal.objects.filter(
        is_recurring=True,
        next_occurrence__lte=today,
        recurrence__isnull=False
    ).filter(
        models.Q(recurrence_end__gte=today) | models.Q(recurrence_end__isnull=True)
    )

    logger.debug(f"Found {goals.count()} recurring goals to process")
    for goal in goals:
        logger.debug(f"Enqueuing recurring_task_creation for goal {goal.id}: {goal.title}")
        recurring_task_creation.delay(goal.id)

    logger.info(f"Processed {goals.count()} recurring goals")
