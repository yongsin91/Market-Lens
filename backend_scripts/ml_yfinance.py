#!/usr/bin/env python
# coding: utf-8

import requests
import yfinance as yf
import os

from sqlalchemy import create_engine, text

def sql_connect(update_data):
    try:

        #get database link       
        database = os.getenv("DATABASE_URL")
        engine = create_engine(database)

        #insert data into database
        #duplicate update will be overwritten
        with engine.connect() as conn:
            sql = text('''  
            INSERT INTO stocks (    stock_time,
                                    ticker,
                                    company_name,   
                                    current_price,
                                    volume,
                                    day_low,
                                    day_high,
                                    year_low,     
                                    year_high) 
            VALUES (    FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(NOW()) / 600) * 600),
                        :ticker, 
                        :company_name, 
                        :current_price, 
                        :volume, 
                        :day_low, 
                        :day_high, 
                        :year_low, 
                        :year_high) 
            ON DUPLICATE KEY UPDATE 
                stock_time = VALUES(stock_time),
                ticker = VALUES(ticker); ''')

            conn.execute(sql, update_data)
            conn.commit()
            print(f"Update successful for {update_data['ticker']}")
            
    except Exception as e:
        # Handle any other exceptions
        print(f"An unexpected error occurred during stocks SQL Phase: {e}")
        return None


#function - api connect
def api_connect(symbol):
    try:
        ticker = yf.Ticker(symbol)
        keys_to_include = ['symbol','currentPrice','volume','dayLow','dayHigh','fiftyTwoWeekLow','fiftyTwoWeekHigh','shortName']
        new_dict = {key: ticker.info[key] for key in keys_to_include}
        
        update_data= { 
            'ticker': new_dict['symbol'],
            'company_name' : new_dict['shortName'],
            'current_price': new_dict['currentPrice'],
            'volume': new_dict['volume'],
            'day_low' : new_dict['dayLow'],
            'day_high' : new_dict['dayHigh'],
            'year_low': new_dict['fiftyTwoWeekLow'],
            'year_high': new_dict['fiftyTwoWeekHigh']}
        return update_data
        
    except Exception as e:
        # Handle any other exceptions
        print(f"An unexpected error occurred during stocks API Phase: {e}")
        return None



#main function
def main(ticker):
    try: 

        #retrieve data from api
        data = api_connect(ticker)

        # if data from api received, write it into database
        if data is not None:
            sql_connect(data)
    
    except Exception as e:
        # showing the execption error for subsequent logging
        print(f"An unexpected error occurred before stocks API Connect Phase: {e}")

#main body
if __name__ == "__main__":

    # for testing purpose
    # manual trigger of the individual script
    # to check if successful :
    # 1. go to MySQL database 'stocks' 
    # 2. check if ticker 'AAPL' latest timestamp is current timestamp in 10 mins interval
    ticker = 'AAPL'
    DATABASE_URL = os.getenv('DATABASE_URL')
    print(DATABASE_URL)
    main(ticker)


