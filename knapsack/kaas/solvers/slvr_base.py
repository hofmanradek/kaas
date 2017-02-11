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

    def run(self, *args, **kwargs):
        """
        auxiliary function performing tests on trivial solutions and solution
        :return:
        """
        if self.ds.test_trivial_0():
            pass  # both self.tvalue and self.tweight are zero
        elif self.ds.test_trivial_1():  # all items fit in
            self.tvalue = sum([x.value for x in self.ds.items])
            self.tweight = sum([x.weight for x in self.ds.items])
        else:  # non-trivial solution - we have to find it
            self._solve(*args, **kwargs)

    @abstractmethod
    def _solve(self):
        """
        this method must be implemented for various solver types
        saves total value of items in self.tvalue, total weight in
        self.tweight ans selected items in self.knapsack
        """

    def get_items_indices(self):
        "provides list of items in the knapsack"
        return [i.index for i in self.knapsack]

    def get_total_value(self):
        "return overall value of included items"
        return sum([i.value for i in self.knapsack])

    def get_total_weight(self):
        "returns overall weight of included items"
        return sum([i.weight for i in self.knapsack])

    def get_item_json(self):
        "retuns resulting items in json format"
        return {'items': [i.to_json() for i in self.knapsack]}