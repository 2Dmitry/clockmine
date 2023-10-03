from config import CLOCKIFY_API_KEY, REDMINE_API_KEY, REDMINE_URL
from models.clockify import MyClockify
from models.redmine import MyRedmine

clockify = MyClockify(key=CLOCKIFY_API_KEY)
redmine = MyRedmine(url=REDMINE_URL, key=REDMINE_API_KEY)
