from __future__ import absolute_import
from celery import shared_task, Task
from datetime import datetime, timezone

from kaas.solvers.slvr_greedy import SolverGreedy
from kaas.solvers.slvr_dp import SolverDynamic, SolverDynamicRecurrent
from kaas.solvers.slvr_bb import BranchAndBoundSolver
from kaas.solvers.datastore import Datastore
from kaas.models import KnapsackTask

SOLVER_TYPES = {
    'GREEDY': {'class': SolverGreedy,
               'requires_sorted': True},
    'DYN_PROG': {'class': SolverDynamic,
                 'requires_sorted': False},
    'DYN_PROG_RECURRENT': {'class': SolverDynamicRecurrent,
                     'requires_sorted': False},
    'BRANCH_AND_BOUND': {'class': BranchAndBoundSolver,
                         'requires_sorted': True}
}

SOLVER_DEFAULT = 'BRANCH_AND_BOUND'  # default solver if not provided


def task_driver(data, user):
    """
    Driver prepares task to be run and created a KnapsackTask object which will be later updated on its result
    :param data: Input data in json
    :param user: Djnago User instance of task owner
    :return: celery task result
    """
    solver_type = data.get('solver_type', SOLVER_DEFAULT)  # we have a default solver if not provided
    knapsack_data = data.get('knapsack_data')
    print(knapsack_data)
    #we created a new task in database, in task we will update it on result
    kt = KnapsackTask(
            user=user,
            solver_type=solver_type,
            input=knapsack_data['items'],
            capacity=knapsack_data['capacity'],
            nitems=knapsack_data['num_items'],
    )
    kt.save()

    #call of celery task
    result = solve_knapsack.delay(solver_type, knapsack_data, kt.id, init_kwargs={}, solve_kwargs={})

    return kt.id, result


class LogTaskResult(Task):
    """
    Class implementing callbacks (mainly results persisting) for our celery task
    """
    def on_failure(self, exc, celery_task_id, args, kwargs, einfo):
        """
        What to do on celery task failure
        :param exc: The exception raised by the task.
        :param celery_task_id: Unique id of the failed task.
        :param args: Original arguments for the task that failed.
        :param kwargs: Original keyword arguments for the task that failed.
        :param einfo: ExceptionInfo instance, containing the traceback.
        :return:
        """
        kt_id = args[2]
        #update on FAILURE status
        kt = KnapsackTask.objects.get(id=kt_id)
        kt.celery_task_id = celery_task_id
        kt.status = 'FAILURE'
        kt.done = True
        kt.exception_class = exc.__class__.__name__
        kt.exception_msg = str(exc).strip()
        kt.exception_traceback = str(einfo).strip()
        kt.task_total_duration = datetime.now(timezone.utc) - kt.task_created  # just approximate value - time to failure:)
        kt.save()


    def on_success(self, retval, celery_task_id, args, kwargs):
        """
        What to do on celery task success
        :param retval: The return value of the task (v, w, its['items'], solution_start, solution_end).
        :param task_id: Unique id of the executed task.
        :param args: Original arguments for the executed task.
        :param kwargs: Original keyword arguments for the executed task.
        :return:
        """
        kt_id = args[2]
        #update in SUCCESS status
        kt = KnapsackTask.objects.get(id=kt_id)
        kt.celery_task_id = celery_task_id
        kt.status = 'SUCCESS'
        kt.done = True
        kt.result_value = retval[0]
        kt.result_weight = retval[1]
        kt.result_items = retval[2]
        kt.task_solve_start = retval[3]
        kt.task_solve_end = retval[4]
        kt.task_solution_duration = retval[4] - retval[3]
        kt.task_total_duration = retval[4] - kt.task_created
        kt.save()


@shared_task(base=LogTaskResult, bind=True, name='Knapsack problem', queue="knapsack_solvers")
def solve_knapsack(self, solver_type, knapsack_data, kt_id, init_kwargs={}, solve_kwargs={}):
    """
    Celery task to solve Knapsack problem
    :param solver_type: string identified of solver type
    :param knapsack_data: json with knapsack data, described in Datastore class
    :param kt_id: id of KnapsackTask in database
    :param init_kwargs:  additional params that can be passed to solver constructor, e.g. fractional option
    :param solve_kwargs: additinoal params that can be passed to solve() method, e.g. offsets
    :return: total value and weight of knapsack items
    """
    solution_start = datetime.now(timezone.utc)
    self.update_state(state='INITIALIZING')

    #construction of datastore
    #requires this solver sorted items by their value density?
    requires_sorted = SOLVER_TYPES[solver_type]['requires_sorted']
    #instantiate a datastore
    ds = Datastore(sorted=requires_sorted)
    ds.load_from_json(knapsack_data)

    #construction of solver
    solver_class = SOLVER_TYPES[solver_type]['class']
    solver = solver_class(ds, **init_kwargs)

    self.update_state(state='SOLVING')

    solver.solve()
    v = solver.tvalue
    w = solver.tweight
    its = solver.get_item_json()
    solution_end = datetime.now(timezone.utc)
    return v, w, its['items'], solution_start, solution_end

