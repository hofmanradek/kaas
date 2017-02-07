from __future__ import absolute_import
from celery import shared_task, Task

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


class LogTaskResult(Task):
    """
    Class implementing callbacks (mainly results persisting) for our celery task
    """
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        What to do on celery task failure
        :param exc: The exception raised by the task.
        :param task_id: Unique id of the failed task.
        :param args: Original arguments for the task that failed.
        :param kwargs: Original keyword arguments for the task that failed.
        :param einfo: ExceptionInfo instance, containing the traceback.
        :return:
        """
        input_data = args[1]

        kt = KnapsackTask(task_id=task_id,
                          status='FAILURE',
                          done=True,
                          solver_type=args[0],
                          exception_class=exc.__class__.__name__,
                          exception_msg=str(exc).strip(),
                          exception_traceback=str(einfo).strip(),
                          input=input_data['items'],
                          capacity=input_data['capacity'],
                          nitems=input_data['num_items'],
                          )
        kt.save()


    def on_success(self, retval, task_id, args, kwargs):
        """
        What to do on celery task success
        :param retval: The return value of the task.
        :param task_id: Unique id of the executed task.
        :param args: Original arguments for the executed task.
        :param kwargs: Original keyword arguments for the executed task.
        :return:
        """
        input_data = args[1]

        kt = KnapsackTask(task_id=task_id,
                          status='SUCCESS',
                          done=True,
                          solver_type=args[0],
                          input=input_data['items'],
                          capacity=input_data['capacity'],
                          nitems=input_data['num_items'],
                          result_value=retval[0],
                          result_weight=retval[1],
                          result_items=retval[2]
                          )
        kt.save()


@shared_task(base=LogTaskResult, bind=True, name='Knapsack problem', queue="knapsack_solvers")
def solve_knapsack(self, solver_type, knapsack_data, init_kwargs={}, solve_kwargs={}):
    """
    Celery task to solve Knapsack problem
    :param solver_type: string identified of solver type
    :param knapsack_data: json with knapsack data, described in Datastore class
    :param init_kwargs:  additional params that can be passed to solver constructor, e.g. fractional option
    :param solve_kwargs: additinoal params that can be passed to solve() method, e.g. offsets
    :return: total value and weight of knapsack items
    """
    self.update_state(state='PREPARING')

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
    return v, w, its

