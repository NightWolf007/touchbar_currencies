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

def currency_symbol_to_char(symbol):
    if symbol == 'USD' or symbol == 'USDT':
        return u'$'
    if symbol == 'BTC':
        return u'₿'
    return ''

def format_percent_change(pc):
    if pc >= 0:
        return '+' + round(pc * 100, 2) + '%'
    else:
        return '-' + round(pc * 100, 2) + '%'

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
    return [
        [
            (ticker[0][1:4], ticker[0][4:]),
            ticker[7],
            ticker[6]
        ] for ticker in tickers
    ]

def get_bittrex_tickers():
    response = requests.get(BITTREX_URL + '/api/v1.1/public/getmarketsummaries')
    tickers = response.json()['result']
    return [
        [
            tuple(reversed(ticker['MarketName'].split('-'))),
            ticker['Last'],
            (ticker['Last'] - ticker['PrevDay']) / ticker['PrevDay']
        ] for ticker in tickers
    ]

bitfinex_symbols = get_bitfinex_symbols()
bitfinex_tickers = sorted(get_bitfinex_tickers(bitfinex_symbols), key=lambda x: x[2])

bittrex_tickers = sorted(get_bittrex_tickers(), key=lambda x: x[2])

r = redis.StrictRedis(host='localhost', port=6379, db=0)
for i, ticker in enumerate(bitfinex_tickers):
    symbol = ticker[0]
    price = round_price(ticker[1])
    percent_change = ticker[2]

    symbol_key = APP_NAME + ':bitfinex:' + ':'.join(symbol)
    button_key = APP_NAME + ':buttons:bitfinex:' + i
    r.mset({
        symbol_key + ':price': price,
        symbol_key + ':percent_change': percent_change,
        button_key + ':currency': symbol[0],
        button_key + ':currency_symbol': currency_symbol_to_char(symbol[1]),
        button_key + ':price': price,
        button_key + ':percent_change': percent_change
    })
    r.set(key + ':price', price)
    r.set(key + ':percent_change', percent_change)
    key = APP_NAME = ':buttons:bitfinex:' + i ''
    r.delete(key)
    r.rpush(key, )
    r.rpush(key, ticker[2])
    key = APP_NAME + ':buttons:bitfinex:' + i
    r.delete()

for i, ticker in enumerate(bittrex_tickers):
    key = APP_NAME + ':bittrex:' + ':'.join(ticker[0])
    r.delete(key)
    r.rpush(key, round_price(ticker[1]))
    r.rpush(key, ticker[2])

exit(0)
