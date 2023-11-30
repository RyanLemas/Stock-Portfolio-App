from alpha_vantage.timeseries import TimeSeries
from django.core.exceptions import ImproperlyConfigured
from stock.models import Portfolio
import pandas as pd
import numpy as np
import pickle
import logging
import os

logging.basicConfig(filename='script_log.txt', level=logging.ERROR)

def fetch_and_store_stock_data(stock, api_key):
    try:
        time = TimeSeries(key = api_key, output_format = 'pandas')
        data, _ = time.get_daily(symbol=stock, outputsize = 'full')
        script_directory = os.path.dirname(os.path.abspath(__file__))
        file_name = os.path.join(script_directory, f"{stock}_stock_data.pkl")
        with open(file_name, 'wb') as f:
            pickle.dump(data,f)

        print(f"Stock data for {stock} fetched and stored in {file_name}")
        return file_name
    except Exception as e:
        print(f"Error fetching and storing stock data: {e}")
        logging.error(f"Error fetching and storing stock data for {stock}: {e}")

def load_stock_data(stock):
    try:
        with open(f"{stock}_stock_data.pkl", 'rb') as f:
            stock_data = pickle.load(f)
        return stock_data
    except FileNotFoundError as e:
        print(f"Error loading stock data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def get_user_portfolio_stocks(user):
    try:
        user_portfolio = Portfolio.objects.filter(user=user)
        user_stocks = [entry.symbol for entry in user_portfolio]
        return user_stocks
    except Exception as e:
        print(f"Error getting user portfolio stocks: {e}")

def add_stock_to_portfolio(user, stock, shares, purchase_price):
    try:
        existing_entry = Portfolio.objects.filter(user=user, symbol=stock).first()

        if existing_entry and existing_entry.purchase_price == purchase_price:
            existing_entry.shares_owned += shares
            existing_entry.save()
            print(f"Stock {stock} updated in the portfolio.")
            return True
        else:
            new_entry = Portfolio.objects.create(
                user=user,
                symbol=stock,
                shares_owned=shares,
                purchase_price=purchase_price
            )
            print(f"Stock {stock} added to the portfolio.")
            return True

    except Exception as e:
        print(f"Error adding stock to portfolio: {e}")
        return False


def remove_stock_from_portfolio(user, stock, shares):
    try:
        shares = int(shares)
        existing_entry = Portfolio.objects.filter(user=user, symbol=stock).first()
        if existing_entry:
            if existing_entry.shares_owned >= shares:
                existing_entry.shares_owned -= shares

                if existing_entry.shares_owned == 0:
                    existing_entry.delete()
                else:
                    existing_entry.save()

                print(f"Removed {shares} shares of {stock} from your portfolio.")
                return True
            else:        
                print(f"You don't have enough {stock} shares in your portfolio.")
                return False
        else:
            print(f"There are no {stock} shares in your portfolio")
            return False
    except Exception as e:
        print(f"Error adding stock to portfolio: {e}")
        return False
        

def get_current_stock_data(stock, api_key):
    try:
        time_series = TimeSeries(key=api_key, output_format='pandas')
        data, _ = time_series.get_quote_endpoint(symbol=stock)
        return data

    except Exception as e:
        print(f"Error fetching current stock data: {e}")

def buy_sell_hold_logic(stock, stock_data):
    try:
        close_prices = pd.to_numeric(stock_data['08. previous close'], errors='coerce')
        last_close_price = close_prices.iloc[-1]

        average_close_price = np.mean(close_prices)

        if last_close_price < average_close_price:
            print(f"Buy {stock} - Last close price is lower than the average")
            return "Buy"
        elif last_close_price > average_close_price:
            print(f"Sell {stock} - Last close price is higher than the average.")
            return "Sell"
        else:
            print(f"Hold {stock} - Last close price is around the average")
            return "Hold"
    except Exception as e:
        error_message = f"Error fetching and storing stock data for {stock}: {e}"
        print(error_message)
        logging.error(error_message)

