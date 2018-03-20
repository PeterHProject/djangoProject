#Webscraping to get house price data 

from bs4 import BeautifulSoup
import requests
import pandas

list_of = []
for i in range(0,1):
    url = "https://www.zoopla.co.uk/for-sale/property/balham/?identifier=balham&q=Balham%2C%20London&search_source=refine&radius=0&pn="
    r = requests.get(url+str(i))
    c = r.content
    soup = BeautifulSoup(c, 'html.parser')
    properties = soup.find_all("div", {"class":"listing-results-right clearfix"})
    for y in range(0,len(properties)):
        price = properties[y].find('a').text.replace('\n', '').replace(' ', '')
        bedroom = properties[y].find_all('span')[0].text

        list_of.append([price, bedroom])

def clean_up(x):
    allowed = ["0","1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "-"]
    x = str(x)
    n = ""
    for i in x:
        if i in allowed:
            n = n+i
    try:
        n = float(n)
    except:
        n = 0
    return n

df = pandas.DataFrame(columns=['Price', 'Bedroom'])
for i in range(0,len(list_of)):
    df.loc[i] = [list_of[i][0], list_of[i][1]]
df['Price'] = df['Price'].apply(clean_up)
df['Bedroom'] = df['Bedroom'].apply(clean_up)
df2 = df.groupby('Bedroom').mean()
