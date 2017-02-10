from django.test import TestCase
import os

from kaas.solvers.datastore import Datastore
from kaas.solvers.slvr_greedy import SolverGreedy
from kaas.solvers.slvr_dp import SolverDynamicRecurrent, SolverDynamic
from kaas.solvers.slvr_bb import BranchAndBoundSolver

THIS_MODULE_PATH = os.path.dirname(__file__)
TEST_FILE_PATH = os.path.join(THIS_MODULE_PATH, "data", "ks_22.json")


class TestDatastore(TestCase):
    """
    Tests for datastore module
    """

    def test_datastore_load_json(self):
        ds = Datastore(sorted=True)
        ds.load_from_json_file(TEST_FILE_PATH)

        assert ds.nitems == 22
        assert ds.capacity == 400
        assert len(ds.items) == ds.nitems

        #test of items sorting
        #highest
        assert ds.items[0].value == 150
        assert ds.items[0].weight == 9
        assert ds.items[0].density == 50/3
        #lowest
        assert ds.items[ds.nitems-1].value == 10
        assert ds.items[ds.nitems-1].weight == 52
        assert ds.items[ds.nitems-1].density == 5/26


class TestSolvers(TestCase):
    """
    Test for all availbale solvers
    """
    def setUp(self):
        self.ds = Datastore(sorted=True)
        self.ds.load_from_json_file(TEST_FILE_PATH)

    def tearDown(self):
        pass

    def test_greedy_non_fractional(self):
        "test of Greedy solver - non fractional version (0/1 Knapsack)"

        sgreedy = SolverGreedy(self.ds, fractional=False)

        #test of correct initialization
        assert sgreedy.fract == False
        assert sgreedy.ds.nitems == 22

        #test of solver
        sgreedy.solve()
        assert sgreedy.tweight == 396
        assert sgreedy.tvalue == 1030

    def test_greedy_fractional(self):
        "test of Greedy solver - fractional version"

        sgreedy = SolverGreedy(self.ds, fractional=True)

        #test of correct initialization
        assert sgreedy.fract == True
        assert sgreedy.ds.nitems == 22

        #test of solver
        sgreedy.solve()
        assert sgreedy.tweight == 400
        assert sgreedy.tvalue == 1035.2173913043478

    def test_dynamic_programming(self):
        "test of dynamic programming solver"

        sdpr = SolverDynamic(self.ds)

        #test of correct initialization
        assert sdpr.ds.nitems == 22

        #test of solver
        sdpr.solve()
        assert sdpr.tweight == 396
        assert sdpr.tvalue == 1030

    def test_recurrent_dynamic_programming(self):
        "test of dynamic programming solver"

        sdpr = SolverDynamicRecurrent(self.ds)

        #test of correct initialization
        assert sdpr.ds.nitems == 22

        #test of solver
        sdpr.solve(lru_cache_maxsize=None)
        assert sdpr.tweight == 396
        assert sdpr.tvalue == 1030

    def test_branch_and_bound(self):
        "test of Branch&Bound implementation using fractional Greedy relaxation"

        sbb = BranchAndBoundSolver(self.ds)

        #test of correct initialization
        assert sbb.ds.nitems == 22

        #test of solver
        sbb.solve()
        assert sbb.tweight == 396
        assert sbb.tvalue == 1030


