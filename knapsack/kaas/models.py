from django.db import models
from jsonfield import JSONField
from django.contrib.auth.models import User
# Create your models here.

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
    status = models.CharField(max_length=20, default='SUBMITTED')
    solver_type = models.CharField(max_length=30, blank=True)
    done = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name="tasks_of_user")

    #if task fails (to know what happened)
    exception_class = models.TextField(blank=True)
    exception_msg = models.TextField(blank=True)
    exception_traceback = models.TextField(blank=True)

    #input
    input = JSONField(default="{}")
    capacity = models.FloatField(default=0.)
    nitems = models.IntegerField(default=0)

    #output
    result_weight = models.FloatField(default=0.)
    result_value = models.FloatField(default=0.)
    result_items = JSONField(blank=True)


