from datetime import datetime,timedelta
from pathlib import Path
import requests
from binance.client import Client
import csv
import json
import pandas as pd
import time

# MARKET=[]
MARKET = ['ETH-230929-800-C', 'ETH-230929-800-P', 'BNB-230728-225-C', 'BTC-240329-65000-P']
TRADE_DATA = []
OLD_TRADE =[]

PAIRS = set()
PRICE_TICKER =[]
HISTORICAL_RECORD =[]

TRADE_SET = {'id', 'symbol', 'price', 'qty', 'quoteQty', 'side', 'time'}
# trade_list_file = './tradeList.csv'
OLD_TRADE_LOOKUP = {'id', 'tradeId', 'price', 'qty', 'quoteQty', 'side', 'time', 'symbol'}
# old_trade_file = './oldTradeLookup.csv'
SYMBOL_PRICE_TICKER = {'indexPrice', 'time', 'symbol'}
# symbol_price_file = './symbolPriceTicker.csv'
HISTORICAL_EXERCISE_RECORD = {'symbol', 'strikePrice', 'realStrikePrice', 'expiryDate', 'strikeResult'}
# historical_exercise_file = './historicalExerciseFile.csv'

INDEX_PRICE_DATA_SET = ['openTimeOfCandle','openPrice','highPrice','lowPrice','closePrice','Volume','closeTimeOfCandle','quoteAssetVolume','NumberOfTrades','takerBuyBaseAssetVolume','takerBuyQuoteAssetVolume','Ignore']
index_price_data = []

def getSymbol():
    response = requests.get('https://eapi.binance.com/eapi/v1/exchangeInfo')
    print(response)
    if response.status_code == 200:
        data = response.json()
        # print(data)
        option_symbols_list = data["optionSymbols"]
        for symbol_data in option_symbols_list:
            # MARKET.append(symbol_data["symbol"])
            PAIRS.add(symbol_data["underlying"])
        print(MARKET)
        print(PAIRS)

def getTradeList():
    endpoint = 'https://eapi.binance.com/eapi/v1/trades'
    for market in MARKET:
        params = {'symbol': market}
        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                data = response.json()
                for item in data:
                    utc_datetime = datetime.fromtimestamp(item['time'] / 1000)
                    item['time']=utc_datetime.strftime('%Y-%m-%d %H:%M:%S')
                TRADE_DATA.extend(data)

        except Exception as e:
            continue
    # print(TRADE_DATA)
    # with open(trade_list_file, 'w', newline='') as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=TRADE_SET)
    #     writer.writeheader()
    #     writer.writerows(TRADE_DATA)

def oldTradeLookup():
    endpoint = 'https://eapi.binance.com/eapi/v1/historicalTrades'
    for market in MARKET:
        params = {'symbol': market, "limit": 500}
        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                data = response.json()
                for item in data:
                    utc_datetime = datetime.fromtimestamp(item['time'] / 1000)
                    item['time']=utc_datetime.strftime('%Y-%m-%d %H:%M:%S')
                    item['symbol'] = market
                OLD_TRADE.extend(data)
        except Exception as e:
            continue
    # print(OLD_TRADE)
    # with open(old_trade_file, 'w', newline='') as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=OLD_TRADE_LOOKUP)
    #     writer.writeheader()
    #     writer.writerows(OLD_TRADE)

def getSymbolPriceTicker():
    endpoint = 'https://eapi.binance.com/eapi/v1/index'
    print(PAIRS)
    for market in PAIRS:
        params = {'underlying': market}
        print(params)
        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:             
                data = response.json() 
                data['symbol'] = market   
                utc_datetime = datetime.fromtimestamp(data['time'] / 1000)
                data['time']=utc_datetime.strftime('%Y-%m-%d %H:%M:%S')
                PRICE_TICKER.append(data)
        except Exception as e:
            continue
    print(PRICE_TICKER)
    # with open(symbol_price_file, 'w', newline='') as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=SYMBOL_PRICE_TICKER)
    #     writer.writeheader()
    #     writer.writerows(PRICE_TICKER)

def getHistoricalExerciseRecords():
    response = requests.get('https://eapi.binance.com/eapi/v1/exerciseHistory')
    if response.status_code == 200:
        data = response.json()
        # print(data)
        for item in data:
            utc_datetime = datetime.fromtimestamp(item['expiryDate'] / 1000)
            item['expiryDate']=utc_datetime.strftime('%Y-%m-%d %H:%M:%S')
            HISTORICAL_RECORD.append(item)
        # with open(historical_exercise_file, 'w', newline='') as csvfile:
        #     writer = csv.DictWriter(csvfile, fieldnames=HISTORICAL_EXERCISE_RECORD)
        #     writer.writeheader()
        #     writer.writerows(data)

def getOpenInterest():
    endpoint = 'https://eapi.binance.com/eapi/v1/openInterest'
    for market in PAIRS:
        params = {'underlyingAsset': market, 'expiration': '1790032798'}
        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                data = response.json()
                print(data)
        except Exception as e:
            continue

def getklineCandlesPerSecond():
    for i in range(10):
        params = {"symbol": 'ETHUSDT', "interval": "1m" , "limit":"1"}
        response = requests.get('https://api.binance.com/api/v1/klines',params=params)
        raw_data = response.json()
        for data in raw_data:
            utc_datetime = datetime.fromtimestamp(data[0] / 1000)
            updated_datetime = utc_datetime + timedelta(seconds=1+i)
            data[0] = updated_datetime.strftime('%Y-%m-%d %H:%M:%S')
            time.sleep(1)               
        # print(raw_data)
        index_price_data.extend(raw_data) 

    print(index_price_data)
    with open("./getklineCandlesPerSecond.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(INDEX_PRICE_DATA_SET)
        writer.writerows(index_price_data)    

def getOrderBookMidPrice():

    url = "https://fapi.binance.com/fapi/v1/depth"

    # Parameters for the order book request
    symbol = "ethusdt"  # Trading pair symbol
    limit = 20  # Number of levels to fetch (e.g., 5 for top 5 bids and asks)

    # Create or open the CSV file in write mode
    csv_file = open('restApi_midPrice8-12-2023.csv', 'w', newline='')
    csv_writer = csv.writer(csv_file)

    # Write the header row to the CSV file
    csv_writer.writerow(['Current Time','Transaction Time', 'Message Time', 'Highest Bid', 'Lowest Ask', 'Mid Price'])

    while True:
        # Query parameters
        params = {
            "symbol": symbol,
            "limit": limit,
            # "interval":"1m"
        }

        # Send the GET request to fetch order book data
        response = requests.get(url, params=params)
        print(response)

        # Process the response
        if response.status_code == 200:
            order_book_data = response.json()

            utc_datetime = datetime.fromtimestamp(order_book_data['T'] / 1000)
            transaction_timestamp = utc_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')

            utcMessage_datetime = datetime.fromtimestamp(order_book_data['E'] / 1000)
            Message_timestamp = utcMessage_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')

            current_time = time.time()
            current_local_time = datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S.%f')


            # Calculate mid price
            highest_bid_price = float(order_book_data["bids"][0][0])
            lowest_ask_price = float(order_book_data["asks"][0][0])
            
            for bid in order_book_data['bids']:
                price = float(bid[0])
                if highest_bid_price is None or price > highest_bid_price:
                    highest_bid_price = price

            for ask in order_book_data['asks']:
                price = float(ask[0])
                if lowest_ask_price is None or price < lowest_ask_price:
                    lowest_ask_price = price

            mid_price = (highest_bid_price + lowest_ask_price) / 2        

            print(order_book_data)
            
            # Write the data to the CSV file
            csv_writer.writerow([current_local_time,transaction_timestamp,Message_timestamp, highest_bid_price, lowest_ask_price, mid_price])
            
            # Print the data
            print(f"Timestamp: {current_local_time}")
            print(f"Highest Bid Price: {highest_bid_price}")
            print(f"Lowest Ask Price: {lowest_ask_price}")
            print(f"Mid Price: {mid_price}")
        else:
            print("Failed to fetch order book data.")
            print(response.text)
        
        # Delay for 1 second
        time.sleep(1)

def getIndexPriceSecond():

    url = "https://fapi.binance.com/fapi/v1/premiumIndex"
    print("Calling index price api....",url)    

    # Parameters for the order book request
    symbol = "ethusdt"  # Trading pair symbol

    # Create or open the CSV file in write mode
    csv_file = open('RestAPIindexPricesPerSecond.csv', 'w', newline='')
    csv_writer = csv.writer(csv_file)

    # Write the header row to the CSV file
    csv_writer.writerow(["timestamp","IndexPrice","Symbol"])

    while True:
        # Query parameters
        params = {
            "symbol": symbol
        }

        # Send the GET request to fetch order book data
        response = requests.get(url, params=params)
        print(response)

        # Process the response
        if response.status_code == 200:
            raw_data = response.json()
            index_price = raw_data["indexPrice"]            
            timestamp=datetime.fromtimestamp(raw_data["time"] / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')
            csv_writer.writerow([timestamp,index_price,symbol])     
        else:
            print("Failed to fetch index data.")
            print(response.text)
        
        # Delay for 1 second
        time.sleep(1)

def main():
    # getSymbol()

    # getTradeList()

    # oldTradeLookup()

    # getSymbolPriceTicker()

    # getHistoricalExerciseRecords()

    # getOpenInterest()

    # getIndexPricePerSecond()

    # getOrderBookMidPrice()

    getIndexPriceSecond()


    # with pd.ExcelWriter('binance_data.xlsx', engine='openpyxl') as writer:
    #     pd.DataFrame(TRADE_DATA).to_excel(writer, sheet_name='TradeList', index=False)
    #     pd.DataFrame(OLD_TRADE).to_excel(writer, sheet_name='OldTradeLookup', index=False)
    #     pd.DataFrame(PRICE_TICKER).to_excel(writer, sheet_name='SymbolPriceTicker', index=False)
    #     pd.DataFrame(HISTORICAL_RECORD).to_excel(writer, sheet_name='HistoricalExerciseRecord', index=False)
        

if __name__ == '__main__':
    main()