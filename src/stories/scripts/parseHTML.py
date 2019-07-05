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
  parser.add_argument('-ch', '--chapters', help='Volume Number to be parsed', required=False)
  parser.add_argument('-t', '--test', help='Test Loop', required=False,action='store_const', const=1)
  parser.add_argument('-d', '--download', help='Download PDF of all Volumes', required=False,action='store_const', const=1)
  parser.add_argument('-p', '--parse', help='parse HTML', required=False,action='store_const', const=1)
  parser.add_argument('-p1', '--parse1', help='parse HTML', required=False,action='store_const', const=1)
  parser.add_argument('-p2', '--parse2', help='parse HTML', required=False,action='store_const', const=1)

  args = vars(parser.parse_args())
  return args

def get_element(node):
  # for XPATH we have to count only for nodes with same type!
  length = len(list(node.previous_siblings)) + 1
  if (length) > 1:
    return '%s:nth-child(%s)' % (node.name, length)
  else:
    return node.name

def xpath_soup(element):
    """
    Generate xpath from BeautifulSoup4 element
    :param element: BeautifulSoup4 element.
    :type element: bs4.element.Tag or bs4.element.NavigableString
    :return: xpath as string
    :rtype: str
    
    Usage:
    
    >>> import bs4
    >>> html = (
    ...     '<html><head><title>title</title></head>'
    ...     '<body><p>p <i>1</i></p><p>p <i>2</i></p></body></html>'
    ...     )
    >>> soup = bs4.BeautifulSoup(html, 'html.parser')
    >>> xpath_soup(soup.html.body.p.i)
    '/html/body/p[1]/i'
    """
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        """
        @type parent: bs4.element.Tag
        """
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name
            if siblings == [child] else
            '%s[%d]' % (child.name, 1 + siblings.index(child))
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

#xpath /html/body/h1[2]
def modifyFootNote(logger,tag):
  superTag=tag.find("sup")
  if superTag is not None:
    superText=superTag.text.lstrip().rstrip()
    superTextLength=len(superText)
    tagText=tag.text.lstrip().rstrip()
    if str(superText) == tagText[:superTextLength]:
      superTag['class']="footnote"
def detectFootNote(logger,tag):
  footNote=False
  superTag=tag.find("sup")
  if superTag is not None:
    superText=superTag.text.lstrip().rstrip()
    superTextLength=len(superText)
    tagText=tag.text.lstrip().rstrip()
    if str(superText) == tagText[:superTextLength]:
      footNote=True
  return footNote
  
def extractTextFromP(logger,tag,vn,ch,paraNumber,notesDict):
  superTags=tag.findAll("sup")
  for superTag in superTags:
    logger.info(tag.text)
    superText=superTag.text.lstrip().rstrip()
    refNo="(cwg-%s-%s-%s-%s)" %(str(vn),str(ch),str(paraNumber),superText)
    if superText.isdigit():
      noteTag=tag.findNext("sup",text=superText)
      if noteTag is not None:
        superTag.string=refNo
        logger.info(superText)
        logger.info(noteTag.parent)
        while noteTag.parent.name != "p":
          if noteTag.parent.parent is not None:
            noteTag=noteTag.parent
          else:
            logger.info("I am breaking")
            break
        if noteTag.parent is not None:
          noteText=noteTag.parent.text.lstrip().rstrip()
        else:
          noteText=''
        notesDict[refNo]=noteText
  tagText=tag.text.lstrip().rstrip().replace("\n"," ")
  tagText=re.sub('\t', ' ', tagText) 
  tagText=re.sub(' +', ' ', tagText) 
  return tagText,notesDict

def createJson(logger,myhtml,volumeNumber=None):
  mysoup=BeautifulSoup(myhtml,"lxml")
  i=0
  paraNumber=1
  hrs=mysoup.findAll("hr")
  for hr in hrs:
    notesDict={}
    i=i+1
    logger.info(i)
    content=''
    h1=hr.findNext("h1")
    title=h1.text.lstrip().rstrip()
    for tag in hr.next_siblings:
      if tag.name == "hr":
          break
      else:
        if tag.name is not None:
          if tag.name == "p":
            try:
              tagClass=tag['class']
            except:
              tagClass=[]
            logger.info(tagClass)
            if "footnote" not in tagClass:
           #isFootNote=detectFootNote(logger,tag)
           #if isFootNote == False:
             # tagText=tag.text.lstrip().rstrip().replace("\n","")
             # logger.info(tagText)
              tagText,notesDict=extractTextFromP(logger,tag,volumeNumber,i,paraNumber,notesDict)
              paraNumber+=1
              content+=tagText
              content+="\n"
            
          else:
            paras=tag.findAll("p")
            for para in paras:
              try:
                tagClass=para['class']
              except:
                tagClass=[]
              logger.info(tagClass)
              if "footnote" not in tagClass:
             # if tagClass != "footnote":
             # isFootNote=detectFootNote(logger,para)
             # if isFootNote == False:
                tagText,notesDict=extractTextFromP(logger,para,volumeNumber,i,paraNumber,notesDict)
                paraNumber+=1
                #extractTextFromP(logger,para,volumeNumber,i)
                content+=tagText
                content+="\n"
    logger.info(title)
    logger.info(content)
    logger.info(notesDict)
    myStory=Story.objects.filter(title=title,volumeNo=volumeNumber).first()
    if myStory is None:
      myStory=Story.objects.create(title=title,volumeNo=volumeNumber)
    myStory.content=content
    myStory.footnote=str(notesDict)
    myStory.save()
  
def insertLines(logger,myhtml,volumeNumber=None,fileDir=None):
  mysoup=BeautifulSoup(myhtml,"lxml")
      # create a new tag

  # insert the new tag after the current tag
  h1s=mysoup.findAll("h1",{"class":"western"})
  i=0
  s=''
  for h1 in h1s:
    i=i+1
    xpath=xpath_soup(h1)
    title=h1.text.lstrip().rstrip()
    elem=h1
    elemText=elem.text.lstrip().rstrip()
    pxpath=xpath_soup(elem)
    while pxpath != "/html/body":
      titleElement=elem
      elem=elem.parent
      pxpath=xpath_soup(elem)
    #logger.info(titleElement)
    lineTag = mysoup.new_tag("hr")
    titleElement.insert_before(lineTag)
    logger.info(f"{i}-{title}")
    s+="%s,%s,%s,%s\n" % (i,xpath,pxpath,title)
  with open("/tmp/%s.css" % str(volumeNumber),"w") as f:
    f.write(s)

  paras=mysoup.findAll("p")
  for para in paras:
    superTag=para.find("sup")
    if superTag is not None:
      superText=superTag.text.lstrip().rstrip()
      superTextLength=len(superText)
      tagText=para.text.lstrip().rstrip()
      if str(superText) == tagText[:superTextLength]:
        superTag['class']="footnote"
        superTag.string=superText
        para['class']="footnote"

  filename="%s/%s.html" % (fileDir,str(volumeNumber))
  with open(filename, "w") as file:
    file.write(str(mysoup))


def getElements(logger,myhtml,volumeNumber,totalChapters):
  mysoup=BeautifulSoup(myhtml,"lxml")
  h1s=mysoup.findAll("h1",{"class":"western"})
  i=0
  for h1 in h1s:
    i=i+1
    title=h1.text.lstrip().rstrip()
    logger.info(f"{i}-{title}")
  exit(0)
  for i in range(1,int(totalChapters)+1):
    h1=None
    if i == 1:
      nextTag=mysoup.find("ol")
      logger.info(nextTag)
      h1=nextTag.find("h1")
      logger.info(h1)
    else:  
      nextTag=curTag.findNext("ol")
      h1=nextTag.find("h1")
    while h1 is None:
      nextTag=nextTag.findNext("ol")
      h1=nextTag.find("h1")
      
    if h1 is  None:
      title=None
      logger.info(f"{i}-{title}")
    else:
      title=nextTag.text.lstrip().rstrip()
      curTag=h1
      logger.info(f"{i}-{title}")
  exit(0)
 
  for i in range(1,int(totalChapters)+1):
    i=i+1
    logger.info(i)
    nextTag=mysoup.find("ol",start=i)
    if nextTag is  None:
      title="None"
    else:
      title=nextTag.text.lstrip().rstrip()
  exit(0)
  titleStyle="display:inline"
  titles=mysoup.findAll("h1",{"style":titleStyle})
#  titles=mysoup.findAll("h1")
  i=0
  for title in titles:
    i=i+1
    titleText=title.text.lstrip().rstrip()
    z=re.match("^\d{1,3}\..*$",titleText)
    if z:
      match='match'
    else:
      match='nothing'
    try:
      if match == "nothing":
        parentTag=title.parent.parent
        chapterID=parentTag['start']
      else:
        chapterID=''
    except:
      chapterID=''
    logger.info(f"{i}-{match}-{chapterID}-{titleText}")
  exit(0)
  titleStyle="display:inline"
  curTag=mysoup.find("ol",start="1")
  logger.info(curTag)
  for i in range(1,int(totalChapters)+1):
    logger.info(i)
    nextTag=curTag.findNext("h1",{"style":titleStyle})
    titleText=nextTag.text.lstrip().rstrip()
    z=re.match("^\d{1,3}\..*$",titleText)
    if z:
      match='match'
      chapterID=0
    else:
      try:
        parentTag=nextTag.parent.parent
        chapterID=parentTag['start']
        if int(chapterID) == i:
          match='match'
        else:
          match='nothing'
      except:
        chapterID=''
        matchin='nothing'
    logger.info(f"{i}-{match}-{chapterID}-{titleText}")
    if match == 'nothing':
      exit(0)
    curTag=nextTag
  exit(0)
  firstChapterTag=mysoup.find("ol",start="1")
  if firstChapterTag is None:
    return "First Chapter not found"
  curTag=firstChapterTag
  logger.info(firstChapterTag)
  nextTag=curTag.findNext("ol",start="2")
  logger.info(nextTag)
  for i in range(1,int(totalChapters)+1):
    i=i+1
    logger.info(i)
    nextTag=curTag.findNext("ol",start=i)
    if nextTag is  None:
      logger.info("tag is None")
      curTitle=curTag
      while nextTag is None:
        curTitle=curTitle.findNext("h1")
        curTitleText=curTitle.text.lstrip().rstrip()
        logger.info(curTitleText)
        titleSearchString="%s." %(str(i))
        if titleSearchString in curTitleText:
          nextTag=curTitle
          exit(0)
      exit(0)
    logger.info(nextTag.text.lstrip().rstrip())
    curTag=nextTag
     #curTitle=curTag
     #while nextChapterTag is None:
     #  curTitle=curTitle.findNext("h1")
     #  curTitleText=curTitle.text.lstrip().rstrip()
     #  z=re.match("^\d{1,3}\..*$",titleText)

  exit(0)
  titleStyle="display:inline"
  titles=mysoup.findAll("h1",{"style":titleStyle})
  titles=mysoup.findAll("h1")
  i=0
  for title in titles:
    i=i+1
    titleText=title.text.lstrip().rstrip()
    z=re.match("^\d{1,3}\..*$",titleText)
    if z:
      match='match'
    else:
      match='nothing'
    try:
      if match == "nothing":
        parentTag=title.parent.parent
        chapterID=parentTag['start']
      else:
        chapterID=''
    except:
      chapterID=''
    logger.info(f"{i}-{match}-{chapterID}-{titleText}")
  exit(0)
  ols=mysoup.findAll("ol",{"class":"c50"})
  i=0
  for ol in ols:
    h1=ol.find("h1")
    if h1 is not None:
      i=i+1
      titleText=h1.text.lstrip().rstrip()
      logger.info(f"{i}-{titleText}")

  exit(0)
def getElements1(logger,myhtml,bookTitle,volumeNumber):
  titleClass="s1"
  globalTitle="THE COLLECTED WORKS OF MAHATMA GANDHI"
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
          #VOL. 48 : 21 NOVEMBER, 1929 2 APRIL, 1930 
         #cmd="wget -O %s %s " % (filename,volLink)
         #logger.info(cmd)
         #os.system(cmd)
  if args['parse']:
    logger.info("Parsing the HTML")
    vnArray=[]
    vn=args['volumeNumber']
    if vn is None:
      logger.info("Volume number is not sepcified")
      for i in range(1,99):
        vnArray.append(i)
    else:
      vnArray.append(vn)
    logger.info(vnArray)
    for volumeNumber in vnArray:
      fileDir=os.path.join(settings.MEDIA_ROOT,"books","experiment")
      filename=fileDir+"/gandhi_vol%s.html" % (volumeNumber)
      f=open(filename,"rb")
      myhtml=f.read()
      insertLines(logger,myhtml,volumeNumber=volumeNumber,fileDir=fileDir)
      filename="%s/%s.html" % (fileDir,str(volumeNumber))
      f=open(filename,"rb")
      myhtml=f.read()
      createJson(logger,myhtml,volumeNumber=volumeNumber)

  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
