# Code for scraping stuff
import selenium
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Get name data
df = pd.read_csv("~/Desktop/class_enrollment_summary_spring_2022.csv")
df['Instructor Full Name']=df['Instructor Full Name'].fillna(",")
names = df["Instructor Full Name"].values.tolist()
last_names = []
first_names = []

# Clean up first/last names
for item in names:
    last_names.append(item.split(',')[0])
    first_names.append(item.split(',')[1])

# Remove middle names
length = len(first_names)
for i in range(length):
    if first_names[i] != "":
        first_names[i] = first_names[i].split()[0]

emails = []

def directory_scraper(last_name, first_name):
    '''Scraping based on list of last_names that correspond to list of first_names'''
    # Open chromedriver
    driver = webdriver.Chrome(
        executable_path="/Users/brianham77/Desktop/classdata/chromedriver"
    )
    length = len(last_name)
    emailList = []
    for i in range(length):
        # Open site
        driver.get("https://directory.harvard.edu")

        # Clear previous
        driver.find_element("xpath", "//input[@name='lastName']").clear()
        driver.find_element("xpath", "//input[@name='firstName']").clear()

        # The David Bug: for some reason the directory breaks down when you search for Prof. David Wang. I literally have no idea why.
        if first_name[i] == "David":
            emailList.append(first_name[i] + " " + last_name[i])
            continue

        # Enter info
        driver.find_element("xpath", "//input[@name='lastName']").send_keys(last_name[i])
        driver.find_element("xpath", "//input[@name='firstName']").send_keys(first_name[i])
        driver.find_element("xpath", "//input[@id='search']").click()
        page_source = driver.page_source

        # Soup
        soup = BeautifulSoup(page_source, 'lxml')
        if soup.find('form') is None:
            emailList.append(first_name[i] + " " + last_name[i])
            continue
        form = soup.find('form')

        if form.find('p') is not None: # If invalid person
            emailList.append(first_name[i] + " " + last_name[i])
        else:
            if form.find('a') is None: # If no email address listed
                emailList.append(first_name[i] + " " + last_name[i])
            else:
                emailList.append(form.find('a').get_text())
    driver.quit()
    return emailList

def chunkify(l, n):
    '''split list l into chunks of max size n'''
    final = [l[i * n:(i + 1) * n] for i in range((len(l) + n - 1) // n )]
    return final

# Do 400 at a time as otherwise server crashes
meta_lastnames = chunkify(last_names, 400)
meta_firstnames = chunkify(first_names, 400)
iters = len(meta_lastnames)

for i in range(iters):
    print("Chunk " + str(i) + "\n")
    emails.extend(directory_scraper(meta_lastnames[i], meta_firstnames[i]))

print(emails)