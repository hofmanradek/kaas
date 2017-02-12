![knapsack fig](https://upload.wikimedia.org/wikipedia/commons/f/fd/Knapsack.svg)

# KaaS - Knapsack as s Service #

Author: Radek Hofman, *radek@hofman.xyz*


## Introduction ##

KaaS is a simple service offering both web interface and a REST API for solving [0/1 Knapsack problem](https://en.wikipedia.org/wiki/Knapsack_problem). Knapsack problem models various practical problems including distribution of indivisible resources, choice of projects, cutting-stock problems, cryptography, financial decisions and many more.

### Implementation ###

KaaS is a Django base application with distributed task queue Celery on the backend. There are many means how to solve Knapsack problem. Our service offers following solvers which you can feed by your Knapsak problems:

*  [**Greedy approximation**](https://en.wikipedia.org/wiki/Knapsack_problem#Greedy_approximation_algorithm). This algorithm yields a suboptimal solution but it is fast and for most of real world problems it is not far from the true optimum. Internally, our Greedy solver tackles both 0/1 and fractional Knapsack and we use it in our other solver Branch and Bound to get an upper bound for the optimal value of the original
problem
* [**Dynamic Programming**](https://en.wikipedia.org/wiki/Knapsack_problem#Dynamic_programming_in-advance_algorithm) in a classical and recurrent versions. This algorithm provides optimal solution. It can be used only for problems with integer weights and for problems with large knapsack capacity or large number of items becomes computationally prohibitive.
* [**Branch and Bound**](https://en.wikipedia.org/wiki/Branch_and_bound) with fractional Greedy relaxation. This algorithm provides optimal solution and works even with non-integer weights. Branch and Bound does a complete search of all possible subsets but those which are identified as worse than the current best one are neglected. This leads to a great reduction of subsets which have to evaluated. Unfortunately, it can happen that the structure of the data leads to exponential complexity, see Section **Solving Sample Knapsacks** for examples.

Each solver is represented by its *class* in `/knapsack/kaas/solvers`. All solvers are inherited from the the base *class* `SolverBase`. This class defines a common interface for all solvers a facilitates:

* ingestion of data via class `Datastore`,
* evaluation of results,
* testing of trivial cases:
	 - all items are heavier than the knapsack capacity => none fits in,
	 - sum of all items' weights is less or equal to knapsack capacity => all fit in,
* and some other infrastructure tasks common to all solvers. 

Implementation of abstract method `SolverBase._solve()` which does the knapsack solution itself is the place where the solvers differ. This method must be implemented if you decide to code your own solver.

#### Data Ingestion and Validation ####
Tasks are defined using a JSON structure. This structure is common for web and REST API interfaces. Example follows (we hope that the structure is more or less self-explanatory):

```
{"solver_type": "BRANCH_AND_BOUND",
 "knapsack_data": {
                   "num_items": 4,
                   "capacity": 10,
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
                             },
                             {
                              "index": 2,
                              "value": 15,
                              "weight": 8
                             },
                             {
                              "index": 3,
                              "value": -4,
                              "weight": 3
                             }
                            ]
                   }
}
```
String constants for available solvers are: `GREDDY`, `DYN_PROG`, `DYN_PROG_RECURRENT` and `BRANCH_AND_BOUND`.

Task structure is thoroughly validated on input via web or REST API endpoint. We tried to provide as detailed error message as possible. For example, if a user tries to submit task specified above, he/she gets following error message:

```
{
    "error": [
        "Value -4 of key 'value' of item 3 cannot be <0!"
    ]
}
``` 

#### Persisting of Results ####

KaaS supports user accounts. User must authenticate to use web and REST API interfaces. More details on user authentication can be found in dedicated sections of this document. This enables us to monitor and control usage of the application and provides us means to keep track of user accounts and tasks of respective users. All tasks are persisted in relational DB using `KnapsackTask` DB model reflecting task structure above plus additional information including:

* celery_task_id
* User: Django User object
* status (`CRATED`, `SUCCESS`, `FAILURE`)
* task inputs and outputs: `solver_type`, `inputs`, `results` if `status` == `SUCCESS`
* Detail description of exception which occurred during celery execution (if `status` == `FAILURE`): 
	- `exception_class`, 
	- `exception_msg`, 
	- `exception_traceback`
* various time related attributes: 
    - `task_created`: timestamp when user created the task (either via web or API)
    - `task_solve_start`, `task_solve_end`
    - `task_total_duration`: total time spent since submission
    - `task_solution_duration`: time spent just in celery solver

More or getting results via web and API interfaces can be found in Section **User Interfaces**.

## Installation ##

#### Prerequisites: ####

Please make sure that the following prerequisites are met before you proceed to KaaS installation:

* [RabbitMQ](https://www.rabbitmq.com/)
* [Python3](https://www.python.org/downloads/)
* Python [pip](https://pip.pypa.io/en/stable/installing/)
* Python [virtualenv](https://virtualenv.pypa.io/en/stable/)
* [git](https://git-scm.com/)

#### Installation: ####

* Clone code from repository: `git clone https://radekhofman@bitbucket.org/radekhofman/kaas.git`
* In the project folder (or elsewhere where it is convenient for you) create a new Python3 based virualenv: `virtualenv env -p python3`
* Activate viartual env: `source env/bin/activate`
* Install all Python packages required by the project. In the project root (`kaas/knapsack/`) execute `pip install -r requirements.txt`
* Do database migration: `python manage.py migrate`
* Now you can start Django server which provides web and REST API interfaces: `python manage.py runserver`. Output should be as follows (depending on your terminal type):

```
(env)➜  knapsack git:(master) ✗ python manage.py runserver
Performing system checks...

System check identified no issues (0 silenced).
February 12, 2017 - 20:41:15
Django version 1.10.5, using settings 'knapsack.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

* The last step is to start celery worker which does all the heavy work:) 
     - Before you proceed please make sure your RabbitMQ server is running. Either run `rabbitmq-server` or start RabbitMQ as a service. To verify you can try [http://localhost:5672](http://localhost:5672) i your browser and the url should offer you a file to download with text `AMQP` as its content.
     - We have a dedicated celery queue called `knapsack_solvers`. In a new terminal window in KaaS project root (`kaas/knapsack/`) start a new celery worker listening on that queue using `celery worker -A knapsack -l info -Q knapsack_solvers`

```
 -------------- celery@panda.local v4.0.2 (latentcall)
---- **** ----- 
--- * ***  * -- Darwin-14.5.0-x86_64-i386-64bit 2017-02-12 20:20:46
-- * - **** --- 
- ** ---------- [config]
- ** ---------- .> app:         knapsack:0x104a33080
- ** ---------- .> transport:   amqp://guest:**@localhost:5672//
- ** ---------- .> results:     amqp://
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> knapsack_solvers exchange=knapsack_solvers(direct) key=knapsack_solvers
                

[tasks]
  . Knapsack problem
  . knapsack.celery.debug_task

[2017-02-12 20:20:46,598: INFO/MainProcess] Connected to amqp://guest:**@127.0.0.1:5672//
[2017-02-12 20:20:46,609: INFO/MainProcess] mingle: searching for neighbors
[2017-02-12 20:20:47,631: INFO/MainProcess] mingle: all alone
[2017-02-12 20:20:47,649: WARNING/MainProcess] /Users/panda/twisto/kaas/env/lib/python3.6/[2017-02-12 20:20:47,649: INFO/MainProcess] celery@panda.local ready.
```

#### Testing ####

* Yes, we have tests! It would be quite difficult without them. You can run tests as `python manage.py test`. We use `django-nose` with package `cover` to measure code test coverage. You can see that the current code test coverage is 74%.

```
(env)➜  knapsack git:(master) ✗ python manage.py test
nosetests --with-coverage --cover-package=kaas --verbosity=1
Creating test database for alias 'default'...
..........
Name                              Stmts   Miss  Cover
-----------------------------------------------------
kaas.py                               0      0   100%
kaas/admin.py                         6      6     0%
kaas/api.py                           0      0   100%
kaas/api/endpoints.py                35      2    94%
kaas/api/serializers.py              15      0   100%
kaas/forms.py                        61     20    67%
kaas/migrations/0001_initial.py      11      0   100%
kaas/migrations.py                    0      0   100%
kaas/models.py                       34     32     6%
kaas/solvers.py                       0      0   100%
kaas/solvers/datastore.py            47      2    96%
kaas/solvers/slvr_base.py            23      3    87%
kaas/solvers/slvr_bb.py              44      0   100%
kaas/solvers/slvr_dp.py              37      0   100%
kaas/solvers/slvr_greedy.py          21      1    95%
kaas/tasks.py                        59     10    83%
kaas/views.py                        54     38    30%
-----------------------------------------------------
TOTAL                               447    114    74%
----------------------------------------------------------------------
Ran 10 tests in 0.229s

OK
Destroying test database for alias 'default'...
```

## User Interfaces ##

### Web Interface ###

Locally, web interface can be assessed on `http://localhost:[PORT]/` (PORT is 8000 by default). It is a responsive web page based on Bootstrap and Django forms. 

To register and run your first Knapsack task please follow steps listed bellow:

1. Go to `http://localhost:8000` and press `Sign up today`
![Screen Shot 2017-02-12 at 23.45.17.png](https://bitbucket.org/repo/9x78dR/images/2094379485-Screen%20Shot%202017-02-12%20at%2023.45.17.png) 
2. What appears is a User creation form which you fill
![Screen Shot 2017-02-12 at 23.46.08.png](https://bitbucket.org/repo/9x78dR/images/3416623992-Screen%20Shot%202017-02-12%20at%2023.46.08.png)
3. After successful registration message use Login form to log in the app
![Screen Shot 2017-02-12 at 23.46.47.png](https://bitbucket.org/repo/9x78dR/images/2694745354-Screen%20Shot%202017-02-12%20at%2023.46.47.png)
4. After successful login you land on Dashboard which is empty until you submit a task. To do so please press `Solve knapsack` in top navigation bar and this brings you to a task submission page:
![Screen Shot 2017-02-12 at 23.52.17.png](https://bitbucket.org/repo/9x78dR/images/2842750772-Screen%20Shot%202017-02-12%20at%2023.52.17.png)
5. There are three tabs. First with the Knapsack JSON format, second with web submission form and the third with description of REST API and your personal REST API Token. Copy sample task JSON into the clipboard and go to the second tab `Web JSON input`. Paste task JSON into the text area and press `Solve`. Success message on green background should appear over the text area. **Your first knapsack task just has been submitted!**
![Screen Shot 2017-02-12 at 23.56.13.png](https://bitbucket.org/repo/9x78dR/images/1775174709-Screen%20Shot%202017-02-12%20at%2023.56.13.png)
6. Now you can go back do `Dashboard` and see that it is no empty no more. There are results of your first task. Congrats:)
![Screen Shot 2017-02-12 at 23.58.47.png](https://bitbucket.org/repo/9x78dR/images/3641525083-Screen%20Shot%202017-02-12%20at%2023.58.47.png)

### Rest API ###

REST API consists of a set of endpoints for task submission and results retrieving. 

#### API Authentication ####

All APIs are protected using using `TokenAuthentication` provided by Django Rest Framework. This means that each API call must have a user-specific Token in request header. Users can get their Tokens after registration in their web accounts. Examples of calling API with authentication Token in request header using [curl](https://curl.haxx.se/):

Task submission where task configuration is stored in the file `knapsack_file.json`:

```
curl -X POST http://127.0.0.1:8000/api/v1/tasks/ \
         -H "Content-Type: application/json" \
         -H "Authorization: Token 00a91e0adc4b814b89b2c850d419f107ce98d9ca" \
         -d @knapsack_file.json
```

Response should look like:

```
HTTP 201 Created
Allow: GET, POST, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "id": "5e79ced7-6e5c-4e4f-ae41-96a01af0ee2e",
    "celery_task_id": "6d35a51d-ea52-4f1e-84bb-85e8fb8570d1"
}
```

If the Token is not valid or provided:

```
HTTP 401 Unauthorized
Allow: GET, POST, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept
Authenticate: Token

{
    "detail": "Authentication credentials were not provided."
}
```

#### Task List Endpoint `/api/v1/tasks/` ####

This api provides a list of user tasks via GET and serves for task submission via POST.


**Request:**
 
```
GET /api/v1/tasks/
```
This endpoint provide a list of user's tasks. To achieve pagination of results use `/api/v1/tasks/?start=S&limit=L` to get slice [S:S+L] (default is [0:10] - first ten results).


In following response we see two tasks, one successful with its results and the other which failed with its error messages (this is just a simulated error:). 

This endpoint does not provide nor task input items neither a set of items selected as optimal. This can be retrieved by task detail endpoint described later.

**Response:**

```
HTTP 200 OK
Allow: GET, POST, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

[
    {
        "id": "7a616b3b-bf0f-4e4e-9620-611b02e8d95f",
        "celery_task_id": "657bc86a-d34e-433a-87be-6e4757e6b1b6",
        "status": "SUCCESS",
        "solver_type": "BRANCH_AND_BOUND",
        "done": true,
        "user_name": "radek",
        "task_created": "2017-02-11T14:01:21.310822Z",
        "task_solve_start": "2017-02-11T14:01:22.076412Z",
        "task_solve_end": "2017-02-11T14:01:22.110189Z",
        "total_duration_sec": 0.799367,
        "solution_duration_sec": 0.033777,
        "exception_class": "",
        "exception_msg": "",
        "exception_traceback": "",
        "capacity": 1.0,
        "nitems": 4,
        "result_weight": 0.0,
        "result_value": 0.0
    },
    {
        "id": "b1e08a3d-e986-48cd-9b0e-b9973d115be0",
        "celery_task_id": "cf764512-8889-413d-a662-292493f40176",
        "status": "FAILURE",
        "solver_type": "BRANCH_AND_BOUND",
        "done": true,
        "user_name": "radek",
        "task_created": "2017-02-11T20:52:31.929138Z",
        "task_solve_start": null,
        "task_solve_end": null,
        "total_duration_sec": 0.881459,
        "solution_duration_sec": 0.0,
        "exception_class": "TypeError",
        "exception_msg": "'<' not supported between instances of 'Node' and 'Node'",
        "exception_traceback": "Traceback (most recent call last):\n  File \"/Users/panda/twisto/kaas/env/lib/python3.6/site-packages/celery/app/trace.py\", line 367, in trace_task\n    R = retval = fun(*args, **kwargs)\n  File \"/Users/hofmanr/twisto/kaas/env/lib/python3.6/site-packages/celery/app/trace.py\", line 622, in __protected_call__\n    return self.run(*args, **kwargs)\n  File \"/Users/panda/twisto/kaas/knapsack/kaas/tasks.py\", line 129, in solve_knapsack\n    solver.run()\n  File \"/Users/panda/twisto/kaas/knapsack/kaas/solvers/slvr_base.py\", line 26, in run\n    self._solve(*args, **kwargs)\n  File \"/Users/hofmanr/twisto/kaas/knapsack/kaas/solvers/slvr_bb_prty.py\", line 82, in _solve\n    q.sort()\nTypeError: '<' not supported between instances of 'Node' and 'Node'",
        "capacity": 9486367.0,
        "nitems": 400,
        "result_weight": 0.0,
        "result_value": 0.0
    }
}    
```

**Request:**

```
POST /api/v1/tasks/
```

This endpoint server for submission of new task. Task JSON structure is send via post as `application/json` mime type. In the response we get `id` which the is tasks id in our database and we can use it later to retrieve task details and results. `celery_task_id` is for debugging purposes - it is Celery task id.

**Response:**

```
HTTP 201 Created
Allow: GET, POST, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "id": "fe384d5c-4f05-4f4e-a4cc-7cea3d7aa3cb",
    "celery_task_id": "512036a5-6e38-4c8d-8316-16fd286d05bf"
}
```

#### Task Detail Endpoint /api/v1/tasks/[id] ####

This endpoint offers task details given its `id` via GET and possibility to delete the task via DELETE.

**Request:**

```
GET /api/v1/tasks/7a616b3b-bf0f-4e4e-9620-611b02e8d95f/
```

What follows is a response containing all details on task given its `id` including inputs and outputs:

**Response:**

```
HTTP 200 OK
Allow: GET, DELETE, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "id": "7a616b3b-bf0f-4e4e-9620-611b02e8d95f",
    "celery_task_id": "657bc86a-d34e-433a-87be-6e4757e6b1b6",
    "status": "SUCCESS",
    "solver_type": "BRANCH_AND_BOUND",
    "done": true,
    "user_name": "radek",
    "task_created": "2017-02-11T14:01:21.310822Z",
    "task_solve_start": "2017-02-11T14:01:22.076412Z",
    "task_solve_end": "2017-02-11T14:01:22.110189Z",
    "total_duration_sec": 0.799367,
    "solution_duration_sec": 0.033777,
    "exception_class": "",
    "exception_msg": "",
    "exception_traceback": "",
    "input": [
        {
            "index": 0,
            "value": 8,
            "weight": 4
        },
        {
            "index": 1,
            "value": 10,
            "weight": 5
        },
        {
            "index": 2,
            "value": 15,
            "weight": 8
        },
        {
            "index": 3,
            "value": 4,
            "weight": 3
        }
    ],
    "capacity": 1.0,
    "nitems": 4,
    "result_weight": 0.0,
    "result_value": 0.0,
    "result_items": []
}
```

**Request:**

```
DELETE /api/v1/tasks/7a616b3b-bf0f-4e4e-9620-611b02e8d95f/
```

**Response:**

```
HTTP 204 No Content
Allow: GET, DELETE, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept
```


## Solving Sample Knapsacks ##

In this Section we provide results obtained with test data included in the project in `/tests/data/sample_inputs`. `Dynamic programming` solvers are infeasible for datasets with large knapsack capacity (because memory and computational complexity is then proportional to `nitems*capacity`). 

You can observe that Greedy suboptimal solver always found a good solution in rather short time compared to optimal solvers.

Interestingly, `Branch and Bound` solver did not finish in some reasonable type when applied to dataset `ks_200`. `ks_200` has very similar value/weight ration for all items. Due to these inputs paths in the solution graph cannot be easily pruned during searching for the optimum. In worst case, the complexity of `Branch and Bound` can be the same as of brute force complete search `2^nitems` (with this on mind we rather killed the solver after some time:).


#### Dataset ks_4 ####

dataset       | solver             | time [s] | weight | value 
------------- | ------------------ | -------- | -----: | ------ 
ks_4          | GREEDY             | 0.042073 |     9  |  18
ks_4          | DYN_PROG           | 0.039994 |     9  |  18
ks_4          | DYN_PROG_RECURRENT | 0.040615 |     9  |  18
ks_4          | BRANCH_AND_BOUD    |  0.044590|     9  |  18

#### Dataset ks_30 ####

dataset       | solver             | time [s] | weight | value 
------------- | ------------------ | -------- | ------ | ------ 
ks_30         | GREEDY             |0.026891  | 90001  | 90001
ks_30         | DYN_PROG           |1.789777  |99846   | 99798
ks_30         | DYN_PROG_RECURRENT | 0.048572 | 99846 |  99798
ks_30         | BRANCH_AND_BOUD    | 0.265175 |99846   |  99798

#### Dataset ks_50 ####

dataset       | solver             | time [s] | weight | value 
------------- | ------------------ | -------- | ------ | ------ 
ks_50         | GREEDY             |0.029264  |341012  |  142156
ks_50         | DYN_PROG           |13.484481 |341012  |  142156
ks_50         | DYN_PROG_RECURRENT | 9.523678 |341012  |  142156
ks_50         | BRANCH_AND_BOUD    | 0.031506 |341012  |  142156

#### Dataset ks_200 ####

dataset       | solver             | time [s] | weight | value 
------------- | ------------------ | -------- | ------ | ------ 
ks_200        | GREEDY             |0.040002  | 99781  | 100062
ks_200        | DYN_PROG           |12.340783 | 99993  | 100236
ks_200        | DYN_PROG_RECURRENT |0.426496  | 99993  | 100236
ks_200        | BRANCH_AND_BOUD    |  -  | - | -

#### Dataset ks_400 ####

dataset       | solver             | time [s] | weight | value 
------------- | ------------------ | -------- | ------ | ------ 
ks_400        | GREEDY             | 0.045390 | 9485926 | 3966813
ks_400        | DYN_PROG           | -        |    -    |  -
ks_400        | DYN_PROG_RECURRENT |  -       |    -    |   -
ks_400        | BRANCH_AND_BOUD    | 23.27769 | 9486360 |3967180

#### Dataset ks_1000 ####

dataset       | solver             | time [s] | weight | value 
------------- | ------------------ | -------- | ------ | ------ 
ks_1000       | GREEDY             |0.051719  | 99972  |109869
ks_1000       | DYN_PROG           |   -      |  -     |  -
ks_1000       | DYN_PROG_RECURRENT |   -      |  -     |  -
ks_1000       | BRANCH_AND_BOUD    |0.287275  | 99999  | 109899 

#### Dataset ks_10000 ####

dataset       | solver             | time [s] | weight | value 
------------- | ------------------ | -------- | ------ | ------ 
ks_10000      | GREEDY             |0.079201  | 1000000 | 1099870
ks_10000      | DYN_PROG           |   -      |    -   |  -
ks_10000      | DYN_PROG_RECURRENT |   -      |    -   |  -
ks_10000      | BRANCH_AND_BOUD    |4.680166  | 999994  | 1099893