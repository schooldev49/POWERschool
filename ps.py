import io
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup
from simple_term_menu import TerminalMenu

URL = 'https://millburn.powerschool.com/guardian/home.html'

payload = {
  'dbpw': os.environ['PASSWORD'],
  'serviceName': 'PS Parent Portal',
  'pcasServerUrl': '/',
  'credentialType': 'User Id and Password Credential',
  'account': os.environ['USERNAME'],
  'pw': os.environ['PASSWORD'],
}

s = requests.Session()
r = s.post(URL, data=payload)
soup = BeautifulSoup(r.text, 'lxml')

def select_value(options):
  def get_key(keys):
    menu = TerminalMenu(keys)
    index = menu.show()
    return keys[index]
  key = get_key(list(options.keys()))
  return options[key]

student_links = soup.select('#students-list > li > a')
students = {link.text: link['href'][25:-2] for link in student_links}

r = s.post(URL, {'selected_student_id': select_value(students)})
soup = BeautifulSoup(r.text, 'lxml')
score_table = soup.find('table')

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
df = pd.read_html(io.StringIO(str(score_table)), header=1, extract_links='body')[0]
grades = df.loc[:, 'Course':].iloc[:-1, :-2]
grades.to_html('grades.html')
