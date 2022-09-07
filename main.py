
import requests
from bs4 import BeautifulSoup

import datetime


def validate_bedrooms(bedrooms):
    if bedrooms == 'Bachelor/Studio':
        return 1
    return bedrooms

def validate_date(date):
    if "<" in date:
        return datetime.datetime.now().strftime('%d-%m-%Y')
    return date


url = f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{1}/c37l1700273"

req = requests.get(url)

doc = BeautifulSoup(req.text, "html.parser")

items = doc.find_all(class_="search-item")

res = []


for item in items:
    item_res = {}
    if item:
        try: 
            item_res["img_url"] = item.find("picture").find("img").get("data-src")
        except Exception:
            item_res["img_url"] = item.find("img").get("src")

        item_res["title"] = item.find("a", class_="title").string.strip()
        item_res["data_posted"] =  validate_date(item.find(class_="date-posted").string.strip())
        item_res["location"] = item.find(class_="location").find("span").string.strip()
        item_res["bedrooms"] = validate_bedrooms(item.find(class_="bedrooms").text.split("Beds:")[1].strip())
        item_res["description"]  =  " ".join(item.find(class_="description").text.strip().split())
        price = item.find(class_="price").text.strip()
        item_res["currency"] = price[0]
        item_res["price"] = price[1:]
        res.append(item_res)

