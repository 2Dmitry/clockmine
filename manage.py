#!/usr/bin/env python
import argparse

from config import CLOCKIFY_API_KEY, REDMINE_API_KEY, REDMINE_URL
from models import MyClockifySession, MyRedmine
from utils import collect_data, init, push, report

# Parse arguments
parser = argparse.ArgumentParser(description="My example explanation")
parser.add_argument("command", type=str, help="what do you want? you can: report/push/init")
parser.add_argument("-c", "--coeff", type=float, help="coefficient for every time entry")
parser.add_argument("-t", "--target", type=float, help="total time entry")
my_namespace = parser.parse_args()

# Validator arguments
if my_namespace.coeff and my_namespace.target:
    raise Exception("Укажите максимум одно значение")
elif (my_namespace.coeff and my_namespace.coeff <= 0) or (my_namespace.target and my_namespace.target <= 0):
    raise Exception("Значение должно быть положительным")

# Init clock&mine
clockify = MyClockifySession(key=CLOCKIFY_API_KEY)
redmine = MyRedmine(url=REDMINE_URL, key=REDMINE_API_KEY)

# Work
collect_data(clockify=clockify, redmine=redmine, coeff=my_namespace.coeff, target=my_namespace.target)
if my_namespace.command == "init":
    init(clockify=clockify, redmine=redmine)
elif my_namespace.command == "report":
    report(redmine=redmine)
elif my_namespace.command == "push":
    report(redmine=redmine)
    push(clockify=clockify, redmine=redmine)
else:
    raise Exception("Unknown command. Use 'dc exec app ./manage.py -h'")
