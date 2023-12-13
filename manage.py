#!/usr/bin/env python
import argparse

from utils.commands import clean_desc, collect_data, init, push, report

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

# Work
collect_data(coeff=my_namespace.coeff, target=my_namespace.target)
if my_namespace.command == "init":
    init()
elif my_namespace.command == "clean":
    clean_desc()
elif my_namespace.command == "report":
    report()
elif my_namespace.command == "push":
    report()
    push()
else:
    raise Exception("Unknown command. Use 'dc exec app ./manage.py -h'")
