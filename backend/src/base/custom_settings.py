"""This module has custom settings for Libtech Django backend"""
from pathlib import Path
import json

HOME_DIR = str(Path.home())
HOME_DIR = '/opt/config/gandhi_django_config'
JSON_CONFIG_FILE = f"{HOME_DIR}/.libtech/emailConfig.json"
with open(JSON_CONFIG_FILE) as config_file:
    EMAIL_CONFIG = json.load(config_file)
BASE_CONFIG_FILE = f"{HOME_DIR}/.libtech/baseConfig.json"
with open(BASE_CONFIG_FILE) as base_config_file:
    BASE_CONFIG = json.load(base_config_file)
SQL_CONFIG = f"{HOME_DIR}/.libtech/mysqlConfig.cnf"
