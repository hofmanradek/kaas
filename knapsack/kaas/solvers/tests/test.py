import unittest
from kaas.solvers.datastore import Datastore
import os

THIS_MODULE_PATH = os.path.dirname(__file__)
TEST_FILE_PATH = os.path.join(THIS_MODULE_PATH, "data", "ks_30.json")


class TestDatastore(unittest.TestCase):
    """
    Tests for datastore module
    """

    def test_datastore_load_json(self):
        ds = Datastore()
        ds.load_from_json_file(TEST_FILE_PATH)

        assert ds.nitems == 30
        assert ds.capacity == 100000
        assert len(ds.items) == ds.nitems


class TestSolvers(unittest.TestCase):

    def setUp(self):
        self.ds = Datastore()
        self.ds.load_from_json_file(TEST_FILE_PATH)

    def tearDown(self):
        pass


