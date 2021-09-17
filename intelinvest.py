import sys
import csv
import datetime
from decimal import Decimal
report_file_name = str(sys.argv[1])
event_mapping = {
    'STOCKBUY': '',
    'STOCKSELL': '',
    'BONDBUY': '',
    'BONDSELL': '',
    'COUPON': '',
    'AMORTIZATION': '',
    'DIVIDEND': '',
    'MONEYDEPOSIT': '',
    'MONEYWITHDRAW': '',
    'INCOME': '',
    'LOSS': '',
    'CURRENCY_BUY': '',
    'CURRENCY_SELL': '',
}
with open(report_file_name, 'r') as fp:
    reader = csv.reader(fp, delimiter=';', )
    with open(report_file_name+'_snowball.csv', "w") as output:
        csv_iter = iter(reader)
        results = list()
        for row in csv_iter:
            res = {
                'operation': row[0],
                'at': datetime.datetime.strptime(row[1], '%d.%m.%Y %h:%M:%s'),
                'ticker': row[2],
                'quantity': Decimal(row[3]),
                'price': Decimal(row[4]),
                'fee': Decimal(row[4]),
                'nominal': Decimal(row[5]),
                'currency': row[6],
                'fee_currency': Decimal(row[7]),
                'note': row[8],
                'link': row[9]
            }
            results.append(res)
        for transaction in transactions:
            name = transaction.find(attrs={"class": "trs_name"}).string.strip()
            if name[0] == "\"" and name[-1] == "\"":
                name = name.strip("\"")
            data = transaction.find(attrs={"class": "idate"})['data-date']
            summ_tag = transaction.find(attrs={"class": "trs_sum"})
            income = summ_tag.find(attrs={"class": "trs_st-refill"})
            summ = summ_tag.get_text().strip()
            if not income:
                summ = '-' + summ
            category = transaction.find(attrs={"class": "icat"}).get_text().strip()
            print(",".join([name, data, summ, category]), file=output)