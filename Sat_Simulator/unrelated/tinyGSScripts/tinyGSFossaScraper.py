#python tinyGSScraper.py link

import os
import sys
import requests

import dateutil.parser
from datetime import timedelta

from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait

options = webdriver.ChromeOptions()

options.add_argument("--incognito")
options.add_argument("--nogpu")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,1280")
options.add_argument("--no-sandbox")
options.add_argument("--enable-javascript")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')

ua = UserAgent()
userAgent = ua.random

driver = webdriver.Chrome("/home/omchabra/satelliteSims/satelliteSimulator/otherStuff/chromedriver", chrome_options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": userAgent})

def document_initialised(driver):
    return driver.execute_script("console.log('return initialised')")

driver.get(sys.argv[1])
driver.implicitly_wait(3)

times = []
snrs = []
elevations = []
sats = []
distance = []
for i in range(1, 80):
    sats.append(driver.find_elements_by_xpath("/html/body/div/div/main/div/div[1]/div/div[2]/div[3]/div[" + str(i) + "]/a/div/div[1]/h3")[0].text)
    times.append(driver.find_elements_by_xpath("/html/body/div/div/main/div/div[1]/div/div[2]/div[3]/div[ " + str(i) + "]/a/div/div[1]/div")[0].text)
    distance.append(driver.find_elements_by_xpath("/html/body/div/div/main/div/div[1]/div/div[2]/div[3]/div[ " + str(i) + "]/a/div/div[4]/div[2]")[0].text)
    elevations.append(driver.find_elements_by_xpath("/html/body/div/div/main/div/div[1]/div/div[2]/div[3]/div[" + str(i) + "]/a/div/div[5]/div[2]")[0].text)
    snrs.append(driver.find_elements_by_xpath("/html/body/div/div/main/div/div[1]/div/div[2]/div[3]/div[" + str(i) + "]/a/div/div[7]/div[2]")[0].text)

print(sats)
print(times)
print(elevations)
print(distance)
print(snrs)

for i in range(0, len(sats)):
    tm = times[i].split("(")[0]
    times[i] = dateutil.parser.parse(tm) + timedelta(hours=7)
    elevations[i] = elevations[i][:-1]
    distance[i] = distance[i][:-2]
    snrs[i] = snrs[i][:-2]
print(sats)
print(times)
print(elevations)
print(distance)
print(snrs)

outStr = "Sat, Time, Elevation, Distance, SNR\n"
for i in range(0, len(sats)):
    outStr += str(sats[i]) + "," + str(times[i]) + "," + str(elevations[i]) + "," + str(distance[i]) + "," + str(snrs[i]) + "\n"
file = open("TinyGS_Data/scraped.txt", 'w+')
file.write(outStr)
file.close()