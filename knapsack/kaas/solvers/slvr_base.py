from abc import ABCMeta, abstractmethod


class SolverBase(metaclass=ABCMeta):
    """
    Base solver clase defining a common interface for all types of Knapsack solvers.
    """

    def __init__(self, datastore):
        self.ds = datastore  # datastore object with all items
        self.knapsack = []  # items included in knapsack
        self.tvalue = 0.  # total value
        self.tweight = 0.  # total weight

    @abstractmethod
    def solve(self):
        "this method must be implemented"

    def get_items_indices(self):
        "provides list of items in the knapsack"
        return [i.index for i in self.knapsack]

    def get_total_value(self):
        "return overall value of included items"
        return sum([i.value for i in self.knapsack])

    def get_total_weight(self):
        "returns overall weight of included items"
        return sum([i.weight for i in self.knapsack])