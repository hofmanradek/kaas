from functools import lru_cache
import sys; sys.setrecursionlimit(10000)  # well...:)

from kaas.solvers.slvr_base import SolverBase


class SolverDynamic(SolverBase):
    """
    Solver class for Dynamic programming
    """
    def _solve(self):
        t = [[0 for i in range(self.ds.capacity+1)] for j in range(self.ds.nitems+1)]  #numpy.zeros((self.ds.nitems+1, self.ds.capacity))

        for m in range(1, self.ds.nitems+1):
            for n in range(0, self.ds.capacity+1):
                item = self.ds.items[m-1]
                if item.weight <= n:
                    t[m][n] = max(t[m-1][n], item.value+t[m-1][n-item.weight])
                else:
                    t[m][n] = t[m-1][n]

        #backward run to collect results
        n = self.ds.capacity
        for m in range(self.ds.nitems, 0, -1):
            if t[m][n] != t[m-1][n]:
                item = self.ds.items[m-1]
                n -= item.weight
                self.knapsack.append(item)
                self.tvalue += item.value
                self.tweight += item.weight


class SolverDynamicRecurrent(SolverBase):
    """
    Solver class for Dynamic programming using recurrent formula
    """
    def _solve(self, lru_cache_maxsize=None):
        """
        Recurrent Dynamic Programing (DP) solution algorithm of Knapsack problem
        :param lru_cache_maxsize: maximum number of entries store in cache (None = no limit)
        """
        @lru_cache(maxsize=lru_cache_maxsize)
        def dp(m, n):
            "recurrent function for DP"
            if m == 0:
                return 0

            item = self.ds.items[m-1]
            if item.weight <= n:
                return max( dp(m-1, n) , item.value+ dp(m-1, n-item.weight) )
            else:
                return dp(m-1, n)

        #backward run
        n = self.ds.capacity

        for m in range(self.ds.nitems, 0, -1):
            if dp(m, n) != dp(m-1, n):
                item = self.ds.items[m-1]
                n -= item.weight
                self.knapsack.append(item)
                self.tvalue += item.value
                self.tweight += item.weight

