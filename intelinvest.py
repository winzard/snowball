import sys
import csv
import datetime
from decimal import Decimal
report_file_name = str(sys.argv[1])
event_mapping = {
    'STOCKBUY': 'Buy',
    'STOCKSELL': 'Sell',
    'BONDBUY': 'Buy',
    'BONDSELL': 'Sell',
    'COUPON': 'Dividend',
    'AMORTIZATION': 'Amortisation', # TODO сделать импорт амортизации
    'DIVIDEND': 'Dividend',
    'MONEYDEPOSIT': 'Cash_In',
    'MONEYWITHDRAW': 'Cash_Out',
    'INCOME': 'Cash_Gain',
    'LOSS': 'Cash_Expense',
    'CURRENCY_BUY': 'Cash_Convert',
    'CURRENCY_SELL': 'Cash_Convert',
}
with open(report_file_name, 'r') as fp:
    reader = csv.reader(fp, delimiter=';', )
    header = ['Event', 'Date', 'Symbol', 'Price', 'Quantity', 'Currency', 'FeeTax', 'Exchange', 'NKD', 'FeeCurrency']
    buffer = {}
    with open(report_file_name+'_snowball.csv', "w") as output:
        csv_iter = iter(reader)
        print(",".join(list(header)), file=output)
        for row in csv_iter:
            source = {
                'operation': row[0],
                'at': datetime.datetime.strptime(row[1], '%d.%m.%Y %H:%M:%S'),
                'ticker': row[2],
                'quantity': Decimal(row[3]) if row[3] else '',
                'price': Decimal(row[4]) if row[4] else '',
                'fee': Decimal(row[5]) if row[5] else '',
                'nkd': Decimal(row[6]) if row[6] else '',
                'nominal': Decimal(row[7]) if row[7] else '',
                'currency': row[8],
                'fee_currency': row[9],
                'note': row[10],
                'link': row[11]
            }
            dest = {
                'Event': '',
                'Date': datetime.datetime.strftime(source['at'], '%Y-%m-%d'),
                'Symbol': '',
                'Price': '',
                'Quantity': '',
                'Currency': '',
                'FeeTax': '',
                'Exchange': '',
                'NKD': '',
                'FeeCurrency': ''
            }
            if source['link']: # связанная сделка. Пихаем в буфер или ищем там пару и исполняем
                if source['link'] not in buffer:
                    buffer[source['link']] = source
                    continue
                else:
                    # есть связанная сделка
                    linked = buffer[source['link']]
                    if linked['operation'] == 'MONEYDEPOSIT' or linked['operation'] == 'MONEYWITHDRAW':
                        money = linked
                        event = source
                    else:
                        money = source
                        event = linked

                    if event['operation'] == 'CURRENCY_BUY':
                        dest['Event'] = 'Cash_Convert'
                        dest['Symbol'] = event['currency']
                        dest['Price'] = money['price']
                        dest['Quantity'] = event['price']
                        dest['Currency'] = money['currency']
                        dest['FeeTax'] = event['fee']
                        dest['Exchange'] = 'MCX'
                        dest['NKD'] = 0
                        dest['FeeCurrency'] = event['fee_currency']

                        print(",".join([str(f) for f in dest.values()]), file=output)
                        del buffer[source['link']]
                    elif event['operation'] == 'CURRENCY_SELL': # у меня пока нет таких операций
                        dest['Event'] = 'Cash_Convert'
                        dest['Symbol'] = event['currency']
                        dest['Price'] = money['price']
                        dest['Quantity'] = event['price']
                        dest['Currency'] = money['currency']
                        dest['FeeTax'] = event['fee']
                        dest['Exchange'] = 'MCX'
                        dest['NKD'] = 0
                        dest['FeeCurrency'] = event['fee_currency']

                        print(",".join([str(f) for f in dest.values()]), file=output)
                        del buffer[source['link']]
                    elif event['operation'] == 'STOCKBUY' or event['operation'] == 'STOCKSELL':
                        dest['Event'] = event_mapping[event['operation']]
                        dest['Symbol'] = event['ticker'] if not '.DE' in event['ticker'] else event['ticker'][0:-3]
                        dest['Price'] = event['price']
                        dest['Quantity'] = event['quantity']
                        dest['Currency'] = money['currency']
                        dest['FeeTax'] = event['fee']
                        dest['Exchange'] = 'MCX' if money['currency'] == 'RUB' else 'SPB'
                        dest['NKD'] = 0
                        dest['FeeCurrency'] = event['fee_currency']
                        print(",".join([str(f) for f in dest.values()]), file=output)
                        del buffer[source['link']]
                    elif event['operation'] == 'BONDBUY' or event['operation'] == 'BONDSELL':
                        dest['Event'] = event_mapping[event['operation']]
                        dest['Symbol'] = event['ticker'] if not '.DE' in event['ticker'] else event['ticker'][0:-3]
                        dest['Price'] = event['price']*event['nominal']/Decimal(100) # проценты и номинал надо учитывать
                        dest['Quantity'] = event['quantity']
                        dest['Currency'] = money['currency']
                        dest['FeeTax'] = event['fee']
                        dest['Exchange'] = 'MCX'
                        dest['NKD'] = event['nkd']
                        dest['FeeCurrency'] = money['currency']
                        print(",".join([str(f) for f in dest.values()]), file=output)
                        del buffer[source['link']]
                    elif event['operation'] == 'LOSS' or event['operation'] == 'INCOME':
                        dest['Event'] = event_mapping[event['operation']]
                        dest['Symbol'] = money['currency']
                        dest['Price'] = 1
                        dest['Quantity'] = money['price']
                        dest['Currency'] = money['currency']
                        dest['FeeTax'] = 0
                        dest['Exchange'] = ''
                        dest['NKD'] = ''
                        dest['FeeCurrency'] = ''
                        print(",".join([str(f) for f in dest.values()]), file=output)
                        del buffer[source['link']]
                    elif event['operation'] == 'COUPON' or event['operation'] == 'DIVIDEND':
                        # связанная сделка с купоном или дивидендом - деньги зачисляются
                        dest['Event'] = event_mapping[event['operation']]
                        dest['Symbol'] = event['ticker'] if not '.DE' in event['ticker'] else event['ticker'][0:-3]
                        dest['Price'] = event['price']
                        dest['Quantity'] = money['price'] #* Decimal(0.87)  # intelinvest 13% вычитает
                        dest['Currency'] = event['currency']
                        dest['FeeTax'] = 0 #money['price'] * Decimal(0.13)
                        dest['Exchange'] = ''
                        dest['NKD'] = 0
                        dest['FeeCurrency'] = ''
                        print(",".join([str(f) for f in dest.values()]), file=output)
                        del buffer[source['link']]

            else:
                # несвязанная сделка, это ввод или вывод денег
                event = source
                if event['operation'] == 'MONEYDEPOSIT':
                    dest['Event'] = 'Cash_In'
                    dest['Symbol'] = event['currency']
                    dest['Price'] = 1
                    dest['Quantity'] = event['price']
                    dest['Currency'] = event['currency']
                    dest['FeeTax'] = 0
                    dest['Exchange'] = ''
                    dest['NKD'] = 0
                    dest['FeeCurrency'] = ''

                    print(",".join([str(f) for f in dest.values()]), file=output)
                elif event['operation'] == 'MONEYWITHDRAW':
                    dest['Event'] = 'Cash_Out'
                    dest['Symbol'] = event['currency']
                    dest['Price'] = 1
                    dest['Quantity'] = event['price']
                    dest['Currency'] = event['currency']
                    dest['FeeTax'] = 0
                    dest['Exchange'] = ''
                    dest['NKD'] = 0
                    dest['FeeCurrency'] = ''

                    print(",".join([str(f) for f in dest.values()]), file=output)
                elif event['operation'] == 'COUPON' or event['operation'] == 'DIVIDEND':
                    # несвязанная сделка - выводим сумму TODO проверить налоги
                    dest['Event'] = event_mapping[event['operation']]
                    dest['Symbol'] = event['ticker'] if not '.DE' in event['ticker'] else event['ticker'][0:-3]
                    dest['Price'] = event['price']
                    dest['Quantity'] = event['price']*event['quantity'] # intelinvest 13% вычитает
                    dest['Currency'] = event['currency']
                    dest['FeeTax'] = 0 # event['price']*event['quantity']*Decimal(0.13)
                    dest['Exchange'] = ''
                    dest['NKD'] = 0
                    dest['FeeCurrency'] = ''
                    print(",".join([str(f) for f in dest.values()]), file=output)
                    dest['Event'] = 'Cash_Out'
                    # dest['Symbol'] = event['currency']
                    dest['Price'] = 1
                    dest['Quantity'] = event['price'] * event['quantity']
                    # dest['Quantity'] = event['price']
                    # dest['Currency'] = event['currency']
                    dest['FeeTax'] = 0
                    # dest['Exchange'] = 'MCX'
                    dest['NKD'] = 0
                    dest['FeeCurrency'] = ''

                    print(",".join([str(f) for f in dest.values()]), file=output)
