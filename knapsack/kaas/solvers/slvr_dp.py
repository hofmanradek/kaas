from functools import lru_cache
from kaas.solvers.slvr_base import SolverBase


class SolverDynamicRecurrent(SolverBase):
    """
    Solver class for Greedy algorithm
    """

    def solve(self, lru_cache_maxsize=None):
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
                self.knapsack.append(item.name)
                self.tvalue += item.value
                self.tweight += item.weight

