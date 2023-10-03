from environs import Env

from constants.timezones import allowed_timezones

env = Env()
env.read_env()

REDMINE_API_KEY = env("REDMINE_API_KEY")
CLOCKIFY_API_KEY = env("CLOCKIFY_API_KEY")

TIMEZONE = env("TIMEZONE")
if TIMEZONE not in allowed_timezones:
    raise Exception("ERROR! Вы указали таймзону, которая не поддерживается")

REDMINE_ACTIVITIES_NOT_ALLOWED = env("REDMINE_ACTIVITIES_NOT_ALLOWED")
REDMINE_URL_TIME_ENTRY = env("REDMINE_URL_TIME_ENTRY")
REDMINE_URL = env("REDMINE_URL")
