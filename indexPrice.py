import requests
import json
import hashlib
import hmac
import time

API_KEY = '5775f'
API_SECRET = '527a'

# Binance API base URL
BASE_URL = 'https://testnet.binancefuture.com'

# Symbol you want to get data for
symbol = 'BTCUSDT'

# Interval for the candlestick data (e.g., 1s, 5s, 1m, 1h, etc.)
interval = '1m'

def generate_signature(query_string):
    return hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def get_candlestick_data(symbol, interval):
    endpoint = '/fapi/v1/klines'
    params = f'symbol={symbol}&interval={interval}&limit={1}'
    url = BASE_URL + endpoint + '?' + params

    # Add timestamp to the query string for signed requests
    timestamp = int(time.time() * 1000)
    query_string = f'{params}&timestamp={timestamp}'
    signature = generate_signature(query_string)

    # Add the signature to the request headers
    headers = {'X-MBX-APIKEY': API_KEY}
    params += f'&timestamp={timestamp}&signature={signature}'

    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == "__main__":
    candlestick_data = get_candlestick_data(symbol, interval)
    print(json.dumps(candlestick_data, indent=2))
