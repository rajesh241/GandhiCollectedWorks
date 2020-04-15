"""This module is for importing all nrega locations"""
import os
import argparse
import datetime
import random
import re
import urllib.parse as urlparse
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import django
import pandas as pd
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from commons import logger_fetch, get_date_object
from defines import DJANGO_SETTINGS
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)
django.setup()
from app.models import Article

User  = get_user_model()
def args_fetch():
    '''
    Paser for the argument list that returns the args list
    '''

    parser = argparse.ArgumentParser(description=('This script will import',
                                                  'nrega locations from nic'))
    parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
    parser.add_argument('-i', '--import', help='import',
                        required=False, action='store_const', const=1)
    parser.add_argument('-t', '--test', help='test functions',
                        required=False, action='store_const', const=1)
    parser.add_argument('-f', '--fixfilepath', help='fix broken file paths',
                        required=False, action='store_const', const=1)
    parser.add_argument('-lt', '--location_type', help='location type', required=False)
    args = vars(parser.parse_args())
    return args


def main():
    """Main Module of this program"""
    args = args_fetch()
    logger = logger_fetch(args.get('log_level'))
    if args['test']:
        csv_array = []
        column_headers = ["title", "content", "footnote", "volume_number",
                          "chapter_number", "posted"]
        logger.info("In test mode")
        objs = Article.objects.all()
        for obj in objs:
            logger.info(obj.id)
            a = [obj.title, obj.content, obj.footnote, obj.volume_number,
                 obj.chapter_number, obj.posted]
            csv_array.append(a)
        df = pd.DataFrame(csv_array, columns=column_headers)
        df.to_csv("/tmp/dump.csv")
 
if __name__ == '__main__':
    main()
