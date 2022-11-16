# https://blog.theodo.com/2020/11/django-jupyter-vscode-setup/

import django
import os
import sys

# Find the project base directory
BASE_DIR = os.path.dirname("../whatever")

# Add the project base directory to the sys.path
# This means the script will look in the base directory for any module imports
# Therefore you'll be able to import analysis.models etc
sys.path.insert(0, BASE_DIR)

# The DJANGO_SETTINGS_MODULE has to be set to allow us to access django imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
# Allow async operations
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# This is for setting up django
django.setup()
