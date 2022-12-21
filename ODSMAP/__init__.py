from __future__ import absolute_import, unicode_literals
import django
import os
import nltk

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('rslp')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ODSMAP.settings.dev")

django.setup()


# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)