require 'json'
require 'net/http'

def get_bitfinex_symbols
  url = URI('https://api.bitfinex.com/v1/symbols')
  http = Net::HTTP.new(url.host, url.port)
  http.use_ssl = true
  request = Net::HTTP::Get.new(url)
  response = http.request(request)
  symbols = JSON.parse(response.read_body)
  symbols.map { |s| [s[0..2].upcase, s[3..-1].upcase] }
end

def get_bittrex_symbols
  url = URI('https://bittrex.com/api/v1.1/public/getmarkets')
  http = Net::HTTP.new(url.host, url.port)
  http.use_ssl = true
  request = Net::HTTP::Get.new(url)
  response = http.request(request)
  markets = JSON.parse(response.read_body)['result']
  markets.map { |m| [m['MarketCurrency'], m['BaseCurrency']] }
end

def build_group(name, order, symbols, widget_script_fun, action_script_fun)
  symbol_buttons = symbols.map.with_index(1) do |symbol, i|
    {
      'BTTWidgetName' => symbol.join(':'),
      'BTTTriggerType' => 639,
      'BTTTriggerTypeDescription' => 'Apple Script Widget',
      'BTTTriggerClass' => 'BTTTriggerTypeTouchBar',
      'BTTPredefinedActionType' => 172,
      'BTTPredefinedActionName' => 'Run Apple Script (enter directly as text)',
      'BTTInlineAppleScript' => action_script_fun.call(symbol),
      'BTTEnabled' => 1,
      'BTTOrder' => i,
      'BTTTriggerConfig' => {
        'BTTTouchBarItemIconHeight' => 22,
        'BTTTouchBarItemIconWidth' => 22,
        'BTTTouchBarItemPadding' => 0,
        'BTTTouchBarFreeSpaceAfterButton' => '5.000000',
        'BTTTouchBarButtonColor' => '58.650001, 58.650001, 58.650001, 255.000000',
        'BTTTouchBarAlwaysShowButton' => '0',
        'BTTTouchBarAppleScriptString' => widget_script_fun.call(symbol),
        'BTTTouchBarAlternateBackgroundColor' => '109.650002, 109.650002, 109.650002, 255.000000',
        'BTTTouchBarScriptUpdateInterval' => 60
      }
    }
  end

  buttons = [
    {
      'BTTTouchBarButtonName' => 'Close Group',
      'BTTTriggerType' => 629,
      'BTTTriggerClass' => 'BTTTriggerTypeTouchBar',
      'BTTPredefinedActionType' => 191,
      'BTTPredefinedActionName' => 'Close currently open Touch Bar group',
      'BTTEnabled' => 1,
      'BTTOrder' => 0,
      'BTTIconData' => 'Standard Close Icon',
      'BTTTriggerConfig' => {
        'BTTTouchBarItemIconHeight' => 0,
        'BTTTouchBarItemIconWidth' => 0,
        'BTTTouchBarItemPadding' => 0,
        'BTTTouchBarButtonColor' => '0.000000, 0.000000, 0.000000, 255.000000',
        'BTTTouchBarOnlyShowIcon' => 1
      }
    }
  ] + symbol_buttons

  {
    'BTTTouchBarButtonName' => name,
    'BTTTriggerType' => 630,
    'BTTTriggerClass' => 'BTTTriggerTypeTouchBar',
    'BTTEnabled' => 1,
    'BTTOrder' => order,
    'BTTAdditionalActions' => buttons
  }
end

bitfinex_symbols = get_bitfinex_symbols.sort_by(&:first)
bitfinex_group = build_group(
  'Bitfinex',
  0,
  bitfinex_symbols.select { |s| s.last == 'USD' },
  lambda do |symbol|
    "tell application \"JSON Helper\"\r\tset resp to (fetch JSON from \"https:\/\/api.bitfinex.com\/v1\/pubticker\/#{symbol.join.downcase}\")\r\tset price to last_price of resp as real\rend tell\rset result_string to \"#{symbol.first}: \" & {round(price * 100)} & \" \" & \"#{symbol.last}\"\rreturn result_string"
  end,
  lambda do |symbol|
    "tell application \"Google Chrome\"\r\tactivate\r\topen location \"https:\/\/www.bitfinex.com\/t\/#{symbol.join(':')}\"\rend tell"
  end
)

bittrex_symbols = get_bittrex_symbols.sort_by(&:first)
bittrex_group = build_group(
  'Bittrex',
  1,
  bittrex_symbols.select { |s| s.last == 'USDT' },
  lambda do |symbol|
    "tell application \"JSON Helper\"\r\tset resp to (fetch JSON from \"https:\/\/bittrex.com\/api\/v1.1\/public\/getticker?market=#{symbol.reverse.join('-')}\")\r\tset price to |last| of |result| of resp as number\rend tell\rset result_string to \"#{symbol.first}: \" & {round(price * 100)} & \" \" & \"#{symbol.last}\"\rreturn result_string"
  end,
  lambda do |symbol|
    "tell application \"Google Chrome\"\r\tactivate\r\topen location \"https:\/\/bittrex.com\/Market\/Index?MarketName=#{symbol.reverse.join('-')}\"\rend tell"
  end
)

groups = [bitfinex_group, bittrex_group]

puts(JSON.pretty_generate(groups))
