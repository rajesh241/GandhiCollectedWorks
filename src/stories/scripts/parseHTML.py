import os
import csv
import re
import sys
import requests
import time
from bs4 import BeautifulSoup
fileDir = os.path.dirname(os.path.realpath(__file__))
rootDir=fileDir+"/../../"
sys.path.insert(0, rootDir)
djangoSettings="base.settings"
import django
from django.core.wsgi import get_wsgi_application
from django.db import models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()
from django.db.models import F,Q,Sum,Count
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from stories.scripts.commons import loggerFetch
from stories.models import Story
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='This implements the crawl State Machine')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-vn', '--volumeNumber', help='Volume Number to be parsed', required=False)
  parser.add_argument('-t', '--test', help='Test Loop', required=False,action='store_const', const=1)
  parser.add_argument('-d', '--download', help='Download PDF of all Volumes', required=False,action='store_const', const=1)
  parser.add_argument('-p', '--parse', help='parse HTML', required=False,action='store_const', const=1)

  args = vars(parser.parse_args())
  return args

titleClass="s1"
globalTitle="THE COLLECTED WORKS OF MAHATMA GANDHI"
def getElements(logger,myhtml,bookTitle,volumeNumber):
  mysoup=BeautifulSoup(myhtml,"lxml")
  footnoteStyle="font-size: 10px;"
  titleStyle="font-size: 13px;"
  #First Purging teh Page Numbers
  div12s=mysoup.findAll("div",style="font-size: 12px;")
  j=0
  for div12 in div12s:
    myText=div12.text.lstrip().rstrip()
    if myText == bookTitle:
      div12.decompose()
    z=re.match("^([\d]+)$",myText)
    if z:
      div12.decompose()
      j=j+1
      logger.info(f" count-{j} page-{myText}")
  logger.info("I am sleeping")
  logger.info(f"Total Pages -{j}")
  div10s=mysoup.findAll("div",style="font-size: 10px;")
  for div10 in div10s:
    myText=div10.text.lstrip().rstrip()
    if myText==globalTitle:
      logger.info(myText)
      div10.decompose()
  div10s=mysoup.findAll("div",style="font-size: 10px;")
  for div10 in div10s:
    myText=div10.text.lstrip().rstrip()
    if myText==bookTitle:
      logger.info(myText)
      div10.decompose()

  #Now we will get all Titles
  titleDivs=mysoup.findAll("div",{"style":titleStyle})
  i=1
  for titleDiv in titleDivs:
    title=titleDiv.text.lstrip().rstrip()
    z=re.match("^\d{1,3}\..*$",title)
    if z:
      content=''
      footnote=''
      j=0
      for tag in titleDiv.find_next_siblings("div"):
        j=j+1
        style=tag['style']
        if (j == 1) and (style == titleStyle):
          title=title+" "+tag.text.lstrip().rstrip()
        if (j > 1) and (style == titleStyle):
          break
        else:
          if style == footnoteStyle:
            footnote+=tag.text
            footnote+="\n"
          else:
            content+=tag.text
            content+="\n"
    # titleNext=titleDiv.find_next_sibling("div")
    # style=titleNext['style']
    # if style == titleStyle:
    #   title=title+" "+titleNext.text.lstrip().rstrip()
      logger.info(f"{i}    {title}")
      myStory=Story.objects.filter(title=title,volumeNo=volumeNumber).first()
      if myStory is None:
        myStory=Story.objects.create(title=title,volumeNo=volumeNumber)
      myStory.content=content
      myStory.footnote=footnote
      myStory.save()
      i=i+1
  return None

  #Now we need to purge the title of the book


  

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info("Begin Processing")
  if args['test']:
    logger.info("Running the test loop")
  if args['download']:
    url="http://www.gandhiashramsevagram.org/gandhi-literature/collected-works-of-mahatma-gandhi-volume-1-to-98.php"
    baseURL="http://www.gandhiashramsevagram.org/gandhi-literature/"
    fileDir=os.path.join(settings.MEDIA_ROOT,"books")
    r=requests.get(url)
    if r.status_code == 200:
      myhtml=r.content
      mysoup=BeautifulSoup(myhtml,"lxml")
      links=mysoup.findAll("a")
      i=0
      for link in links:
        volName=link.text
        volLink=baseURL+link["href"]
        if ("Volume" in volName) and ("pdf" in volLink):
          logger.info(volLink)
          i=i+1
          logger.info(f"{i}-{volName}")
          filename="%s/gandhi_vol%s.pdf" % (fileDir,str(i))
          logger.info(filename)
          cmd="wget -O %s %s " % (filename,volLink)
          logger.info(cmd)
          os.system(cmd)
  if args['parse']:
    logger.info("Parsing the HTML")
    vn=args['volumeNumber']
    if vn is None:
      vn='48'
    if vn == '1':
      bookTitle="VOL.1: 1884 30 NOVEMBER, 1896"
    else:
      bookTitle="VOL. 48 : 21 NOVEMBER, 1929 2 APRIL, 1930"
    fileDir=os.path.join(settings.MEDIA_ROOT,"books")
    filename=fileDir+"/gandhi_vol%s.html" % (vn)
    logger.info(filename)
    f=open(filename,"rb")
    myhtml=f.read()
    error=getElements(logger,myhtml,bookTitle,vn)
    logger.info(f"Error is {error}")
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
