import datetime

import requests
from bs4 import BeautifulSoup

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from models import Base, Data 


def validate_bedrooms(bedrooms):
    if bedrooms == 'Bachelor/Studio':
        return 1
    return bedrooms

def validate_date(date):
    if "<" in date:
        return datetime.datetime.now().strftime('%d-%m-%Y')
    elif date == "Yesterday":
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)
        return yesterday
    return datetime.datetime.strptime(date.replace("/", "-"), "%d-%m-%Y")

def validate_price(price):



    if price == "Please Contact":
        return None, None

    currency = price[:1]
    price = int(price[1:].replace(",", "")[:-3])

    return currency, price

def main():
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
    
    path = "postgresql://postgres:mysecretpassword@localhost:5432/mytestdb"

    obj_list = []
    for item in main():
        obj = Data(**item)
        # obj = Data(title=item_res["title"], date_posted=item_res["date_posted"], location=item_res["location"], 
        #             bedrooms=item_res["bedrooms"], description=item_res["description"], currency=item_res["currency"], price=item_res["price"]
        #             )
        obj_list.append(obj)

    engine = create_engine(path, echo = True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add_all(obj_list)

    session.commit()
