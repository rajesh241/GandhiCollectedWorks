"""Blank file which can server as starting point for writing any script file"""
import argparse
import re
import pandas as pd
from bs4 import BeautifulSoup, NavigableString, element

from commons import logger_fetch
dateRegex = re.compile(r'((January)|(February)|(March)|(April)|(May)|(June)|(July)|(August)|(September)|(October)|(November)|(December))\s*\d{1,2}\,\s*\[?\d{4,4}\]?')

def args_fetch():
    '''
    Paser for the argument list that returns the args list
    '''

    parser = argparse.ArgumentParser(description=('This is blank script',
                                                  'you can copy this base script '))
    parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
    parser.add_argument('-t', '--test', help='Test Loop',
                        required=False, action='store_const', const=1)
    parser.add_argument('-p', '--parse', help='parse html',
                        required=False, action='store_const', const=1)
    parser.add_argument('-vn', '--volumeNumber', help='Volume Number', required=False)
    parser.add_argument('-ti1', '--testInput1', help='Test Input 1', required=False)
    parser.add_argument('-ti2', '--testInput2', help='Test Input 2', required=False)
    args = vars(parser.parse_args())
    return args

def strip_tags(html):
    soup = BeautifulSoup(html, "lxml")
    fonts = soup.findAll("font")
    for font in fonts:
        font.unwrap()
    spans = soup.findAll("span")
    for span in spans:
        span.unwrap()
    italics = soup.findAll("i")
    for italic in italics:
        italic.unwrap()
    return soup

def get_titles(logger, soup, volume_number):
    csv_array = []
    column_headers = ["chapter_no", "date", "title", "content"]
    content = ''
    first_hr = soup.find("hr")
    chapter_no = 1
    h1 = first_hr.findNext("h1")
    title = h1.text.lstrip().rstrip()
    h1.decompose()
    content = ''
    for tag in first_hr.next_siblings:
        if tag.name == "hr":
            logger.info(f"{chapter_no} - {title}")
            date_string = extract_dates(logger, content)
            row = [chapter_no, date_string, title, content]
            csv_array.append(row)
            logger.info(date_string)
            logger.info("Priting content ")
            chapter_no = chapter_no + 1
            content = ''
            h1 = tag.findNext("h1")
            title = h1.text.lstrip().rstrip()
            h1.decompose()
        else:
            #logger.info(f" Tag Content {tag.contents}")
            is_navigable_string = isinstance(tag, element.NavigableString)
            logger.info(f"tag name is {tag.name} - {is_navigable_string}")
            if not is_navigable_string:
                tag_content = ''.join(tag.findAll(text=True))
                content = content + "\n" + process_text(logger, tag_content)
    date_string = extract_dates(logger, content)
    row = [chapter_no, date_string, title, content]
    csv_array.append(row)
    filename = f"data/csv/{volume_number}_content.csv"
    dataframe = pd.DataFrame(csv_array, columns=column_headers)
    dataframe.to_csv(filename, index=False)
        
def process_text(logger, s):
    s = s.replace("\n", " ")
    s = s.replace("\p", " ")
    return s

def extract_dates(logger, s):
    date_string = None
    mo = dateRegex.search(s.replace("[","").replace("]",""))
    if mo is not None:
        date_string = mo.group(0).replace("[","").replace("]","")
    return date_string
        
  
def strip_footnotes(logger, soup, volume_number):
    csv_array = []
    column_headers = ["footnote_no", "footnote"]
    footnote_number = 1
    sup = soup.find("sup")
    j = 0
    while sup is not None:
        if sup.has_attr("class"):
            logger.info("Nothing needs to be done here")
        else:
            sup_text = sup.text.lstrip().rstrip()
            sup_p = sup.findNext("p", attrs={'class' : 'footnote'})
            footnote_found = False
            k = 0
            note_text = ''
            while (not footnote_found) and (sup_p):
                k = k + 1
                if k == 10:
                    break
                inside_sup = sup_p.find("sup",  text=sup_text)
                if inside_sup is not None:
                    footnote_found = True
                    note_text = sup_p.text.lstrip().rstrip().replace("\n"," ")
                    sup_p.decompose()
                else:
                    sup_p = sup_p.findNext("p", attrs={'class' : 'footnote'})
            new_tag = soup.new_tag("footnote")
            new_tag_text = f"libtech_{footnote_number}_footnote"
            new_tag.append(new_tag_text)
            a = [new_tag_text, note_text]
            csv_array.append(a)
            footnote_number = footnote_number + 1
            sup.insert_after(new_tag)
            logger.info(f"{sup_text}- {note_text}")
        sup = sup.findNext("sup")
        j = j + 1
        if j == 1000000:
            break
    dataframe = pd.DataFrame(csv_array, columns=column_headers)
    filename = f"data/csv/{volume_number}_footnotes.csv"
    dataframe.to_csv(filename, index=False)
    sups = soup.findAll("sup")
    for sup in sups:
        sup.decompose()
    return soup

def process_volume(logger, volume_number):
    logger.info(f"Porcessing volume {volume_number}")
    filename = f"data/html/{volume_number}.html"
    with open(filename, "rb") as fi:
        myhtml = fi.read()
    soup = strip_tags(myhtml)
    soup = strip_footnotes(logger, soup, volume_number)
    get_titles(logger, soup, volume_number)

def main():
    """Main Module of this program"""
    args = args_fetch()
    logger = logger_fetch(args.get('log_level'))
    if args['parse']:
        volume_number = args['volumeNumber']
        volume_array = []
        if volume_number is None:
            logger.error("Volume number is required or enter all")
            exit(0)
        if volume_number == "all":
            for i in range(1, 99):
                 volume_array.append(i)
        else:
            volume_array.append(volume_number)
        logger.info(f"Volumes to be processed are {volume_array}")
        for volume_no in volume_array:
            process_volume(logger, volume_no)

    if args['test']:
        logger.info("Testing phase")
        filename = "data/test.html"
        with open(filename, "rb") as fi:
            myhtml=fi.read()
        invalid_tags = ['font']
        soup = strip_tags(myhtml)
        soup = strip_footnotes(logger,soup)
        with open("y.html", "w") as fo:
            fo.write(soup.prettify())
        get_titles(logger,soup)

    logger.info("...END PROCESSING")

if __name__ == '__main__':
    main()
