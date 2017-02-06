from __future__ import division
import json
from pprint import pprint


class Item(object):
    """
    Class representing a single Knapsack item
    """

    def __init__(self, value, weight, index=None, name=None):
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



class Datastore(object):
    """
    Class representing uniresal datastore for all Knapsack solvers
    """

    def __init__(self):
        self.nitems = 0.  # number of items
        self.capacity = 0.  # maximum capacity of Knapsack
        self.items = None

    def load_from_json(self, s):
        """
        load data from json string
        :param s: string with json
        :return:
        """
        data = json.loads(s)
        self.nitems = data['num_items']
        self.capacity = data['capacity']
        self.items = []
        for item in data['items']:
            self.items.append(Item(item['value'], item['weight'], item['index']))

    def load_from_json_file(self, file_path):
        """
        loads data from json string from a file
        :param file_path: path to json file
        :return:
        """
        with open(file_path, 'r') as f:
            s = f.read()
            self.load_from_json(s)


