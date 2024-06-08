"""
* create venv *
$ python3 -m ensurepip
$ python3 -m pip install --upgrade pip
$ pip install -r requirements.txt
$ python
$ import graph30
"""

import psycopg2
import networkx as nx


from config import DATABASE_URI_REPORTS_REDMINE


conn = psycopg2.connect(DATABASE_URI_REPORTS_REDMINE)
cur = conn.cursor()

G = nx.DiGraph()
