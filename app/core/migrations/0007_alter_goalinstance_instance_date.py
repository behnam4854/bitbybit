# Generated by Django 4.2.21 on 2025-06-07 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_goal_next_occurrence'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goalinstance',
            name='instance_date',
            field=models.DateField(auto_now=True),
        ),
    ]
