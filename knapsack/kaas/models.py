from django.db import models
from jsonfield import JSONField
# Create your models here.


class KnapsackTask(models.Model):
    """
    Class representing database model for a Knapsack task
    """
    task_id = models.CharField(max_length=36)  # UUID has 36 chars
    status = models.CharField(max_length=20)
    solver_type = models.CharField(max_length=30)
    done=models.BooleanField(default=False)

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


