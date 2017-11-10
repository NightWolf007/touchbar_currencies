#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import log10, floor
import requests
import redis

APP_NAME = 'tbcurrencies'
BITFINEX_URL='https://api.bitfinex.com'
BITTREX_URL='https://bittrex.com'

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

def round_to_2(x):
    return round(x, -int(floor(log10(abs(x)))) + 1)

def fromat_price(x):
    if x >= 1:
        return str(round(x, 2))
    return str(round_to_2(x))

def format_currency_symbol(symbol):
    if symbol == 'USD' or symbol == 'USDT':
        return u'$'
    if symbol == 'BTC':
        return u'₿'
    return ''

def format_percent_change(pc):
    if pc >= 0:
        return '+' + str(round(pc * 100, 2)) + '%'
    else:
        return str(round(pc * 100, 2)) + '%'

def format_button(ticker):
    symbol = ticker[0]
    return (
        symbol[0] + ': ' +
        fromat_price(ticker[1]) + ' ' +
        format_currency_symbol(symbol[1]) + ' ' +
        format_percent_change(ticker[2])
    )

def save_tickers(r, exchange, tickers, currencies):
    base_key = ':'.join([APP_NAME, exchange])
    for currency in currencies:
        ctickers = filter(lambda x: x[0][1] == currency, tickers)
        for i, ticker in enumerate(ctickers):
            exchange_key = ':'.join([base_key, ':'.join(ticker[0])])
            button_key = ':'.join([base_key, 'buttons', currency, str(i)])
            text = format_button(ticker)
            r.mset({
                exchange_key: text,
                button_key: text
            })

def main():
    bitfinex_symbols = get_bitfinex_symbols()
    bitfinex_tickers = sorted(get_bitfinex_tickers(bitfinex_symbols),
                              key=lambda x: x[2], reverse=True)
    bittrex_tickers = sorted(get_bittrex_tickers(),
                             key=lambda x: x[2], reverse=True)

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    save_tickers(r, 'bitfinex', bitfinex_tickers, ['USD', 'BTC'])
    save_tickers(r, 'bittrex', bittrex_tickers, ['BTC', 'USDT'])

    exit(0)

if __name__ == '__main__':
    main()
