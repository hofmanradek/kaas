from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from celery.result import AsyncResult

from kaas.models import KnapsackTask
from kaas.tasks import task_driver, solve_knapsack, SOLVER_TYPES, SOLVER_DEFAULT


class SolveKnapsackAPI(APIView):
    """
    Api accepting kanpsack problems to put in Celery queue to be solved
    """
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """
        API endpoit for submitting new task
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
        :return: Celery task_id for further tracking
        """
        result = task_driver(request.data, request.user)
        return Response({'task_id': result.task_id}, status=status.HTTP_201_CREATED)


class TaskInfoAPI(APIView):
    """
    Api for celery task info
    """
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, task_id):
        """
        API endpoint for getting Celery task info
        :param request:
        :return:
        """

        c_task = AsyncResult(task_id)
        retdata = {'task_id': task_id,
                   'status': c_task.status
                   }

        if c_task.status == 'SUCCESS':
            retdata['result'] = c_task.result

        return Response(retdata, status=status.HTTP_200_OK)