#!/usr/bin/env python
# coding: utf-8

import requests
import os
import datetime as dt
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL') # From .env file
AV_KEY = os.getenv('AV_KEY') # From .env file


# Function to update articles in the database
def update_articles(data):
    try:
        # Create a connection engine to the database using SQLAlchemy
        engine = create_engine(DATABASE_URL)

        # Insert data into the 'articles' table in the database
        with engine.connect() as conn:
            # SQL query to insert article data into the articles table
            sql = text('''  
                INSERT IGNORE INTO articles (title, article_date, source, url)
                VALUES (:title, :article_date + INTERVAL 8 HOUR, :source, :url) 
            ''')

            # Execute the SQL query with the provided data
            conn.execute(sql, data)
            conn.commit()

            # Insert article stock link into 'stocks_articles' table
            query = text('''   
                SELECT article_id FROM articles
                WHERE title = :title 
                AND article_date = :article_date + INTERVAL 8 HOUR
                AND source = :source
                AND url = :url 
            ''')

            # Retrieve article_id from the 'articles' table
            result = conn.execute(query, data).scalar()
            update = {'title': data['ticker'], 'article_id': result}
            
            # Insert stock-related data into 'stocks_articles' table
            sql = text('''  
                INSERT IGNORE INTO stocks_articles (ticker, article_id)
                VALUES (:title, :article_id) 
            ''')

            # Execute the SQL query for the stock articles data
            conn.execute(sql, update)
            conn.commit()

            print("AV news update successful")
            
    except Exception as e:
        print(f"An unexpected error occurred during the SQL Phase: {e}")
        return None


# Function to get the time period for filtering news articles
def time_format():
    # to get the time which is 24 hours before the current time
    time_24hrs_ago = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=24)).strftime("%Y%m%dT%H%M")

    return time_24hrs_ago



# Function to connect to the API and retrieve news data
def api_connect(symbol):
    try:
        # Use the hardcoded API key
        time_period = time_format()

        # Construct the API URL for fetching news data
        url = (
            f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&'
            f'apikey={AV_KEY}&time_from={time_period}&limit=50'
        )

        # Print the URL to ensure it's formed correctly
        # print("Constructed API URL:", url)

        # Send the request to the API and retrieve the news data
        response = requests.get(url).json()

        # Print the entire response to see if there's an error message
        # print("Raw API Response:", response)

        # Check if the 'feed' key exists in the response
        if 'feed' in response:
            news_list = []
            for article in response['feed']:
                # Prepare the article data
                news_data = {
                    'title': article['title'],
                    'article_date': article['time_published'],
                    'source': 'Alpha Vantage',
                    'url': article['url'],
                    'ticker': symbol
                }
                news_list.append(news_data)

            return news_list
        else:
            print("AV Error: 'feed' key not found in the response.")
            return None
        
    except Exception as e:
        print(f"An unexpected error occurred during the API connection: {e}")
        return None





# Main function to retrieve and update news articles in the database
def main(ticker):
    try: 
        # Fetch news articles using the API
        data = api_connect(ticker)

        # If news data is received, update the articles table in the database
        if data:
            for news in data:
                update_articles(news)
          
    except Exception as e:
        print(f"An unexpected error occurred before API connect phase: {e}")


# Main script execution
if __name__ == "__main__":

    # for testing purpose
    # manual trigger of the individual script
    # to check if successful:
    # 1. Go to MySQL database 'articles' 
    # 2. Search for source = 'Alpha Vantage', check if latest news is 1 day before current date
    ticker = 'AAPL'
    DATABASE_URL = os.getenv('DATABASE_URL')
    print(DATABASE_URL)
    main(ticker)
