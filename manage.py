#!/usr/bin/env python
import argparse

from clockify.session import ClockifySession
from redminelib import Redmine

from config import CLOCKIFY_API_KEY, REDMINE_API_KEY
from constants import redmine_url
from utils import collect_data, push, report, report_push

parser = argparse.ArgumentParser(description="My example explanation")  # TODO причесать парсер аргументов
parser.add_argument("command", type=str)
parser.add_argument("--coeff", type=float, default=1.0)
parser.add_argument("--target", type=float, default=0.0)
my_namespace = parser.parse_args()

clockify = ClockifySession(CLOCKIFY_API_KEY)
redmine = Redmine(redmine_url, key=REDMINE_API_KEY)
collect_data(clockify, redmine, coeff=my_namespace.coeff, target=my_namespace.target)

if my_namespace.command == "report":
    report()

if my_namespace.command == "push":
    push(redmine)

if my_namespace.command == "report_push":
    report_push(redmine)
