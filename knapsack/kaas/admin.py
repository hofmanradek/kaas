from django.contrib import admin
from kaas.models import KnapsackTask
# Register your models here.

@admin.register(KnapsackTask)
class MetaResolvedAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'user', 'status', \
                    'capacity', 'nitems', 'result_weight', 'result_value', 'task_created', 'task_total_duration')
    list_filter = ('task_id', 'status', 'user', 'task_created')


