# 

Scraper use BS4 for working with html and getting data. Before that it makes request with requests library
Then depends on what user chose he inserting scraped data 
In db using SQLAlchemy
And in Google Sheets using Gspread

1. All u need is to run docker conteiner with postgresql:
  docker run -d -p 5432:5432 --name my-postgres -e POSTGRES_PASSWORD=mysecretpassword postgres
2. Then create table with name:
  mytesttable
 
3. After that u are ready to go.
  just accec vitual env and install requirements and run main.py

4. Choose how may pages and where to insert your data)

Good Luck!

  
