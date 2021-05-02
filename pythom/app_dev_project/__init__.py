import os
import shelve
from datetime import timedelta, datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint

import Location
import User
import item
from Forms import Shop, Order, Restock, self_collect, Supplier, SignUp, Login, CreateLocation, CreateDeliverymen, CreateUserForm, SearchUserForm
from alicia import alicia

UPLOAD_FOLDER = 'static/img/uploaded'
ALLOWED_EXTENSIONS = {'png'}

app = Flask(__name__)
app.secret_key = 'any_random_string'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["SESSION_PERMANENT"] = False
app.register_blueprint(alicia)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/stock', methods=['GET', 'POST'])
def stock():
    users_dict = {}
    db = shelve.open('storage.db', 'c')
    try:
        users_dict = db['item']
    except:
        print("Error in retrieving Users from storage.db.")

    item_list = []
    for key in users_dict:
        user = users_dict.get(key)
        item_list.append(user)

    if request.method == 'POST':
        percentage = int(request.form['percentage'])
        db['percentage'] = percentage
    else:
        try:
            percentage = db['percentage']
        except:
            percentage = 20

    db.close()
    return render_template('stock.html', item_list=item_list, percentage=percentage)


@app.route('/shop_admin', defaults={'sort': None})
@app.route('/shop_admin/<sort>')
def shop(sort):
    users_dict = {}
    try:
        db = shelve.open('storage.db', 'r')
        users_dict = db['item']
        db.close()
    except:
        print("Error in retrieving Users from storage.db.")

    item_list = []
    for key in users_dict:
        user = users_dict.get(key)
        item_list.append(user)

    return render_template('shop_admin.html', item_list=item_list)


@app.route('/shop_cus', defaults={'sort': None})
@app.route('/shop_cus/<sort>')
def shop_cus(sort):
    users_dict = {}
    try:
        db = shelve.open('storage.db', 'r')
        users_dict = db['item']
        db.close()
    except:
        print("Error in retrieving Users from storage.db.")

    item_list = []
    for key in users_dict:
        user = users_dict.get(key)
        item_list.append(user)

    if sort == 'alphabet':
        item_list.sort(key=lambda x: x.get_stock_name())
    elif sort == 'Low_to_high_price':
        item_list.sort(key=lambda x: x.get_base_price())
    elif sort == 'High_to_low_price':
        item_list.sort(key=lambda x: x.get_base_price(), reverse=True)
    elif sort == 'brand_AtoZ':
        item_list.sort(key=lambda x: x.get_brand())
    elif sort == 'brand_ZtoA':
        item_list.sort(key=lambda x: x.get_brand(), reverse=True)
    return render_template('shop_cus.html', item_list=item_list)


@app.route('/shop_display')
def display():
    return render_template('shop_item_display.html')


@app.route('/cart/<int:product_id>', methods=['POST', 'GET'])  # done with {user:{id:item}}
def add(product_id):
    cart_dict = {}
    email_cart_dict = {}
    db = shelve.open('storage.db', 'c')
    try:
        email = session.get('current')
    except:
        print('no email in session')
        return url_for('login')

    try:
        email_cart_dict = db['Cart']
        if email in email_cart_dict:
            cart_dict = email_cart_dict.get(email)
    except:
        print('das')

    shop_dict = db['item']
    print('***', cart_dict)

    item_list = []  # get object of stocks
    for key in shop_dict:
        user = shop_dict.get(key)
        item_list.append(user)

    for item in item_list:  # adding to cart
        id = item.get_id()
        if product_id in cart_dict:
            item_cart = cart_dict.get(product_id)
            item_cart.add_amount()
            session['cart_added'] = item_cart.get_stock_name()
            break
        else:
            if id == product_id:
                item.add_amount()
                cart_dict[item.get_id()] = item
                session['cart_added'] = item.get_stock_name()
                break

    email_cart_dict[email] = cart_dict
    db['Cart'] = email_cart_dict
    db.close()

    return redirect(url_for('shop_cus'))


@app.route('/add/<int:product_id>')
def add_change(product_id):
    cart_dict = {}
    email_cart_dict = {}
    db = shelve.open('storage.db', 'c')
    email = session.get('current')

    try:
        email_cart_dict = db['Cart']
        if email in email_cart_dict:
            cart_dict = email_cart_dict.get(email)
    except:
        print('das')

    item = cart_dict.get(product_id)
    item.add_amount()
    email_cart_dict[email] = cart_dict
    db['Cart'] = email_cart_dict
    db.close()

    return redirect(url_for('cart'))


@app.route('/minus/<int:product_id>')
def minus_change(product_id):
    cart_dict = {}
    email_cart_dict = {}
    db = shelve.open('storage.db', 'c')
    email = session.get('current')

    try:
        email_cart_dict = db['Cart']
        if email in email_cart_dict:
            cart_dict = email_cart_dict.get(email)
    except:
        print('das')

    item = cart_dict.get(product_id)
    if item.get_amount() > 0:
        item.minus()
    email_cart_dict[email] = cart_dict
    db['Cart'] = email_cart_dict
    db.close()

    return redirect(url_for('cart'))


@app.route('/cart')  # done with {user:{id:item}}
def cart():
    cart_list = {}
    email_cart_dict = {}
    db = shelve.open('storage.db', 'c')
    item_list = []
    total = 0
    try:
        email = session.get('current')
        email_cart_dict = db['Cart']
        cart_list = email_cart_dict.get(email)
        for key in cart_list:
            user = cart_list.get(key)
            price = user.get_price()
            total += int(price)
            item_list.append(user)
    except:
        print('error')
        session['empty_cart'] = 'cart is empty'
        return redirect(url_for('shop_cus'))
    session['Total_price'] = total

    return render_template('cart.html', item_list=item_list, price=total)


@app.route('/clear_cart')
def clear():
    email = session.get('current')
    db = shelve.open('storage.db', 'c')
    try:
        email_cart_dict = db['Cart']
        email_cart_dict[email] = {}
        db['Cart'] = email_cart_dict
    except:
        print('email not in dict')

    return redirect(url_for('shop_cus'))


@app.route('/delivery', methods=['POST', 'GET'])
def delivery():
    total = session.get('Total_price', None)
    date_now = datetime.now()
    max_date = date_now + timedelta(60)
    if total > 100:
        total = total
    else:
        total = total + 3
    if request.method == 'POST':
        date = request.form['date']
        input_date = datetime(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2]))
        if input_date > max_date:
            session['invalid_date'] = date + ' is invalid. Please choose another date'
            redirect(url_for('delivery'))
        elif input_date < date_now:
            session['invalid_date'] = date + ' is invalid. Please choose another date'
            redirect(url_for('delivery'))
        else:
            session['date'] = date
            return redirect(url_for('order'))
    session['Total_price'] = total
    return render_template('delivery_date.html', total=total)


@app.route('/self-collect', methods=['POST', 'GET'])
def collect():
    total = session.get('Total_price', None)
    db = shelve.open('location.db', 'c')
    locations_dict = db['Locations']
    locations_list = []
    for key in locations_dict:
        location = locations_dict.get(key)
        locations_list.append(location)
    date_now = datetime.now()
    max_date = date_now + timedelta(30)
    date_now_hour = date_now.hour

    if request.method == 'POST':
        date = request.form['date']
        input_date = datetime(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2]))
        time = request.form['time']
        input_hour = time[0]
        print(input_date, max_date)
        if input_date > max_date:
            session['invalid_date'] = date + ' is invalid. Please choose another date'
            redirect(url_for('collect'))
        elif input_date == date_now:
            if input_hour <= date_now.hour:
                session['invalid_time'] = input_hour + ' is invalid. Please choose another timing'
                redirect(url_for('collect'))
        elif input_date < date_now:
            session['invalid_date'] = date + ' is invalid. Please choose another date'
            redirect(url_for('collect'))
        else:
            location = request.form['location']
            session['date'] = date
            session['time'] = time
            session['location'] = location
            return redirect(url_for('order_self'))
    session['Total_price'] = total
    return render_template('self_collect_details.html', total=total, stores=locations_list)


@app.route('/order', methods=['GET', 'POST'])
def order():
    count = 1
    date = session.get('date', None)
    create_order = Order(request.form)
    if request.method == 'POST' and create_order.validate():
        users_dict = {}
        db = shelve.open('storage.db', 'c')
        try:
            users_dict = db['orders_delivery']
            while count in users_dict:
                count += 1
        except:
            print('Error in retrieving users from db')

        order_item = item.Order_delivery(create_order.name.data, create_order.number.data, create_order.postal.data,
                                         create_order.address.data, create_order.level.data,
                                         create_order.door_number.data, create_order.card_number.data,
                                         create_order.exp_date.data, create_order.cvv.data, create_order.card_type.data,
                                         create_order.general_location.data, create_order.remarks.data)
        order_item.set_card(create_order.card_type.data)
        order_item.set_id(count)  # To set new Id
        order_item.set_date(date)
        session['current_id_delivery'] = count
        users_dict[order_item.get_id()] = order_item
        db['orders_delivery'] = users_dict
        db.close()

        return redirect(url_for('summary'))
    return render_template('order_details_delivery.html', form=create_order)


@app.route('/order_self', methods=['POST', 'GET'])
def order_self():
    count = 1
    create_order_self = self_collect(request.form)
    date = session.get('date', None)
    location = session.get('location', None)
    time = session.get('time', None)
    if request.method == 'POST':
        users_dict = {}
        db = shelve.open('storage.db', 'c')
        try:
            users_dict = db['orders_self']
            while count in users_dict:
                count += 1
        except:
            print('error')
        order_item = item.Order_self(create_order_self.name.data, create_order_self.number.data,
                                     create_order_self.card_number.data,
                                     create_order_self.exp_date.data, create_order_self.cvv.data,
                                     create_order_self.card_type.data)
        order_item.set_date(date)
        order_item.set_location(location)
        order_item.set_time(time)
        order_item.set_id(count)
        session['current_id_self'] = count
        users_dict[order_item.get_id()] = order_item
        db['orders_self'] = users_dict
        db.close()

        return redirect(url_for('summary_self'))

    return render_template('order_details_collect.html', form=create_order_self)


@app.route('/summary')
def summary():
    email = session.get('current')
    order_list = {}  # store order
    item_dict = {}  # get dict of stocks
    item_list = []  # for displaying in html

    db = shelve.open('storage.db', 'c')
    order_list = db['orders_delivery']
    item_dict = db['item']
    email_cart_dict = db['Cart']
    cart_dict = email_cart_dict.get(email)

    for key in order_list:  # for displaying in html
        user = order_list.get(key)
        item_list.append(user)

    # for key in cart_dict:
    #   item = cart_dict.get(key)
    #  for i in range(item.get_amount()):
    #     item.decrease_stock()
    # item.set_amount_empty()
    # item_dict[item.get_id()] = item

    current_id = session.get('current_id_delivery')
    current = order_list.get(current_id)
    current.set_item(cart_dict)

    db['item'] = item_dict
    db.close()

    return render_template('Order_delivery_confirmation.html', item_list=item_list, current=current)


@app.route('/summary_self')
def summary_self():
    email = session.get('current')
    order_list = {}  # store order
    item_dict = {}  # get dict of stocks
    item_list = []  # for displaying in html (delete once intergrate with qing)

    db = shelve.open('storage.db', 'c')
    order_list = db['orders_self']
    item_dict = db['item']
    email_cart_dict = db['Cart']
    cart_dict = email_cart_dict.get(email)

    for key in order_list:  # for displaying in html (delete once intergrate with qing)
        user = order_list.get(key)
        item_list.append(user)

    # for key in cart_dict:
    # item = cart_dict.get(key)
    # for i in range(item.get_amount()):
    #    item.decrease_stock()
    # item.set_amount_empty()
    # item_dict[item.get_id()] = item

    current_id = session.get('current_id_self', None)
    current = order_list.get(current_id)
    current.set_item(cart_dict)

    db['item'] = item_dict
    db.close()

    return render_template('Order_collect_confirmation.html', item_list=item_list, current=current)


@app.route('/summary_restock')
def summary_restock():
    order_list = {}
    clear_dict = {}
    item_dict = {}
    item_list = []
    db = shelve.open('storage.db', 'c')
    order_list = db['restock']
    db['Cart'] = clear_dict
    item_dict = db['item']

    for key in order_list:
        user = order_list.get(key)
        item_list.append(user)

    for key in item_dict:
        item = item_dict.get(key)
        item.set_amount_empty()
    db['item'] = item_dict

    current_id = session.get('current_id_restock', None)
    current = order_list.get(current_id)

    return render_template('restock_summary.html', item_list=item_list, current=current)


@app.route('/Delete_order/<delivery_collect>/<int:id>')
def delete_order(delivery_collect, id):
    db = shelve.open('storage.db', 'c')
    if delivery_collect == 'delivery':
        order_dict = db['orders_delivery']
        order_dict.pop(id)
        db['orders_delivery'] = order_dict
    else:
        order_dict = db['orders_self']
        order_dict.pop(id)
        db['orders_self'] = order_dict
    db.close()
    return redirect(url_for('shop_cus'))


@app.route('/sent_order/<delivery_collect>/<int:id>')
def sent_order(delivery_collect, id):
    email = session.get('current')
    db = shelve.open('storage.db', 'c')
    email_cart_dict = db['Cart']
    item_dict = db['item']
    cart_dict = email_cart_dict.get(email)
    order_item = {}
    confirmed_delivery = {}
    confirmed_collect = {}
    try:
        confirmed_delivery = db['confirmed_delivery']
        confirmed_collect = db['confirmed_collect']
    except:
        print('No confirmed orders yet')
    for key in cart_dict:
        item = cart_dict.get(key)
        order_item[item.get_stock_name()] = item.get_amount()

    if delivery_collect == 'delivery':
        orders_delivery = db['orders_delivery']
        current_order = orders_delivery.get(id)
        current_order.set_item(order_item)
        confirmed_delivery[id] = current_order
        db['confirmed_delivery'] = confirmed_delivery
        orders_delivery.pop(id)
        db['orders_delivery'] = orders_delivery
    else:
        orders_collect = db['orders_self']
        current_order = orders_collect.get(id)
        current_order.set_item(order_item)
        confirmed_collect[id] = current_order
        db['confirmed_collect'] = confirmed_collect
        orders_collect.pop(id)
        db['orders_self'] = orders_collect

    for key in cart_dict:
        item = cart_dict.get(key)
        for i in range(item.get_amount()):
            item.decrease_stock()
        item.set_amount_empty()
        item_dict[item.get_id()] = item

    email_cart_dict.pop(email)
    db['Cart'] = email_cart_dict
    db['item'] = item_dict
    db.close()
    return redirect(url_for('shop_cus'))


@app.route('/edit_delivery_order/<int:id>', methods=['POST'])
def edit_order(id):
    db = shelve.open('storage.db', 'c')
    update_order = Order(request.form)
    order_dict = {}
    if request.method == 'POST':
        order_dict = db['orders_delivery']

        current_order = order_dict.get(id)
        current_order.set_name(update_order.name.data)
        current_order.set_phone(update_order.number.data)
        current_order.set_postal(update_order.postal.data)
        current_order.set_address(update_order.address.data)
        current_order.set_level(update_order.level.data)
        current_order.set_door_no(update_order.door_number.data)
        current_order.set_card(update_order.card_type.data)
        current_order.set_exp(update_order.exp_date.data)
        current_order.set_ccv(update_order.cvv.data)
        current_order.set_card_no(update_order.card_number.data)
        current_order.set_location(update_order.general_location.data)
        current_order.set_remark(update_order.remarks.data)

        db['orders_delivery'] = order_dict
        db.close()
        return redirect(url_for('summary'))

    else:
        order_dict = db['orders_delivery']

        current_order = order_dict.get(id)
        update_order.name.data = current_order.get_name()
        update_order.number.data = current_order.get_phone()
        update_order.postal.data = current_order.get_postal()
        update_order.address.data = current_order.get_address()
        update_order.level.data = current_order.get_level()
        update_order.door_number.data = current_order.get_door()
        update_order.card_type.data = current_order.get_card()
        update_order.exp_date.data = current_order.get_exp_date()
        update_order.cvv.data = current_order.get_cvv()
        update_order.card_number.data = current_order.get_card_no()
        update_order.general_location.data = current_order.get_location()
        update_order.remarks.data = current_order.get_remark()
        return render_template('order_details_delivery.html', form=update_order)


@app.route('/edit_collect_order/<int:id>')
def edit_collect_order(id):
    db = shelve.open('storage.db', 'c')
    update_order = Order(request.form)
    if request.method == 'POST':
        order_dict = db['orders_self']

        current_order = order_dict.get(id)
        current_order.set_name(update_order.name.data)
        current_order.set_number(update_order.number.data)
        current_order.set_card_no(update_order.card_number.data)
        current_order.set_exp(update_order.exp_date.data)
        current_order.set_ccv(update_order.cvv.data)
        current_order.set_card_type(update_order.card_type.data)

        db['orders_self'] = order_dict
        db.close()
    else:
        order_dict = db['orders_self']

        current_order = order_dict.get(id)
        update_order.name.data = current_order.get_name()
        update_order.number.data = current_order.get_phone()
        update_order.card_number.data = current_order.get_card_no()
        update_order.exp_date.data = current_order.get_exp()
        update_order.cvv.data = current_order.get_cvv()
        update_order.card_type.data = current_order.get_card()
        return redirect(url_for('summary_self'))

    return render_template('order_details_collect.html', form=update_order)


@app.route('/create_item/<shop_or_stock>', methods=['GET', 'POST'])
def create_stock(shop_or_stock):
    count = 1
    create_item = Shop(request.form)
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            print(file.filename)
            users_dict = {}
            db = shelve.open('storage.db', 'c')
            try:
                users_dict = db['item']
                while count in users_dict:
                    count += 1
            except:
                print('Error in retrieving users from db')

            shop_item = item.Shop_item(create_item.stock_name.data,
                                       create_item.price.data, create_item.origin.data,
                                       create_item.weight.data, create_item.Dietary.data,
                                       create_item.ingredients.data, create_item.description.data,
                                       create_item.amt_of_stock.data, create_item.category.data, create_item.brand.data)
            shop_item.set_id(count)
            users_dict[shop_item.get_id()] = shop_item
            db['item'] = users_dict

            users_dict = db['item']
            shop_item = users_dict[shop_item.get_id()]
            db.close()

            filename = create_item.stock_name.data + '.png'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            session['item_created'] = shop_item.get_stock_name()

            if shop_or_stock == 'stock':
                return redirect(url_for('stock',
                                        filename=filename))
            else:
                return redirect(url_for('shop_admin',
                                        filename=filename))
        else:
            print('invalid file extension')
            flash('Invalid file extension')
    return render_template('create_item.html', form=create_item, shop_or_stock=shop_or_stock)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_stock(id):
    update_item = Shop(request.form)
    if request.method == 'POST':
        item_dict = {}
        db = shelve.open('storage.db', 'w')
        item_dict = db['item']

        item = item_dict.get(id)
        item.set_stock_name(update_item.stock_name.data)
        item.set_price(update_item.price.data)
        item.set_origin(update_item.origin.data)
        item.set_weight(update_item.weight.data)
        item.set_dietary(update_item.Dietary.data)
        item.set_amt_of_stock(update_item.amt_of_stock.data)
        item.set_cat(update_item.category.data)
        item.set_ingredients(update_item.ingredients.data)
        item.set_description(update_item.description.data)
        item.set_brand(update_item.brand.data)

        db['item'] = item_dict
        db.close()

        session['item_updated'] = item.get_stock_name()

        return redirect(url_for('stock'))
    else:
        item_dict = {}
        db = shelve.open('storage.db', 'r')
        item_dict = db['item']
        db.close()

        item = item_dict.get(id)
        update_item.stock_name.data = item.get_stock_name()
        update_item.price.data = item.get_price()
        update_item.origin.data = item.get_origin()
        update_item.weight.data = item.get_weight()
        update_item.Dietary.data = item.get_dietary()
        update_item.category.data = item.get_category()
        update_item.amt_of_stock.data = item.get_amt_of_stock()
        update_item.ingredients.data = item.get_ingredients()
        update_item.description.data = item.get_description()
        update_item.brand.data = item.get_brand()

        return render_template('update_item.html', form=update_item)


@app.route('/delete_stock/<int:id>', methods=['GET', 'POST'])
def delete_stock(id):
    if request.method == 'POST':
        item_dict = {}
        db = shelve.open('storage.db', 'w')
        item_dict = db['item']

        item = item_dict.get(id)
        filename = item.get_stock_name() + '.png'
        filepath = UPLOAD_FOLDER + '/' + filename
        os.remove(filepath)

        item = item_dict.pop(id)

        db['item'] = item_dict
        db.close()

        session['item_deleted'] = item.get_stock_name()

    return redirect(url_for('stock'))


@app.route('/restock/<int:id>', methods=['GET', 'POST'])
def restock(id):
    count = 0
    create_restock = Restock(request.form)
    supplier_dict = {}
    supplier_list = []
    stock_dict = {}
    db = shelve.open('storage.db', 'c')
    stock_dict = db['item']
    current_item = stock_dict.get(id)

    try:
        supplier_dict = db['supplier']
        supplier = True
    except:
        print('supplier not created')
        supplier = False

    if supplier:
        for key in supplier_dict:
            item = supplier_dict.get(key)
            supplier_name = item.get_stock()
            if supplier_name == current_item.get_stock_name():
                supplier_list.append(item)
    if request.method == 'POST':
        data = request.form['supplier']
        amount = request.form['amount']
        session['restock_order'] = data

        for key in stock_dict:
            stock_item = stock_dict.get(key)
            stock_id = stock_item.get_id()
            if id == stock_id:
                stock_item.increase_stock(amount)
        db['item'] = stock_dict
        db.close()
        return redirect(url_for('stock'))
    return render_template('restock.html', form=create_restock, id=id, supplier_list=supplier_list, supplier=supplier)


@app.route('/delete_shop/<int:id>', methods=['GET', 'POST'])
def delete_shop(id):
    if request.method == 'POST':
        item_dict = {}
        db = shelve.open('storage.db', 'w')
        item_dict = db['item']

        item_dict.pop(id)

        db['item'] = item_dict
        db.close()

    return redirect(url_for('shop'))


@app.route('/create_supplier/<int:id>', methods=['GET', 'POST'])
def supplier(id):
    count = 1
    create_supplier = Supplier(request.form)
    if request.method == 'POST':
        supplier_dict = {}
        item_dict = {}
        db = shelve.open('storage.db', 'c')
        item_dict = db['item']

        try:
            supplier_dict = db['supplier']
            while count in supplier_dict:
                count += 1
        except:
            print('error')

        supplier_item = item.Supplier(create_supplier.name.data, create_supplier.email.data,
                                      create_supplier.number.data,
                                      create_supplier.location.data)
        supplier_item.set_id(count)
        stock_item = item_dict.get(id)
        supplier_item.set_stock(stock_item.get_stock_name())
        supplier_dict[supplier_item.get_id()] = supplier_item
        db['supplier'] = supplier_dict
        db.close()
        return redirect(url_for('stock'))
    return render_template('create_supplier.html', form=create_supplier)


@app.route('/suppliers')
def suppliers_list():
    supplier_dict = {}
    db = shelve.open('storage.db', 'r')
    try:
        supplier_dict = db['supplier']
    except:
        flash('No supplier created')
        redirect(url_for('restock'))
    db.close()

    supplier_list = []
    for key in supplier_dict:
        supplier_details = supplier_dict.get(key)
        supplier_list.append(supplier_details)

    return render_template('suppliers.html', count=len(supplier_list), users_list=supplier_list)


@app.route('/deleteSupplier/<int:id>', methods=['POST'])
def delete_supplier(id):
    users_dict = {}
    db = shelve.open('storage.db', 'w')
    users_dict = db['supplier']

    users_dict.pop(id)

    db['supplier'] = users_dict
    db.close()
    return redirect(url_for('stock'))


@app.route('/updateSupplier/<int:id>', methods=['POST'])
def update_supplier(id):
    update_supplier = Supplier(request.form)
    if request.method == 'POST':
        supplier_dict = {}
        db = shelve.open('storage.db', 'c')

        try:
            supplier_dict = db['supplier']
        except:
            print('error')

        supplier_item = supplier_dict.get(id)

        supplier_item.set_name(update_supplier.name.data)
        supplier_item.set_number(update_supplier.number.data)
        supplier_item.set_email(update_supplier.email.data)
        supplier_item.set_location(update_supplier.location.data)

        db['supplier'] = supplier_dict
    else:
        supplier_dict = {}
        db = shelve.open('storage.db', 'c')

        try:
            supplier_dict = db['supplier']
        except:
            print('error')

        supplier_item = supplier_dict.get(id)

        update_supplier.name.data = supplier_item.get_name()
        update_supplier.number.data = supplier_item.get_number()
        update_supplier.email.data = supplier_item.get_email()
        update_supplier.location.data = supplier_item.get_location()

        return render_template('update_supplier.html', form=update_supplier)


# Elly's part
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_form = SignUp(request.form)
    if request.method == 'POST' and signup_form.validate():
        users_dict = {}
        db = shelve.open('storage.db', 'c')

        try:
            users_dict = db['Users']
        except:
            print("Error in retrieving Users from storage.db.")

        user = User.User(signup_form.first_name.data, signup_form.last_name.data, signup_form.email.data, )
        print("===user====", user)
        users_dict[user.get_email()] = user
        db['Users'] = users_dict

        # Test codes
        users_dict = db['Users']
        user = users_dict[user.get_email()]
        print(user.get_first_name(), user.get_last_name(), "was stored in storage.db successfully with user_id ==",
              user.get_user_id())

        db.close()

        session['user_created'] = user.get_first_name() + ' ' + user.get_last_name()

        return redirect(url_for('retrieve_users'))
    return render_template('signup.html', form=signup_form)


@app.route('/retrieveUsers')
def retrieve_users():
    users_dict = {}
    db = shelve.open('storage.db', 'r')
    users_dict = db['Users']
    db.close()

    users_list = []
    for key in users_dict:
        user = users_dict.get(key)
        users_list.append(user)

    return render_template('retrieveUsers.html', count=len(users_list), users_list=users_list)


@app.route('/deleteUser/<email>', methods=['POST'])
def delete_user(email):
    users_dict = {}
    db = shelve.open('storage.db', 'w')
    users_dict = db['Users']

    users_dict.pop(email)

    db['Users'] = users_dict
    db.close()

    return redirect(url_for('retrieve_users'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = Login(request.form)
    if request.method == 'POST' and login_form.validate():
        session['current'] = login_form.email.data
        if login_form.email.data == "ss_staff@gmail.com":
            session['admin'] = True
        else:
            session['admin'] = False
        return redirect(url_for('home'))
    return render_template('login.html', form=login_form)


@app.route('/logout')
def logout():
    try:
        session.pop('current')
        session.pop('admin')
    except:
        flash('User is not logged in')
    session['admin'] = False
    return redirect(url_for('home'))


@app.route('/profile')
def profile():
    users_dict = {}
    db = shelve.open('storage.db', 'r')
    users_dict = db['Users']
    db.close()

    users_list = []
    for key in users_dict:
        user = users_dict.get(key)
        users_list.append(user)

    return render_template('profile.html', count=len(users_list), users_list=users_list)


@app.route('/updateProfile/<email>/', methods=['GET', 'POST'])
def update_profile(email):
    update_profile_form = SignUp(request.form)
    if request.method == 'POST' and update_profile_form.validate():
        users_dict = {}
        db = shelve.open('storage.db', 'w')
        users_dict = db['Users']

        user = users_dict.get(email)
        user.set_first_name(update_profile_form.first_name.data)
        user.set_last_name(update_profile_form.last_name.data)
        user.set_email(update_profile_form.email.data)
        db['Users'] = users_dict
        db.close()

        return redirect(url_for('profile'))
    else:
        users_dict = {}
        db = shelve.open('storage.db', 'r')
        users_dict = db['Users']
        db.close()

        user = users_dict.get(email)
        update_profile_form.first_name.data = user.get_first_name()
        update_profile_form.last_name.data = user.get_last_name()
        update_profile_form.email.data = user.get_email()
        return render_template('updateProfile.html', form=update_profile_form)


@app.route('/createLocation', methods=['GET', 'POST'])
def create_location():
    location_form = CreateLocation(request.form)
    if request.method == 'POST' and location_form.validate():
        locations_dict = {}
        db = shelve.open('location.db', 'c')

        try:
            locations_dict = db['Locations']
        except:
            print("Error in retrieving locations from location.db.")

        location = Location.Location(location_form.neighbourhood.data, location_form.address.data,
                                     location_form.availability.data, )
        print("===location====", location)
        locations_dict[location.get_location_id()] = location
        db['Locations'] = locations_dict

        # Test codes
        locations_dict = db['Locations']
        location = locations_dict[location.get_location_id()]
        print(location.get_address(), "was stored in location.db successfully with location_id ==",
              location.get_location_id())

        db.close()

        session['location_created'] = location.get_address()

        return redirect(url_for('retrieve_locations'))
    return render_template('createLocation.html', form=location_form)


@app.route('/retrieveLocations')
def retrieve_locations():
    locationrs_dict = {}
    db = shelve.open('location.db', 'r')
    locations_dict = db['Locations']
    db.close()

    locations_list = []
    for key in locations_dict:
        location = locations_dict.get(key)
        locations_list.append(location)

    return render_template('retrieveLocations.html', count=len(locations_list), locations_list=locations_list)


@app.route('/storeLocator')
def store_locator():
    locationrs_dict = {}
    db = shelve.open('location.db', 'r')
    locations_dict = db['Locations']
    db.close()

    locations_list = []
    for key in locations_dict:
        location = locations_dict.get(key)
        locations_list.append(location)

    return render_template('storeLocator.html', count=len(locations_list), locations_list=locations_list)


@app.route('/deleteLocation/<int:id>', methods=['POST'])
def delete_location(id):
    locations_dict = {}
    db = shelve.open('location.db', 'w')
    locations_dict = db['Locations']

    locations_dict.pop(id)

    db['Locations'] = locations_dict
    db.close()

    return redirect(url_for('retrieve_locations'))


@app.route('/updateLocation/<int:id>/', methods=['GET', 'POST'])
def update_location(id):
    update_location_form = CreateLocation(request.form)
    if request.method == 'POST' and update_location_form.validate():
        locations_dict = {}
        db = shelve.open('location.db', 'w')
        locations_dict = db['Locations']

        location = locations_dict.get(id)
        location.set_neighbourhood(update_location_form.neighbourhood.data)
        location.set_address(update_location_form.address.data)
        location.set_availability(update_location_form.availability.data)
        db['Locations'] = locations_dict
        db.close()

        return redirect(url_for('retrieve_locations'))
    else:
        locations_dict = {}
        db = shelve.open('location.db', 'r')
        locations_dict = db['Locations']
        db.close()

        location = locations_dict.get(id)
        update_location_form.neighbourhood.data = location.get_neighbourhood()
        update_location_form.address.data = location.get_address()
        update_location_form.availability.data = location.get_availability()
        return render_template('updateLocation.html', form=update_location_form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404


# qing's part
@app.route('/orders', methods=['GET', 'POST'])
def orders():
    db = shelve.open('storage.db', 'r')
    delivery_man_dict = {}
    try:
        collect_dict = db['confirmed_collect']
        delivery_dict = db['confirmed_delivery']
    except:
        return redirect(url_for('home'))
    try:
        delivery_man_dict = db['Deliverymen']
    except:
        print('dsa')

    collect_list = []
    delivery_list = []
    delivery_man = []
    for key in collect_dict:
        order_collect = collect_dict.get(key)
        collect_list.append(order_collect)

    for key in delivery_dict:
        order_delivery = delivery_dict.get(key)
        delivery_list.append(order_delivery)

    for key in delivery_man_dict:
        man = delivery_man_dict.get(key)
        delivery_man.append(man)
    return render_template('orders.html', collect=collect_list, deliver=delivery_list, man=delivery_man)


@app.route('/Dest_West', methods=["POST", "GET"])
def Dest_West():
    users_dict = {}
    db = shelve.open('storage.db', 'r')
    try:
        users_dict = db['Deliverymen']
    except:
        return redirect('Create_Deliverymen')
    order_dict = db['confirmed_delivery']
    db.close()

    order_list = []
    users_list = []
    for key in users_dict:
        user = users_dict.get(key)
        if user.get_regions() == 'W':
            users_list.append(user)

    for key in order_dict:
        order_deliver = order_dict.get(key)
        if order_deliver.get_location() == 'West':
            order_list.append(order_deliver)

    return render_template('Dest_West.html', users_list=users_list, order_list=order_list)


@app.route('/Dest_North')
def Dest_North():
    users_dict = {}
    db = shelve.open('storage.db', 'r')
    try:
        users_dict = db['Deliverymen']
    except:
        return redirect('Create_Deliverymen')
    order_dict = db['confirmed_delivery']
    db.close()

    order_list = []
    users_list = []
    for key in users_dict:
        user = users_dict.get(key)
        if user.get_regions() == 'N':
            users_list.append(user)

    for key in order_dict:
        order_deliver = order_dict.get(key)
        if order_deliver.get_location() == 'North':
            order_list.append(order_deliver)
    return render_template('Dest_North.html', users_list=users_list, order_list=order_list)


@app.route('/Dest_South')
def Dest_South():
    db = shelve.open('storage.db', 'r')
    try:
        users_dict = db['Deliverymen']
    except:
        return redirect('Create_Deliverymen')
    order_dict = db['confirmed_delivery']
    db.close()

    order_list = []
    users_list = []
    for key in users_dict:
        user = users_dict.get(key)
        if user.get_regions() == 'S':
            users_list.append(user)

    for key in order_dict:
        order_deliver = order_dict.get(key)
        if order_deliver.get_location() == 'South':
            order_list.append(order_deliver)
    return render_template('Dest_South.html', users_list=users_list, order_list=order_list)


@app.route('/Dest_East', methods=["POST", "GET"])
def Dest_East():
    db = shelve.open('storage.db', 'r')
    try:
        users_dict = db['Deliverymen']
    except:
        return redirect('Create_Deliverymen')
    order_dict = db['confirmed_delivery']
    db.close()

    order_list = []
    users_list = []
    for key in users_dict:
        user = users_dict.get(key)
        if user.get_regions() == 'E':
            users_list.append(user)

    for key in order_dict:
        order_deliver = order_dict.get(key)
        if order_deliver.get_location() == 'East':
            order_list.append(order_deliver)

    return render_template('Dest_East.html', users_list=users_list, order_list=order_list)


@app.route('/All_Deliveries')
def All_Deliveries():
    order_dict = {}
    db = shelve.open('storage.db', 'r')
    try:
        order_dict = db['confirmed_delivery']
    except:
        print('not created')
        return redirect(url_for('home'))

    order_list = []
    for key in order_dict:
        order_deliver = order_dict.get(key)
        order_list.append(order_deliver)
    return render_template('All_Deliveries.html', order_list=order_list)


@app.route('/All_Self_collection')
def All_Self_collection():
    order_dict = {}
    db = shelve.open('storage.db', 'r')
    try:
        order_dict = db['confirmed_collect']
    except:
        print('not created')
        return redirect(url_for('home'))

    order_list = []
    for key in order_dict:
        order_collect = order_dict.get(key)
        order_list.append(order_collect)
    return render_template('All_Self_collection.html', order_list=order_list)


@app.route('/Create_Deliverymen', methods=['GET', 'POST'])
def Create_Deliverymen():
    create_Deliverymen_form = CreateDeliverymen(request.form)
    if request.method == 'POST' and create_Deliverymen_form.validate():
        users_dict = {}
        db = shelve.open('storage.db', 'c')
        try:
            users_dict = db["Deliverymen"]
        except:
            print("Error in retrieving Users from storage.db.")

        user = User.Deliverymen(create_Deliverymen_form.first_name.data, create_Deliverymen_form.last_name.data,
                                create_Deliverymen_form.gender.data, create_Deliverymen_form.email.data,
                                create_Deliverymen_form.contact_no.data, create_Deliverymen_form.regions.data,
                                create_Deliverymen_form.remarks.data)

        users_dict[user.get_Deliverymen_id()] = user
        db['Deliverymen'] = users_dict
        db.close()

        session['Deliverymen_created'] = user.get_first_name() + ' ' + user.get_last_name()
        return redirect(url_for('Display_Deliverymen'))

    return render_template('Create_Deliverymen.html', form=create_Deliverymen_form)


@app.route('/Display_Deliverymen')
def Display_Deliverymen():
    users_dict = {}
    db = shelve.open('storage.db', 'r')
    users_dict = db['Deliverymen']
    db.close()

    users_list = []
    for key in users_dict:
        user = users_dict.get(key)
        users_list.append(user)

    return render_template('Display_Deliverymen.html', count=len(users_list), users_list=users_list)


@app.route('/updateDeliverymen/<int:id>/', methods=['GET', 'POST'])
def update_Deliverymen(id):
    update_Deliverymen_form = CreateDeliverymen(request.form)
    if request.method == 'POST' and update_Deliverymen_form.validate():
        users_dict = {}
        db = shelve.open('storage.db', 'w')
        users_dict = db['Deliverymen']

        user = users_dict.get(id)
        user.set_first_name(update_Deliverymen_form.first_name.data)
        user.set_last_name(update_Deliverymen_form.last_name.data)
        user.set_gender(update_Deliverymen_form.gender.data)
        user.set_email(update_Deliverymen_form.email.data)
        user.set_contact_no(update_Deliverymen_form.contact_no.data)
        user.set_regions(update_Deliverymen_form.regions.data)
        user.set_remarks(update_Deliverymen_form.remarks.data)

        db['Deliverymen'] = users_dict
        db.close()

        session['Deliverymen_updated'] = user.get_first_name() + ' ' + user.get_last_name()

        return redirect(url_for('Display_Deliverymen'))
    else:
        users_dict = {}
        db = shelve.open('storage.db', 'r')
        users_dict = db['Deliverymen']
        db.close()

        user = users_dict.get(id)
        update_Deliverymen_form.first_name.data = user.get_first_name()
        update_Deliverymen_form.last_name.data = user.get_last_name()
        update_Deliverymen_form.gender.data = user.get_gender()
        update_Deliverymen_form.email.data = user.get_email()
        update_Deliverymen_form.contact_no.data = user.get_contact_no()
        update_Deliverymen_form.regions.data = user.get_regions()
        update_Deliverymen_form.remarks.data = user.get_remarks()

        return render_template('updateDeliverymen.html', form=update_Deliverymen_form)


@app.route('/deleteDeliverymen/<int:id>', methods=['POST'])
def delete_Deliverymen(id):
    users_dict = {}
    db = shelve.open('storage.db', 'w')
    users_dict = db['Deliverymen']

    user = users_dict.pop(id)

    db['Deliverymen'] = users_dict
    db.close()

    session['Deliverymen_deleted'] = user.get_first_name() + ' ' + user.get_last_name()

    return redirect(url_for('Display_Deliverymen'))


@app.route('/assign/<int:id>/<int:orderid>', methods=["POST", "GET"])
def assign(id, orderid):
    users_dict = {}
    order_dict = {}
    db = shelve.open('storage.db', 'r')
    users_dict = db['Deliverymen']
    order_dict = db['confirmed_delivery']

    assign_dict = {}
    try:
        assign_dict = db['assignDeliverymen']
    except:
        print('No database')
    deliverymen = users_dict.get(id)
    current_order = order_dict.get(orderid)
    assign_dict[deliverymen.get_Deliverymen_id()] = current_order
    db['assignDeliverymen'] = assign_dict
    db.close()
    return redirect(url_for('Dest_East'))


@app.route('/Outlet_North')
def Outlet_North():
    return render_template('Outlet_North.html')


@app.route('/Outlet_South')
def Outlet_South():
    return render_template('Outlet_South.html')


@app.route('/Outlet_East')
def Outlet_East():
    return render_template('Outlet_East.html')


@app.route('/Outlet_West')
def Outlet_West():
    return render_template('Outlet_West.html')


if __name__ == '__main__':
    app.run()
