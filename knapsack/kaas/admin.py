from django.contrib import admin
from kaas.models import KnapsackTask
# Register your models here.

@admin.register(KnapsackTask)
class MetaResolvedAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'user', 'status', 'exception_class', 'exception_msg',\
                    'capacity', 'nitems', 'result_weight', 'result_value')
    list_filter = ('task_id', 'status', 'user')


