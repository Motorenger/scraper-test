import datetime

import requests
from bs4 import BeautifulSoup

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from models import Base, Data 


def validate_bedrooms(bedrooms):
    '''
        Validating bedrooms value
    '''
    if bedrooms == 'Bachelor/Studio':
        return 1
    return bedrooms

def validate_date(date):
    '''
        Validating date value
    '''
    if "<" in date:
        return datetime.datetime.now().strftime('%d-%m-%Y')
    elif date == "Yesterday":
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)
        return yesterday
    return datetime.datetime.strptime(date.replace("/", "-"), "%d-%m-%Y")

def validate_price(price):
    '''
        Validating price and currency values
    '''
    if price == "Please Contact":
        return None, None

    currency = price[:1]
    price = int(price[1:].replace(",", "")[:-3])

    return currency, price

def main(pagination):
    '''
        Main func which extracts all the data from website and adding to the list where each item is dictionary
    '''
    res = []

    for page in range(pagination):
        url = f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{page+1}/c37l1700273"
        req = requests.get(url)

        doc = BeautifulSoup(req.text, "html.parser")
        items = doc.find_all(class_="search-item")

        for item in items:
            item_res = {}
            if item:
                try: 
                    item_res["img_url"] = item.find("picture").find("img").get("data-src")
                except Exception:
                    item_res["img_url"] = item.find("img").get("src")

                item_res["title"] = item.find("a", class_="title").string.strip()
                item_res["date_posted"] =  validate_date(item.find(class_="date-posted").string.strip())
                item_res["location"] = item.find(class_="location").find("span").string.strip()
                item_res["bedrooms"] = validate_bedrooms(item.find(class_="bedrooms").text.split("Beds:")[1].strip())
                item_res["description"]  =  " ".join(item.find(class_="description").text.strip().split())
                currency, price = validate_price(item.find(class_="price").text.strip())
                item_res["currency"] = currency
                item_res["price"] = price

            res.append(item_res)

    print("Sraped successfully")
    return res
    


if __name__ == "__main__":
    URL_PATH = "postgresql://postgres:mysecretpassword@localhost:5432/mytestdb"

    obj_list = []

    pages = int(input("How many pages do u want to scrape?: "))

    for obj in main(pages):
        object_instance = Data(**obj)
        obj_list.append(object_instance)

    engine = create_engine(URL_PATH, echo = True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add_all(obj_list)

    session.commit()
