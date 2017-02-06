import unittest
import os

from kaas.solvers.datastore import Datastore
from kaas.solvers.slvr_greedy import SolverGreedy


THIS_MODULE_PATH = os.path.dirname(__file__)
TEST_FILE_PATH = os.path.join(THIS_MODULE_PATH, "data", "ks_22.json")


class TestDatastore(unittest.TestCase):
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


class TestSolvers(unittest.TestCase):

    def setUp(self):
        self.ds = Datastore(sorted=True)
        self.ds.load_from_json_file(TEST_FILE_PATH)

    def tearDown(self):
        pass

    def test_greedy(self):
        "test of Greedy solver"

        sgreedy = SolverGreedy(self.ds.capacity, self.ds, fractional=False)

        #test of correct initialization
        assert sgreedy.fract == False
        assert sgreedy.ds.nitems == 22

        #test of solver
        sgreedy.solve()
        assert sgreedy.tweight == 396
        assert sgreedy.tvalue == 1030



