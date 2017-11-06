#!/usr/bin/python3

import json
import requests

APP_NAME = 'tbcurrencies'
BITFINEX_URL='https://api.bitfinex.com'
BITTREX_URL='https://bittrex.com'

def get_bitfinex_symbols():
    response = requests.get(BITFINEX_URL + '/v1/symbols')
    symbols = response.json()
    return [(symbol[:3].upper(), symbol[3:].upper()) for symbol in symbols]

def get_bittrex_symbols():
    response = requests.get(BITTREX_URL + '/api/v1.1/public/getmarkets')
    markets = response.json()['result']
    return [(m['MarketCurrency'], m['BaseCurrency']) for m in markets]

def currency_symbol_to_char(symbol):
    if symbol == 'USD' or symbol == 'USDT':
        return '$'
    if symbol == 'BTC':
        return '₿'
    return ''

def build_symbol_buttons(symbols, widget_script_fun, action_script_fun, modifier_key=None):
    buttons = []
    for i, symbol in enumerate(symbols):
        button = {
            'BTTWidgetName': ':'.join(symbol),
            'BTTTriggerType': 639,
            'BTTTriggerTypeDescription': 'Apple Script Widget',
            'BTTTriggerClass': 'BTTTriggerTypeTouchBar',
            'BTTPredefinedActionType': 172,
            'BTTPredefinedActionName': 'Run Apple Script (enter directly as text)',
            'BTTInlineAppleScript': action_script_fun(symbol),
            'BTTEnabled': 1,
            'BTTOrder': i + 1,
            'BTTTriggerConfig': {
                'BTTTouchBarItemIconHeight': 22,
                'BTTTouchBarItemIconWidth': 22,
                'BTTTouchBarItemPadding': 0,
                'BTTTouchBarFreeSpaceAfterButton': '5.000000',
                'BTTTouchBarButtonColor': '58.650001, 58.650001, 58.650001, 255.000000',
                'BTTTouchBarAlwaysShowButton': '0',
                'BTTTouchBarAppleScriptString': widget_script_fun(symbol),
                'BTTTouchBarAlternateBackgroundColor': '109.650002, 109.650002, 109.650002, 255.000000',
                'BTTTouchBarScriptUpdateInterval': 60
            }
        }
        if modifier_key is not None:
            button['BTTRequiredModifierKeys'] = modifier_key
        buttons.append(button)
    return buttons

def build_buttons(currencies, symbols, widget_script_fun, action_script_fun):
    symbol_buttons = []
    for currency, modifier_key in currencies.items():
        symbol_buttons += build_symbol_buttons(
            filter(lambda x: x[1] == currency, symbols),
            widget_script_fun, action_script_fun, modifier_key
        )
    close_button = {
      'BTTTouchBarButtonName': 'Close Group',
      'BTTTriggerType': 629,
      'BTTTriggerClass': 'BTTTriggerTypeTouchBar',
      'BTTPredefinedActionType': 191,
      'BTTPredefinedActionName': 'Close currently open Touch Bar group',
      'BTTEnabled': 1,
      'BTTOrder': 0,
      'BTTIconData': 'Standard Close Icon',
      'BTTTriggerConfig': {
        'BTTTouchBarItemIconHeight': 0,
        'BTTTouchBarItemIconWidth': 0,
        'BTTTouchBarItemPadding': 0,
        'BTTTouchBarButtonColor': '0.000000, 0.000000, 0.000000, 255.000000',
        'BTTTouchBarOnlyShowIcon': 1
      }
    }
    return [close_button] + symbol_buttons

def build_group(name, order, currencies, symbols, widget_script_fun, action_script_fun):
    buttons = build_buttons(currencies, symbols, widget_script_fun, action_script_fun)
    return {
        'BTTTouchBarButtonName': name,
        'BTTTriggerType': 630,
        'BTTTriggerClass': 'BTTTriggerTypeTouchBar',
        'BTTEnabled': 1,
        'BTTOrder': order,
        'BTTAdditionalActions': buttons
    }

bitfinex_symbols = get_bitfinex_symbols()
bitfinex_symbols.sort(key=lambda x: x[0])
bitfinex_group = build_group(
    'Bitfinex',
    0,
    {'USD': None, 'BTC': 524288},
    bitfinex_symbols,
    lambda x: '"' + x[0] + ': " & {do shell script "/usr/local/bin/redis-cli get ' + APP_NAME + ':bitfinex:' + ':'.join(x) + '"} & " ' + currency_symbol_to_char(x[1]) + '"',
    lambda x: "tell application \"Google Chrome\"\r\tactivate\r\topen location \"https://www.bitfinex.com/t/" + ':'.join(x) + "\"\rend tell"
)

bittrex_symbols = get_bittrex_symbols()
bittrex_symbols.sort(key=lambda x: x[0])
bittrex_group = build_group(
    'Bittrex',
    1,
    {'USDT': None, 'BTC': 524288},
    bittrex_symbols,
    lambda x: '"' + x[0] + ': " & {do shell script "/usr/local/bin/redis-cli get ' + APP_NAME + ':bittrex:' + ':'.join(x) + '"} & " ' + currency_symbol_to_char(x[1]) + '"',
    lambda x: "tell application \"Google Chrome\"\r\tactivate\r\topen location \"https://bittrex.com/Market/Index?MarketName=" + '-'.join(reversed(x)) + "\"\rend tell"
)

groups = [bitfinex_group, bittrex_group]

print(json.dumps(groups, indent=2))
