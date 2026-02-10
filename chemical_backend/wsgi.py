"""
WSGI config for chemical_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chemical_backend.settings")

application = get_wsgi_application()
