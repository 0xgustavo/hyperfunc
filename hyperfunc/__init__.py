import os
import sys

from .config import BASE_DIR, DJANGO_SETTINGS_MODULE
from .core import hyper
from .utils import register_funcs

sys.path.append(str(BASE_DIR))

if DJANGO_SETTINGS_MODULE:
    try:
        import django

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)
        django.setup()
    except ImportError:
        raise ImportError("Django is not installed")

register_funcs(BASE_DIR)
