from kaas.solvers.slvr_base import SolverBase
from kaas.solvers.slvr_greedy import SolverGreedy


class BranchAndBoundSolver(SolverBase):
    """
    class of Branch and Bound Knapsack solver
    """
    def __init__(self, *args, **kwargs):
        "this solver takes more inputs than the rest, we have to extend constructor"
        super(self.__class__, self).__init__(*args, **kwargs)

        if not self.ds.sorted:  # this solver requires sorted items
            self.ds.set_sorted()

    class Node(object):
        """
        Class of node of the tree built during Branch&Bound solution
        """
        def __init__(self, weight, level, value, datastore, knapsack):
            self.cumul_weight = weight
            self.cumul_value = value
            self.level = level
            self.ds = datastore
            self.ubound = self._upper_bound()
            self.knapsack = knapsack

        def _upper_bound(self):
            """
            This function uses fractional Greedy solver to find
            an upper bound on maximum profit.
            :return: upper bound given by Greedy fractional solver
            """
            sgreedy = SolverGreedy(self.ds, fractional=True)
            sgreedy.run(level=self.level, w_offset=self.cumul_weight, v_offset=self.cumul_value)
            return sgreedy.tvalue

        def go(self):
            """
            Procced to the next level from the given node
            """
            ret = []  # empty list for return values

            if self.level < self.ds.nitems:
                if (self.ds.items[self.level].weight + self.cumul_weight <= self.ds.capacity):
                    item = self.ds.items[self.level]  # auxiliary variable
                    ret.append(BranchAndBoundSolver.Node(item.weight + self.cumul_weight,  # we create a new left node - we take the item
                                                         self.level + 1,
                                                         item.value + self.cumul_value,
                                                         self.ds,
                                                         self.knapsack+[self.ds.items[self.level]]))

                #right child we create always - we try to omit the item
                ret.append(BranchAndBoundSolver.Node(self.cumul_weight, self.level + 1, \
                                                     self.cumul_value, self.ds, self.knapsack))
            return ret

    def _solve(self, priority=False):
        q = []  # we simulate priority queue
        root = self.Node(0, 0, 0, self.ds, [])
        q.append((root.ubound, root))

        best_node = root

        while q:
            ubound, current_node = q.pop()

            if current_node.cumul_value > best_node.cumul_value:
                best_node = current_node

            new_nodes = current_node.go()

            for node in new_nodes:
                if node.ubound > best_node.cumul_value:
                    q.append((node.ubound, node))  # it puts smallest first, we have to negate to get largest:)

            q.sort(key=lambda x: x[0])  # the last one is the one with highest upper_bound


        self.knapsack = best_node.knapsack
        self.tweight = best_node.cumul_weight
        self.tvalue = best_node.cumul_value