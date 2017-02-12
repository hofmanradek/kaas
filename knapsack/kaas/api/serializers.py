from rest_framework import serializers

from kaas.models import KnapsackTask


class KnapsackTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for KnapsackTask model:)
     - this is a concise serializer which do not return intput and resulting items
    """
    #durations we convert to seconds
    total_duration_sec = serializers.SerializerMethodField('_tot_sol')
    solution_duration_sec = serializers.SerializerMethodField('_sol')
    user_name = serializers.SerializerMethodField('_username')

    def _tot_sol(self, obj):
        "converts task_total_duration to seconds"
        return obj.task_total_duration.total_seconds()

    def _sol(self, obj):
        "converts task_solution_duration to seconds"
        return obj.task_solution_duration.total_seconds()

    def _username(self, obj):
        "return username of task owner"
        return obj.user.username

    class Meta:
        model = KnapsackTask
        fields = ('id', 'celery_task_id', 'status', 'solver_type', 'done', 'user_name', 'task_created', \
                  'task_solve_start', 'task_solve_end', \
                  'total_duration_sec', 'solution_duration_sec', \
                  'exception_class', 'exception_msg', 'exception_traceback',
                  'capacity', 'nitems', \
                  'result_weight', 'result_value')


class KnapsackTaskDetailSerializer(KnapsackTaskSerializer):
    """
    Serializer for KnapsackTask model:)
     - full serialized for detailed information including input items and result items
    """
    #durations we convert to seconds
    class Meta:
        model = KnapsackTask
        fields = ('id', 'celery_task_id', 'status', 'solver_type', 'done', 'user_name', 'task_created', \
                  'task_solve_start', 'task_solve_end', \
                  'total_duration_sec', 'solution_duration_sec', \
                  'exception_class', 'exception_msg', 'exception_traceback',
                  'input', 'capacity', 'nitems', \
                  'result_weight', 'result_value', 'result_items')


