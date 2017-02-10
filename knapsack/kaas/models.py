from django.db import models
from jsonfield import JSONField
from django.contrib.auth.models import User
from datetime import timedelta

#let's generate token for each new user
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class KnapsackTask(models.Model):
    """
    Class representing database model for a Knapsack task
    """
    task_id = models.CharField(max_length=36, blank=True)  # celery task id is UUID and has 36 chars
    status = models.CharField(max_length=20, default='CREATED')  # 'CREATED' -> 'INITIALIZING' -> 'SOLVING' -> `SUCCESS`/`FAILURE`
    solver_type = models.CharField(max_length=30, blank=True)  # string identificator of solver types
    done = models.BooleanField(default=False)  # taks solution ended, does not mean with SUCCESS
    user = models.ForeignKey(User, related_name="tasks_of_user")  # task owner
    task_created = models.DateTimeField(auto_now_add=True)  # time when user creates the task via web or API
    task_solve_start = models.DateTimeField(blank=True, null=True)  # start of 'INITIALIZING'
    task_solve_end = models.DateTimeField(blank=True, null=True)  # end of 'SOLVING'
    task_total_duration = models.DurationField(default=timedelta(seconds=0.))  # overall time including queuing
    task_solution_duration = models.DurationField(default=timedelta(seconds=0.))  # timedelta from 'INITIALIZING' to end of 'SOLVING'

    #if task fails (to know what happened)
    #exception fileds are filled only if task ends with 'FAILURE', empty otherwise
    exception_class = models.TextField(blank=True)
    exception_msg = models.TextField(blank=True)
    exception_traceback = models.TextField(blank=True)

    #inputs to our tasks
    input = JSONField(default="{}")
    capacity = models.FloatField(default=0.)
    nitems = models.IntegerField(default=0)

    #output - only if taks ends with 'SUCCESS' and returns, empty otherwise
    result_weight = models.FloatField(default=0.)
    result_value = models.FloatField(default=0.)
    result_items = JSONField(blank=True)



