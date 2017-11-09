#!/usr/bin/python

from math import log10, floor
import requests
import redis

APP_NAME = 'tbcurrencies'
BITFINEX_URL='https://api.bitfinex.com'
BITTREX_URL='https://bittrex.com'

def round_to_2(x):
    return round(x, -int(floor(log10(abs(x)))) + 1)

def round_price(x):
    if x >= 1:
        return round(x, 2)
    return round_to_2(x)

def get_bitfinex_symbols():
    response = requests.get(BITFINEX_URL + '/v1/symbols', timeout=10)
    symbols = response.json()
    return [(symbol[:3].upper(), symbol[3:].upper()) for symbol in symbols]

def get_bitfinex_tickers(symbols):
    params = {
        'symbols': ','.join(['t' + ''.join(symbol) for symbol in symbols])
    }
    response = requests.get(BITFINEX_URL + '/v2/tickers', params=params, timeout=10)
    tickers = response.json()
    return {(ticker[0][1:4], ticker[0][4:]): ticker[7] for ticker in tickers}

def get_bittrex_tickers():
    response = requests.get(BITTREX_URL + '/api/v1.1/public/getmarketsummaries')
    tickers = response.json()['result']
    return {tuple(reversed(ticker['MarketName'].split('-'))): ticker['Last'] for ticker in tickers}

bitfinex_symbols = get_bitfinex_symbols()
bitfinex_tickers = get_bitfinex_tickers(bitfinex_symbols)

bittrex_tickers = get_bittrex_tickers()

r = redis.StrictRedis(host='localhost', port=6379, db=0)
for symbol, price in bitfinex_tickers.items():
    r.set(APP_NAME + ':bitfinex:' + ':'.join(symbol), round_price(price))
for symbol, price in bittrex_tickers.items():
    r.set(APP_NAME + ':bittrex:' + ':'.join(symbol), round_price(price))

exit(0)
