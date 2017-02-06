from kaas.solvers.slvr_base import SolverBase
from kaas.solvers.slvr_greedy import SolverGreedy


class BranchAndBoundSolver(SolverBase):
    """
    class of Branch and Bound Knapsack solver
    """

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
            // Returns bound of profit in subtree rooted with u.
            // This function mainly uses Greedy solution to find
            // an upper bound on maximum profit.
            :return: upper bound given by Greedy fractional solver
            """

            sgreedy = SolverGreedy(self.ds, fractional=True)
            sgreedy.solve(level=self.level, w_offset=self.cumul_weight, v_offset=self.cumul_value)
            return sgreedy.tvalue

        def go(self):
            """
            Procced to the next level from the given node
            """

            ret = []  # empty list for return values

            if (self.ds.items[self.level].weight + self.cumul_weight <= self.ds.capacity):
                item = self.ds.items[self.level]  # auxiliary variable
                ret.append(BranchAndBoundSolver.Node(item.weight + self.cumul_weight,  # we create a new left node - we take the item
                                self.level + 1,
                                item.value + self.cumul_value,
                                self.ds,
                                self.knapsack+[self.level]))

            #right child we create always - we try to omit the item
            ret.append(BranchAndBoundSolver.Node(self.cumul_weight, self.level + 1, \
                                                 self.cumul_value, self.ds, self.knapsack))
            return ret

    def solve(self):
        root = self.Node(0, 0, 0,self.ds, [])
        current_node = root
        nodes_to_go = []

        while current_node.level < self.ds.nitems:
            new_nodes = current_node.go()
            nodes_to_go.extend(new_nodes)
            nodes_to_go.sort(key=lambda x: x.ubound)
            current_node = nodes_to_go.pop()

        self.knapsack = current_node.knapsack
        self.tweight = current_node.cumul_weight
        self.tvalue = current_node.cumul_value
