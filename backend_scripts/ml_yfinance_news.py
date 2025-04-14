#!/usr/bin/env python
# coding: utf-8

import requests
import yfinance as yf
import os

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
        print(f"An unexpected error occurred during yahoo news SQL Phase: {e}")
        return None

#retrieve data from api
def api_connect(symbol):
    try:
        ticker = yf.Ticker(symbol)
        yahoo_news = [a['content'] for a in ticker.news]
        news_list = []
        
        for article in yahoo_news:
            news_data = {   'title': article['title'],
                            'article_date': article['pubDate'],
                            'source' : 'yahoo finance',
                            'url': article['canonicalUrl']['url'],
                            'ticker': symbol }
            news_list.append(news_data)
        return news_list
        
    except Exception as e:
        # Handle any other exceptions
        print(f"An unexpected error occurred during yahoo news API Phase: {e}")
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
        print(f"An unexpected error occurred before yahoo news API Connect Phase: {e}")

#main body
if __name__ == "__main__":

    # for testing purpose
    # manual trigger of the individual script
    # to check if successful:
    # 1. Go to MySQL database 'articles' 
    # 2. Search for source = 'yahoo finance', check if latest news is 1 day before current date
    ticker = 'AAPL'
    DATABASE_URL = os.getenv('DATABASE_URL')
    print(DATABASE_URL)
    main(ticker)


