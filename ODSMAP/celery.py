from __future__ import absolute_import, unicode_literals

import os, glob

from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from django.core import management
from django.core.files.storage import FileSystemStorage

from home import views

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ODSMAP.settings')

# Set it to single thread (this allows Celery to run on windows)
# Can be removed if necessary or convenient
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

# The argument is just the name of the app (arbitrary)
app = Celery('ODSMAP')
app.conf.enable_utc = False

app.conf.update(timezone = "America/Sao_Paulo")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# The decorator flags this as a task to Celery

# Celery Beat Settings



@app.task(bind=True)
def delete_temp(self):
    fs = FileSystemStorage()
    f_list = request_globs('media/relatorio*.csv', 'media/heatmap*.png', 'media/*')
    if f_list:
        for file in f_list:
            fs.delete(file.split('\\')[1])


def request_globs(*templates):
    glob_list = None
    for template in templates:
        # print(template)
        if not glob_list:
            glob_list = glob.glob(template)
        else:
            for path in glob.glob(template):
                glob_list.append(path)
        # print(glob_list)
    return glob_list

@app.task(bind=True)
def delete_sess(self):
    try:
        management.call_command('clearsessions', verbosity=0)
        print('Expired sessions cleared.\n')
    except Exception as e:
        print(e)