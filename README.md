# Kaas - Knapsack as a Service #


### Available solvers ###

Currently we have following solvers implemented:

* Greedy algorithm (both fractional and 0/1 Knapsack)
* Recurrent dynamic programming
* Branch and Bound using Greedy relaxation

### Installation ###

* `pip install -r requirements.txt`
* `python manage.py migrate`
* Currently, we have only solver tests which you can run: `python manage.py test`