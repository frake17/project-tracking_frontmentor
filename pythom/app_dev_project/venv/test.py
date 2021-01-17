import shelve

supply = {'1': '1'}
supplies = {'2': '2'}
add_supplies = {'3': '3'}
supply_2 = {}
supplies_2 = {}
add_supplies_2 = {}

db = shelve.open('test.db', 'c')
db['1'] = supply
db['2'] = supplies
db['3'] = add_supplies
db.close()

db = shelve.open('test.db', 'c')
supply_2 = db['1']
supplies_2 = db['2']
add_supplies_2 = db['3']
print(supply_2)
print(supplies_2)
print(add_supplies_2)