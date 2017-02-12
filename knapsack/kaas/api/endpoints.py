from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from django.core.exceptions import ValidationError

from kaas.models import KnapsackTask
from kaas.tasks import task_driver, solve_knapsack, SOLVER_TYPES, SOLVER_DEFAULT
from kaas.api.serializers import KnapsackTaskSerializer, KnapsackTaskDetailSerializer
from kaas.forms import knapsack_textarea_field_validation


class KnapsackTaskListAPI(APIView):
    """
    API for list of knapsack tasks of current user (GET, POST)
      - To achieve pagination of results during GET, use ?start=S&limit=L to get slice [S:S+L]
    """
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """
        GET handler
        :param task_id: knapsack task id
        :return: serialized tasks json (newest first) and HTTP_200_OK, 404 if task not exist
        """
        try:
            start = int(request.GET['start'])
            limit = int(request.GET['limit'])
        except:
            start = 0
            limit = 10

        tasks = KnapsackTask.objects.filter(user=request.user).order_by('-task_created')[start:start+limit]
        serializer = KnapsackTaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        POST handler
        Accepts media type 'application/json' data of the following format:
        {
            "solver_type": "DYNAMIC_PROG",
            "knapsack_data": {
                "num_items": 2,
                "capacity": 6,
                "items": [
                    {
                        "index": 0,
                        "value": 8,
                        "weight": 4
                    },
                    {
                        "index": 1,
                        "value": 10,
                        "weight": 5
                    },

                ]
            }
        }
        :return: Celery task_id for further tracking and HTTP_201_CREATED if valid input,
                HTTP_400_BAD_REQUEST and reason otherwise
        """
        try:
            knapsack_textarea_field_validation(request.data)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)
        else:
            knapsack_task_id, result = task_driver(request.data, request.user)
            return Response({'id': knapsack_task_id, 'celery_task_id': result.task_id}, \
                            status=status.HTTP_201_CREATED)


class KnapsackTaskDetailAPI(APIView):
    """
    API for a single knapsack task (GET, DELETE)
    """
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, task_id):
        """
        GET handler
        :param task_id: knapsack task id
        :return: serialized task json (newest first) and HTTP_200_OK, 404 if task not exist
        """
        task = get_object_or_404(KnapsackTask, id=task_id, user=request.user)
        serializer = KnapsackTaskDetailSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, task_id):
        """
        DELETE handler
        :param task_id: knapsack task id
        :return: HTTP_204_NO_CONTENT or 404 if task not exists
        """
        task = get_object_or_404(KnapsackTask, id=task_id, user=request.user)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
