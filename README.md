# snowball
Конвертер из Intelinvest в Snowball Income

Как использовать:
1. Скачать репозиторий
2. Перейти в папку snowball
3. Положить туда же файл с выгрузкой из intelinvest.
3.1. Если в intellinvest использовали пользовательские активы, шапку от них нужно вырезать из файла, чтобы получился стандартный csv.
4. В консоли|терминале выполнить

python3 intelinvest.py <report_from_intelinvest>.csv

Получится файл, который нужно загрузить в snowball-income
