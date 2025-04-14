#!/usr/bin/env python
# coding: utf-8

import requests
import os
import datetime as dt

from sqlalchemy import create_engine, text


def update_articles(data):
    try:
        #get database link       
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        #instantiate SQLAlchemy
        engine = create_engine(DATABASE_URL)

        #insert data into database
        with engine.connect() as conn:

            #add articles into database
            sql = text('''  INSERT IGNORE INTO articles ( title, article_date, source, url) 
                            VALUES  (:title, :article_date + INTERVAL 8 HOUR , :source, :url) ''')

            conn.execute(sql, data)
            conn.commit()

            #add article stock link into article_stock database
            query = text( '''   SELECT article_id FROM articles
                                WHERE  title = :title 
                                and article_date = :article_date + INTERVAL 8 HOUR 
                                and source = :source
                                and url = :url ''')

            result = conn.execute(query,data).scalar()
            update = {'title':data['ticker'], 'article_id':result}
            sql = text('''  INSERT IGNORE INTO stocks_articles (ticker, article_id) 
                            VALUES  (:title, :article_id) ''')

            conn.execute(sql, update)
            conn.commit()

            print("Update successful")
            
    except Exception as e:
        # Handle any other exceptions
        print(f"An unexpected error occurred during polygon news SQL Phase: {e}")
        return None

#to get the time period for news filtering 
def time_format():
    # to get the time which is 24hours before current time
    time_10min_ago = (dt.datetime.now(dt.UTC) - dt.timedelta(hours=24)).isoformat() + "Z"

    # Parse the timestamp, ignoring microseconds and timezone
    dt_obj = dt.datetime.strptime(time_10min_ago[:19], "%Y-%m-%dT%H:%M:%S")

    # Convert back to string in the required format
    formatted_timestamp = dt_obj.strftime("%Y-%m-%dT%H:%M:%SZ")

    return formatted_timestamp

#retrieve data from api
def api_connect(symbol):
    try:

        POLY_KEY = os.getenv('POLY_KEY')
        time_period = time_format()

        url = ('https://api.polygon.io/v2/reference/news?'
                f'ticker={symbol}&'
                f'published_utc.gte={time_period}&'
                f'apiKey={POLY_KEY}')

        response = requests.get(url).json()['results']
        news_list = []
        
        for article in response:
            news_data = {   'title': article['title'],
                            'article_date': article['published_utc'],
                            'source' : 'polygon io',
                            'url': article['article_url'],
                            'ticker': symbol }
            news_list.append(news_data)
        return news_list
        
    except Exception as e:
        # Handle any other exceptions
        print(f"An unexpected error occurred during polygon news API Phase: {e}")
        return None


#main function
def main(ticker):
    try: 
        # receives info about ticker and calling data from api
        data = api_connect(ticker)

        # if data from api received, write it into database
        if data:
            for news in data:
                update_articles(news)
          
    except Exception as e:
        # Handle any other exceptions
        print(f"An unexpected error occurred before polygon news API Connect Phase: {e}")

#main body
if __name__ == "__main__":
    main(ticker)



