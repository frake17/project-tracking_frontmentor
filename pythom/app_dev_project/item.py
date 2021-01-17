class Shop_item:
    count_id = 0
    quantity = 0

    def __init__(self, stock_name, supplier_name, price, origin, weight, dietary, ingre, description,amt_of_stock, category):
        Shop_item.count_id += 1
        self.__amount = Shop_item.quantity
        self.__id = Shop_item.count_id
        self.__stock_name = stock_name
        self.__supplier_name = supplier_name
        self.__price = price
        self.__origin = origin
        self.__weight = weight
        self.__dietary = dietary
        self.__ingredients = ingre
        self.__description = description
        self.__amt_of_stock = amt_of_stock
        self.__stock_left = amt_of_stock
        self.__category = category
        self.__total = 0

    def get_id(self):
        return int(self.__id)

    def get_stock_name(self):
        return self.__stock_name

    def get_supplier_name(self):
        return self.__supplier_name

    def get_price(self):
        self.__total = Shop_item.quantity * int(self.__price)
        return self.__total

    def get_origin(self):
        return self.__origin

    def get_dietary(self):
        return self.__dietary

    def get_weight(self):
        return self.__weight

    def get_ingredients(self):
        return self.__ingredients

    def get_description(self):
        return self.__description

    def get_amt_of_stock(self):
        return self.__amt_of_stock

    def get_stock_left(self):
        return int(self.__stock_left)

    def get_percentage(self):
        percentage = (int(self.__stock_left) / int(self.__amt_of_stock)) * 100
        return round(percentage)

    def get_cat(self):
        return self.__category

    def get_base_price(self):
        return self.__price

    def get_category(self):
        return self.__category

    def set_stock_name(self, stock_name):
        self.__stock_name = stock_name

    def set_supplier_name(self, supplier_name):
        self.__supplier_name = supplier_name

    def set_price(self, price):
        self.__price = price

    def set_origin(self, origin):
        self.__origin = origin

    def set_dietary(self, dietary):
        self.__dietary = dietary

    def set_weight(self, weight):
        self.__weight = weight

    def set_ingredients(self, ingredients):
        self.__ingredients = ingredients

    def set_description(self, description):
        self.__description = description

    def set_amt_of_stock(self, amt_of_stock):
        self.__amt_of_stock = amt_of_stock

    def set_stock_left(self, stock_left):
        self.__stock_left = stock_left

    def set_id(self, id):
        self.__id = id

    def set_cat(self, cat):
        self.__category = cat

    def set_amount_empty(self):
        Shop_item.quantity = 0

    def add_amount(self):
        Shop_item.quantity += 1
        self.__amount = Shop_item.quantity

    def minus(self):
        Shop_item.quantity -= 1
        self.__amount = Shop_item.quantity

    def get_amount(self):
        return self.__amount

    def decrease_stock(self):
        self.__stock_left -= 1


class Restock:
    count_id = 0

    def __init__(self, email, order_number):
        Restock.count_id += 1
        self.__id = Restock.count_id
        self.__email = email
        self.__order_number = order_number

    def get_id(self):
        return self.__id

    def get_email(self):
        return self.__email

    def get_order(self):
        return self.__order_number

    def set_email(self, email):
        self.__email = email

    def set_order(self, order):
        self.__order_number = order

    def set_id(self, id):
        self.__id = id


class Order_delivery:
    count_id = 0

    def __init__(self, name,number,postal,address,level,door_no,card_no,exp_date,cvv,card_type, location, remkarks):
        Order_delivery.count_id += 1
        self.__id = Order_delivery.count_id
        self.__name = name
        self.__phone_no = number
        self.__postal = postal
        self.__address = address
        self.__level = level
        self.__door_no = door_no
        self.__card_no = card_no
        self.__exp_Date = exp_date
        self.__cvv = cvv
        self.__card = card_type
        self.__location = location
        self.__date = ""
        self.__remark = remkarks

    def get_name(self):
        return self.__name

    def get_remark(self):
        return self.__remark

    def get_location(self):
        return self.__location

    def get_phone(self):
        return self.__phone_no

    def get_postal(self):
        return self.__postal

    def get_address(self):
        return self.__address

    def get_level(self):
        return self.__level

    def get_door(self):
        return self.__door_no

    def get_card_no(self):
        return self.__card_no

    def get_exp_date(self):
        return self.__exp_Date

    def get_cvv(self):
        return self.__cvv

    def get_id(self):
        return self.__id

    def get_card(self):
        return self.__card

    def get_date(self):
        return self.__date

    def set_card(self, card):
        self.__card = card

    def set_id(self, id):
        self.__id = id

    def set_date(self, date):
        self.__date = date


class Order_self:
    count_id = 0

    def __init__(self, name, number, card_no, exp, cvv, card_type):
        Order_self.count_id += 1
        self.__id = Order_self.count_id
        self.__name = name
        self.__number = number
        self.__card_no = card_no
        self.__exp = exp
        self.__cvv = cvv
        self.__date = ""
        self.__location = ""
        self.__time = ""
        self.__card = card_type

    def get_name(self):
        return self.__name

    def get_number(self):
        return self.__number

    def get_card_no(self):
        return self.__card_no

    def get_exp(self):
        return self.__exp

    def get_date(self):
        return self.__date

    def get_location(self):
        return self.__location

    def get_time(self):
        return self.__time

    def get_id(self):
        return self.__id

    def get_cvv(self):
        return self.__cvv

    def get_card(self):
        return self.__card

    def set_date(self, date):
        self.__date = date

    def set_location(self, location):
        self.__location = location

    def set_time(self, time):
        self.__time = time

    def set_card(self, card):
        self.__card = card

    def set_id(self, id):
        self.__id = id
