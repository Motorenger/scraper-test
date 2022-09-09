import datetime

import requests
from bs4 import BeautifulSoup

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
    

def insert_in_db(pages):
    
    URL_PATH = "postgresql://postgres:mysecretpassword@localhost:5432/mytestdb"

    obj_list = []

    for obj in main(pages):
        object_instance = Data(**obj)
        obj_list.append(object_instance)

    engine = create_engine(URL_PATH, echo = True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    session.add_all(obj_list)

    session.commit()
    print("Successfully inserted data in db")


def insert_in_googlesheet(pages):
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
        "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"
        ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("main-361919-18fbe1722248.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Scraper-Test").sheet1   

    head_row = ["img_url", "title", "date_posted", "location", "bedrooms", "description", "currency", "price"]
    sheet.insert_row(head_row, 1)
    count = 2
    for obj in main(pages):
        row_insert = list(obj.values())
        row_insert[2] = str(row_insert[2])
        sheet.insert_row(row_insert, count)

        count+=1
    print("Successfully inserted data in google sheet")


if __name__ == "__main__":

    pages = int(input("How many pages do u want to scrape?: "))
    
    choose = int(input("Choose where you want to insert data(1: db, 2: google_sheet, 3: both): "))

    # obj_list = main(pages)

    if choose == 1:
        insert_in_db(pages)
        print("End of the program")
    
    elif choose == 2:
        insert_in_googlesheet(pages)
        print("End of the program")

    
    elif choose == 3:
        insert_in_db(pages)
        insert_in_googlesheet(pages)
        print("End of the program")
