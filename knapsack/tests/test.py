from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
import os

from kaas.solvers.datastore import Datastore
from kaas.solvers.slvr_greedy import SolverGreedy
from kaas.solvers.slvr_dp import SolverDynamicRecurrent, SolverDynamic
from kaas.solvers.slvr_bb import BranchAndBoundSolver
from kaas.models import KnapsackTask

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


class TestApi(TestCase):
    """
    Tests for our API
    """
    #following fixtures will be loaded before tests
    fixtures = ['test_fixture.json']

    def setUp(self):
        #we prepare two client to test our security policies
        #authorized client
        self.client_authorized = APIClient(user__username='tester')
        token = Token.objects.get(user__username='tester')
        self.client_authorized.credentials(HTTP_AUTHORIZATION='Token '+ token.key)
        #unauthorized client
        self.client_unauthorized = APIClient()

    def tearDown(self):
        pass

    def test_api_task_list_get(self):
        """
        test of GET
        """
        url = reverse('api_task_list')
        response = self.client_authorized.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_json = response.json()
        self.assertEqual(len(res_json), 2)  # tester has 2 tasks in fixture

        #unauthorized user
        response = self.client_unauthorized.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_task_list_post(self):
        """
        test of POST
        """
        url = reverse('api_task_list')
        data={"solver_type": "BRANCH_AND_BOUND", "knapsack_data": { "num_items": 2, "capacity": 10, "items": [ { "index": 0, "value": 8, "weight": 4 }, { "index": 1, "value": 10, "weight": 5 } ] } }
        response = self.client_authorized.post(url, format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        res_json = response.json()
        self.assertTrue('id' in res_json.keys())
        self.assertTrue('celery_task_id' in res_json.keys())

        #unauthorized user
        response = self.client_unauthorized.post(url, format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_task_detail_get(self):
        """
        test of GET
        """
        task = KnapsackTask.objects.all()[0]
        test_id = task.id
        url = reverse('api_task_detail', args=(test_id,))
        response = self.client_authorized.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_json = response.json()
        #lets try some property...
        self.assertEqual(res_json['celery_task_id'], task.celery_task_id)

        #unauthorized user
        response = self.client_unauthorized.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_task_detail_delete(self):
        """
        test of DELETE
        """
        task = KnapsackTask.objects.all()[0]
        test_id = task.id
        url = reverse('api_task_detail', args=(test_id,))

        #unauthorized user first - will not succeed
        response = self.client_unauthorized.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        #authorized will succeed
        response = self.client_authorized.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        #we make sure it is not there
        response = self.client_authorized.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)