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
    'AMORTIZATION': 'Amortisation',
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
                'at': datetime.datetime.strptime(row[1], '%d.%m.%Y %h:%M:%s'),
                'ticker': row[2],
                'quantity': Decimal(row[3]),
                'price': Decimal(row[4]),
                'fee': Decimal(row[4]),
                'nkd': Decimal(row[5]),
                'nominal': Decimal(row[6]),
                'currency': row[7],
                'fee_currency': Decimal(row[8]),
                'note': row[9],
                'link': row[10]
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

                        print(",".join(list(dest.values())), file=output)
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

                        print(",".join(list(dest.values())), file=output)
                        del buffer[source['link']]
                    elif event['operation'] == 'STOCKBUY' or event['operation'] == 'STOCKSELL':
                        dest['Event'] = event_mapping[event['operation']]
                        dest['Symbol'] = event['ticker']
                        dest['Price'] = event['price']
                        dest['Quantity'] = event['quantity']
                        dest['Currency'] = money['currency']
                        dest['FeeTax'] = event['fee']
                        dest['Exchange'] = 'MCX' if money['currency'] == 'RUB' else 'SPB'
                        dest['NKD'] = 0
                        dest['FeeCurrency'] = event['fee_currency']
                        print(",".join(list(dest.values())), file=output)
                        del buffer[source['link']]
                    elif event['operation'] == 'BONDBUY' or event['operation'] == 'BONDSELL':
                        dest['Event'] = event_mapping[event['operation']]
                        dest['Symbol'] = event['ticker']
                        dest['Price'] = event['price']
                        dest['Quantity'] = event['quantity']
                        dest['Currency'] = money['currency']
                        dest['FeeTax'] = event['fee']
                        dest['Exchange'] = 'MCX'
                        dest['NKD'] = event['nkd']
                        dest['FeeCurrency'] = money['currency']
                        print(",".join(list(dest.values())), file=output)
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
                        print(",".join(list(dest.values())), file=output)
                        del buffer[source['link']]

            else:
                # несвязанная сделка, это ввод или вывод денег
                event = source
                if event['operation'] == 'MONEYDEPOSIT':
                    dest['Event'] = 'Cash_In'
                    dest['Symbol'] = event['currency']
                    dest['Price'] = 1
                    dest['Quantity'] = event['price']
                    dest['Currency'] = money['currency']
                    dest['FeeTax'] = 0
                    dest['Exchange'] = 'MCX'
                    dest['NKD'] = 0
                    dest['FeeCurrency'] = ''

                    print(",".join(list(dest.values())), file=output)
                elif event['operation'] == 'MONEYWITHDRAW':
                    dest['Event'] = 'Cash_Out'
                    dest['Symbol'] = event['currency']
                    dest['Price'] = 1
                    dest['Quantity'] = event['price']
                    dest['Currency'] = money['currency']
                    dest['FeeTax'] = 0
                    dest['Exchange'] = 'MCX'
                    dest['NKD'] = 0
                    dest['FeeCurrency'] = ''

                    print(",".join(list(dest.values())), file=output)
                elif event['operation'] == 'COUPON' or event['operation'] == 'DIVIDEND':
                    dest['Event'] = event_mapping[event['operation']]
                    dest['Symbol'] = event['ticker']
                    dest['Price'] = event['price']
                    dest['Quantity'] = event['price']*event['quantity']/0.87 # intelinvest 13% вычитает
                    dest['Currency'] = event['currency']
                    dest['FeeTax'] = dest['Quantity']*0.13
                    dest['Exchange'] = 'MCX'
                    dest['NKD'] = 0
                    dest['FeeCurrency'] = ''
                    print(",".join(list(dest.values())), file=output)
