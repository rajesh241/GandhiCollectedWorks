"""File to hold constants"""
import os
import sys
import json
import uuid
from pathlib import Path

HOME_DIR = str(Path.home())
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = FILE_DIR+"/../../"
sys.path.insert(0, ROOT_DIR)
DJANGO_SETTINGS = "base.settings"
