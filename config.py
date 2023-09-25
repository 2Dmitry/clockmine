from environs import Env

env = Env()
env.read_env()

CLOCKIFY_API_KEY = env("CLOCKIFY_API_KEY")
REDMINE_API_KEY = env("REDMINE_API_KEY")

TIMEZONE = env("TIMEZONE")
