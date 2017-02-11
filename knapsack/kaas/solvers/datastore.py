from __future__ import division
import json
from pprint import pprint


class Item(object):
    """
    Class representing a single Knapsack item
    """
    def __init__(self, value, weight, index=None, name=""):
        self.name = name
        self.value = value
        self.weight = weight
        self.density = self.val_density()
        self.index = index

    def val_density(self):
        "returns value density of item"
        try:
            return self.value/self.weight
        except ZeroDivisionError:
            return 0

    def to_json(self):
        return {'value': self.value,
                'weight': self.weight,
                'index': self.index,
                'name': self.name
                }


class Datastore(object):
    """
    Class representing uniresal datastore for all Knapsack solvers
    """
    def __init__(self, sorted=False):
        self.nitems = 0.  # number of items
        self.capacity = 0.  # maximum capacity of Knapsack
        self.items = None
        self.sorted = sorted

    @staticmethod
    def sort_by_value_density(items):
        """
        Sorts items by value density in decreasing order (suitable for geedy and b&b solvers)
        :param items: list of Item objects
        :return: sotred list according to item.density
        """
        return sorted(items, key=lambda x: x.density, reverse=True)

    def set_sorted(self):
        self.sorted = True
        self.items = self.sort_by_value_density(self.items)

    def load_from_json(self, data_json):
        """
        loads data from json
        sample:
            {
                "num_items": 2,
                "capacity": 6,
                "items": [
                    {
                        "index": 0,
                        "value": 8,
                        "weight": 4
                    },
                    {
                        "index": 1,
                        "value": 10,
                        "weight": 5
                    }
                ]
            }
        :param data_json: json with items
        :return:
        """
        self.nitems = data_json['num_items']
        self.capacity = data_json['capacity']
        self.items = []

        for item in data_json['items']:
            name = item.get('name', "")
            self.items.append(Item(item['value'], item['weight'], item['index'], name))

        if self.sorted:
            self.set_sorted()

    def load_from_json_str(self, s):
        """
        loads data from json string
        :param s: string with json
        :return:
        """
        self.load_from_json(json.loads(s))


    def load_from_json_file(self, file_path):
        """
        loads data from json string from a file
        :param file_path: path to json file
        :return:
        """
        with open(file_path, 'r') as f:
            s = f.read()
            self.load_from_json_str(s)

    def test_trivial_0(self):
        """
        Test on trivial solution: all items heavier than knapsack capacity
        :return: true if condition for trivial solution holds
        """
        return min([x.weight for x in self.items]) > self.capacity

    def test_trivial_1(self):
        """
        Test on trivial solution: sum of all items' weights <= capacity - all fit in
        :return: true if condition for trivial solution holds
        """
        return sum([x.weight for x in self.items]) <= self.capacity
