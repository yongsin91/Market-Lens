import requests
import os
import ml_yfinance as ys
import ml_yfinance_news as ysn
import ml_polygon_news as pygn
import AVnewspull as avnews
from sqlalchemy import create_engine, text

#function - query ticker list from watchlist database
def watchlist_data():

    try:
        database = os.getenv("DATABASE_URL")
        engine = create_engine(database)

        with engine.connect() as connection:
            result = connection.execute(text("SELECT DISTINCT ticker FROM watchlists"))
            tickers = [row[0] for row in result.fetchall()]

            return tickers
        
    except Exception as e:
        # Handle any other exceptions
        print(f"An unexpected error occurred at Routing Phase: {e}")


def main():
    try: 
        ticker_lists = watchlist_data()

        if ticker_lists is not None:
            for ticker in ticker_lists:
                
                # updating stocks data
                ys.main(ticker)

                # updating stock news
                ysn.main(ticker)
                pygn.main(ticker)
                avnews.main(ticker)

    except Exception as e:
        # Handle any other exceptions
        print(f"An unexpected error occurred at initialization Phase: {e}")

#main body
if __name__ == "__main__":
    main()