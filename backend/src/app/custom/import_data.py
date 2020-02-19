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
        logger.info("In test mode")
        objs = Article.objects.all()
        for obj in objs:
            logger.info(obj.id)
            content = obj.content
            content = content.replace("\r\n","<br />")
            content = content.replace("\n\r","<br />")
            content = content.replace("\n","<br />")
            content = content.replace("\r","<br />")
            obj.content = content
            obj.save()
    if args['import']:
        date_format = "%B %d, %Y"
        data_dir = "../../../../scripts/code/data/csv/"
        volume_array = [i for i in range(1,99)]
        logger.info(volume_array)
        for volume_number in volume_array:
            filename = f"{data_dir}{volume_number}_content.csv"
            logger.info(filename)
            dataframe = pd.read_csv(filename)
            logger.info(dataframe.columns)
            for index, row in dataframe.iterrows():
                title = row['title']
                logger.info(f"{volume_number}-{index}-{title}")
                chapter_number = row['chapter_no']
                post_date_string = str(row['date'])
                posted = get_date_object(post_date_string, date_format=date_format)
                content = row['content']
                title = process_text(logger, title)
                content = process_text(logger, content)
                my_article = Article.objects.filter(volume_number=volume_number, chapter_number=chapter_number).first()
                if my_article is None:
                    my_article = Article.objects.create(volume_number=volume_number, chapter_number=chapter_number, title=title)
                my_article.title = title
                my_article.content = content
                if posted is not None:
                    my_article.posted = posted
                my_article.save()

    logger.info("...END PROCESSING")

def process_text(logger, content):
    is_str = isinstance(content, str)
    if is_str:
        content = re.sub(r'libtech_\d+_footnote', '', content)
    else:
        content = ''
    return content

if __name__ == '__main__':
    main()
