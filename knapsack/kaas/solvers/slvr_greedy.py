from kaas.solvers.slvr_base import SolverBase


class SolverGreedy(SolverBase):
    """
    Solver class for Greedy algorithm
    """

    def __init__(self, *args, w_offset=0., v_offset=0., fractional=False, **kwargs):
        "this solver takes more inputs than the rest, we have to extend constructor"

        super(self.__class__, self).__init__(*args, **kwargs)

        self.fract = fractional  # do we assume fractional Greegy? (good for relaxation in Branc and Bound)

        if not self.ds.sorted:
            raise("not sorted datastore")

    def solve(self, level=0, w_offset=0., v_offset=0.):
        """
        Greedy solution algorithm of Knapsack problem
         - we can use it as a relaxation approximation in Brand and Bound
          if more parameterized
        :param level: from which level to start
        :param w_offset: offset on overall weight
        :param v_offset: offset on overall value
        :return:
        """

        self.tweight = w_offset
        self.tvalue = v_offset

        for item in self.ds.items[level:]:
            if self.tweight + item.weight <= self.ds.capacity:
                self.knapsack.append(item)
                self.tweight += item.weight
                self.tvalue += item.value

            elif self.fract:  # we do fractional Greedy optimization
                self.knapsack.append(item)
                fraction = (self.ds.capacity - self.tweight)/item.weight
                self.tvalue += fraction*item.value
                self.tweight = self.ds.capacity
                break

