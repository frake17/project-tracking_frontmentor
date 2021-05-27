from datetime import date, timedelta, datetime
# dt = date.today() + timedelta(1)
# y = date.today() + timedelta(days=1)
# print(y.strftime('%d %B'))
# hour = int(x.strftime('%H'))
# print(hour)
# if hour == 0:
# print(12)

x = datetime.now()
y = datetime.now()
y += timedelta(100)
c = datetime(2021, 1, 30)
diff = y - x
days = diff.days
if days == 100:
    print('test')

print(x.hour)
if x.hour > 1:
    print('1')
elif x.hour > 2:
    print(2)