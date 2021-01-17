from flask import Flask, render_template, request, redirect, url_for, session
from Forms import Shop, Order, Restock, self_collect
import shelve
import item
import os


UPLOAD_FOLDER = 'static/img/uploaded'
ALLOWED_EXTENSIONS = {'png'}

app = Flask(__name__)
app.secret_key = 'any_random_string'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["SESSION_PERMANENT"] = False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    #db = shelve.open('Cart.db', 'c')
    #db.clear()
    #db.close()
    return render_template('home.html')


@app.route('/stock')
def stock():
    users_dict = {}
    try:
        db = shelve.open('Item.db', 'r')
        users_dict = db['item']
        db.close()
    except:
        print("Error in retrieving Users from storage.db.")

    item_list = []
    for key in users_dict:
        user = users_dict.get(key)
        item_list.append(user)

    return render_template('stock.html', item_list=item_list)


@app.route('/shop')
def shop():
    users_dict = {}
    try:
        db = shelve.open('Item.db', 'r')
        users_dict = db['item']
        db.close()
    except:
        print("Error in retrieving Users from storage.db.")

    item_list = []
    for key in users_dict:
        user = users_dict.get(key)
        item_list.append(user)

    return render_template('shop_admin.html', item_list=item_list)


@app.route('/shop_cus')
def shop_cus():
    users_dict = {}
    try:
        db = shelve.open('Item.db', 'r')
        users_dict = db['item']
        db.close()
    except:
        print("Error in retrieving Users from storage.db.")

    item_list = []
    for key in users_dict:
        user = users_dict.get(key)
        item_list.append(user)
    return render_template('shop_cus.html', item_list=item_list)


@app.route('/cart/<int:product_id>', methods=['POST', 'GET'])
def add(product_id):
    cart_dict = {}
    db = shelve.open('Item.db', 'c')
    try:
        cart_dict = db['Cart']
    except:
        print('das')

    shop_dict = db['item']
    print(cart_dict)

    item_list = []
    for key in shop_dict:
        user = shop_dict.get(key)
        item_list.append(user)

    for item in item_list:
        id = item.get_id()
        if id == product_id:
            item.add_amount()
            if item.get_id() in cart_dict:
                cart_dict.pop(item.get_id())
            cart_dict[item.get_id()] = item
            db['Cart'] = cart_dict
    db.close()

    return redirect(url_for('cart'))


@app.route('/add/<int:product_id>')
def add_change(product_id):
    cart_dict = {}
    db = shelve.open('Item.db', 'c')
    try:
        cart_dict = db['Cart']
    except:
        print('das')

    item = cart_dict.get(product_id)
    item.add_amount()
    db['Cart'] = cart_dict
    db.close()

    return redirect(url_for('cart'))


@app.route('/minus/<int:product_id>')
def minus_change(product_id):
    cart_dict = {}
    db = shelve.open('Item.db', 'c')
    try:
        cart_dict = db['Cart']
    except:
        print('das')

    item = cart_dict.get(product_id)
    item.minus()
    db['Cart'] = cart_dict
    db.close()

    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    cart_list = {}
    db = shelve.open('Item.db', 'c')
    try:
        cart_list = db['Cart']
    except:
        redirect(url_for('home'))

    item_list = []
    total = 0
    for key in cart_list:
        user = cart_list.get(key)
        price = user.get_price()
        total += int(price)
        item_list.append(user)
    session['Total_price'] = total

    return render_template('cart.html', item_list=item_list, price=total)


@app.route('/clear_cart')
def clear():
    db = shelve.open('Item.db', 'c')
    clear_list = {}
    db['Cart'] = clear_list
    item_dict = {}
    item_dict = db['item']
    for key in item_dict:
        item = item_dict.get(key)
        item.set_amount_empty()
    db['item'] = item_dict
    return redirect(url_for('cart'))


@app.route('/delivery', methods=['POST', 'GET'])
def delivery():
    total = session.get('Total_price', None)
    if total > 65:
        total = total
    else:
        total = total + 3
    if request.method == 'POST':
        date = request.form['date']
        session['date'] = date
        return redirect(url_for('order'))
    return render_template('delivery.html', total=total)


@app.route('/self-collect', methods=['POST', 'GET'])
def collect():
    total = session.get('Total_price', None)
    stores = {'Alijunied': 'Blk 118 Aljunied Ave 2, #01-100, Singapore 380118', 'Achorvale': 'Blk 338 Anchorvale Crescent, #01-11 Singapore 540338', 'Ang Mo Kio': 'Blk 122 Ang Mo Kio Ave 3, #01-1753/1755 Singapore 560122', 'Bedok': 'Blk 115 Bedok North Road, #01-319 Singapore 460115',
              'Buki Batok': 'Blk 292 Bukit Batok East Avenue 6, #01-02 Singapore 650292', 'Canberra': 'Blk 105 Canberra St, #02-05 Singapore 750105', 'Clementi West': 'Blk 720 Clementi West St 2, #01-144 Singapore 120720', 'Dawson Rd' : '85 Dawson Road, #01-01 Singapore 141085', 'Toa payoh': 'Blk 4 Toa Payoh Lorong 7, #01-107 Singapore 310004',
              'Geylang 301': 'Blk 301 Geylang Lorong 15, #01-02, BCH Building Singapore 389344', 'Elias mall': 'Blk 623 Elias Road, #B1-01 Elias Mall (Stalls #14-16) Singapore 510623', 'Fajar': 'Blk 446 Fajar Rd, #01-01 Singapore 670446', 'Yishun Ave 675': 'Blk 675 Yishun Avenue 4, #01-10 Singapore 760675'}
    session['stores'] = stores

    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        location = request.form['location']
        session['date'] = date
        session['time'] = time
        session['location'] = location
        return redirect(url_for('order_self'))

    return render_template('self_collect.html', total=total, stores=stores)


@app.route('/order', methods=['GET', 'POST'])
def order():
    count = 1
    date = session.get('date', None)
    create_order = Order(request.form)
    if request.method == 'POST' and create_order.validate():
        users_dict = {}
        db = shelve.open('Item.db', 'c')
        try:
            users_dict = db['orders_delivery']
            while count in users_dict:
                count += 1
        except:
            print('Error in retrieving users from db')

        order_item = item.Order_delivery(create_order.name.data, create_order.number.data, create_order.postal.data, create_order.address.data, create_order.level.data, create_order.door_number.data, create_order.card_number.data, create_order.exp_date.data, create_order.cvv.data, create_order.card_type.data,
                                         create_order.general_location.data, create_order.remarks.data)
        order_item.set_card(create_order.card_type.data)
        order_item.set_id(count) #To set new Id
        order_item.set_date(date)
        session['current_id_delivery'] = count
        users_dict[order_item.get_id()] = order_item
        db['orders_delivery'] = users_dict
        db.close()

        return redirect(url_for('summary'))
    return render_template('order_form.html', form=create_order)


@app.route('/order_self', methods=['POST', 'GET'])
def order_self():
    count = 1
    create_order_self = self_collect(request.form)
    date = session.get('date', None)
    location = session.get('location', None)
    time = session.get('time', None)
    if request.method == 'POST':
        users_dict = {}
        db = shelve.open('Item.db', 'c')
        try:
            users_dict = db['orders_self']
            while count in users_dict:
                count += 1
        except:
            print('dsa')
        order_item = item.Order_self(create_order_self.name.data, create_order_self.number.data, create_order_self.card_number.data,
                                     create_order_self.exp_date.data, create_order_self.cvv.data, create_order_self.card_type.data)
        order_item.set_date(date)
        order_item.set_location(location)
        order_item.set_time(time)
        order_item.set_id(count)
        session['current_id_self'] = count
        users_dict[order_item.get_id()] = order_item
        db['orders_self'] = users_dict
        db.close()

        return redirect(url_for('summary_self'))

    return render_template('order_self.html', form=create_order_self)


@app.route('/summary')
def summary():
    order_list = {}
    clear_dict = {}
    item_dict = {}
    item_list = []
    db = shelve.open('Item.db', 'c')
    order_list = db['orders_delivery']
    db['Cart'] = clear_dict
    item_dict = db['item']

    for key in order_list:
        user = order_list.get(key)
        item_list.append(user)

    for key in item_dict:
        item = item_dict.get(key)
        item.set_amount_empty()
    db['item'] = item_dict

    current_id = session.get('current_id_delivery')
    current = order_list.get(current_id)

    return render_template('summary.html', item_list=item_list, current=current)


@app.route('/summary_self')
def summary_self():
    order_list = {}
    clear_dict = {}
    item_dict = {}
    item_list = []
    db = shelve.open('Item.db', 'c')
    order_list = db['orders_self']
    db['Cart'] = clear_dict
    item_dict = db['item']

    for key in order_list:
        user = order_list.get(key)
        item_list.append(user)

    for key in item_dict:
        item = item_dict.get(key)
        item.set_amount_empty()
    db['item'] = item_dict

    current_id = session.get('current_id_self', None)
    current = order_list.get(current_id)

    return render_template('summary_self.html', item_list=item_list, current=current)


@app.route('/summary_restock')
def summary_restock():
    order_list = {}
    clear_dict = {}
    item_dict = {}
    item_list = []
    db = shelve.open('Item.db', 'c')
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

    return render_template('summary_restock.html', item_list=item_list, current=current)


@app.route('/create_shop', methods=['GET', 'POST'])
def create_shop():
    count = 1
    create_item = Shop(request.form)
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            users_dict = {}
            db = shelve.open('Item.db', 'c')

            try:
                users_dict = db['item']
                while count in users_dict:
                    count += 1
            except:
                print('Error in retrieving users from db')
            shop_item = item.Shop_item(create_item.stock_name.data, create_item.supplier_name.data,
                                       create_item.price.data, create_item.origin.data,
                                       create_item.weight.data, create_item.Dietary.data,
                                       create_item.ingredients.data, create_item.description.data, create_item.amt_of_stock.data, create_item.category.data)
            shop_item.set_id(count)
            users_dict[shop_item.get_id()] = shop_item
            db['item'] = users_dict

            users_dict = db['item']
            shop_item = users_dict[shop_item.get_id()]
            print(shop_item.get_stock_name())
            db.close()

            filename = create_item.stock_name.data + '.png'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            session['item_created'] = shop_item.get_stock_name()

            return redirect(url_for('shop'))
    return render_template('create_shop.html', form=create_item)


@app.route('/create_stock', methods=['GET', 'POST'])
def create_stock():
    count = 1
    create_item = Shop(request.form)
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            print(file.filename)
            users_dict = {}
            db = shelve.open('Item.db', 'c')
            try:
                users_dict = db['item']
                while count in users_dict:
                    count += 1
            except:
                print('Error in retrieving users from db')

            shop_item = item.Shop_item(create_item.stock_name.data, create_item.supplier_name.data,
                                       create_item.price.data, create_item.origin.data,
                                       create_item.weight.data, create_item.Dietary.data,
                                       create_item.ingredients.data, create_item.description.data, create_item.amt_of_stock.data, create_item.category.data)
            shop_item.set_id(count)
            users_dict[shop_item.get_id()] = shop_item
            db['item'] = users_dict

            users_dict = db['item']
            shop_item = users_dict[shop_item.get_id()]
            db.close()

            filename = create_item.stock_name.data + '.png'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            session['item_created'] = shop_item.get_stock_name()

            return redirect(url_for('stock',
                                    filename=filename))
    return render_template('create_shop.html', form=create_item)


@app.route('/update_stock/<int:id>', methods=['GET', 'POST'])
def update_stock(id):
    update_item = Shop(request.form)
    if request.method == 'POST':
        item_dict = {}
        db = shelve.open('Item.db', 'w')
        item_dict = db['item']

        item = item_dict.get(id)
        item.set_stock_name(update_item.stock_name.data)
        item.set_supplier_name(update_item.supplier_name.data)
        item.set_price(update_item.price.data)
        item.set_origin(update_item.origin.data)
        item.set_weight(update_item.weight.data)
        item.set_dietary(update_item.Dietary.data)
        item.set_amt_of_stock(update_item.amt_of_stock.data)
        item.set_cat(update_item.category.data)
        item.set_ingredients(update_item.ingredients.data)
        item.set_description(update_item.description.data)

        db['item'] = item_dict
        db.close()
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = update_item.stock_name.data + '.png'
            filepath = UPLOAD_FOLDER + '/' + filename
            os.remove(filepath)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        session['item_updated'] = item.get_stock_name()

        return redirect(url_for('stock'))
    else:
        item_dict = {}
        db = shelve.open('Item.db', 'r')
        item_dict = db['item']
        db.close()

        item = item_dict.get(id)
        update_item.stock_name.data = item.get_stock_name()
        update_item.supplier_name.data = item.get_supplier_name()
        update_item.price.data = item.get_price()
        update_item.origin.data = item.get_origin()
        update_item.weight.data = item.get_weight()
        update_item.Dietary.data = item.get_dietary()
        update_item.category.data = item.get_category()
        update_item.amt_of_stock.data = item.get_amt_of_stock()
        update_item.ingredients.data = item.get_ingredients()
        update_item.description.data = item.get_description()

        return render_template('update_item.html', form=update_item)


@app.route('/update_shop/<int:id>', methods=['GET', 'POST'])
def update_shop(id):
    update_item = Shop(request.form)
    if request.method == 'POST':
        item_dict = {}
        db = shelve.open('Item.db', 'w')
        item_dict = db['item']

        item = item_dict.get(id)
        item.set_stock_name(update_item.stock_name.data)
        item.set_supplier_name(update_item.supplier_name.data)
        item.set_price(update_item.price.data)
        item.set_origin(update_item.origin.data)
        item.set_weight(update_item.weight.data)
        item.set_dietary(update_item.Dietary.data)
        item.set_cat(update_item.category.data)
        item.set_amt_of_stock(update_item.amt_of_stock.data)
        item.set_ingredients(update_item.ingredients.data)
        item.set_description(update_item.description.data)

        db['item'] = item_dict
        db.close()
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = update_item.stock_name.data + '.png'
            filepath = UPLOAD_FOLDER + '/' + filename
            print(filepath)
            os.remove(filepath)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        session['item_updated'] = item.get_stock_name()

        return redirect(url_for('shop'))
    else:
        item_dict = {}
        db = shelve.open('Item.db', 'r')
        item_dict = db['item']
        db.close()

        item = item_dict.get(id)
        update_item.stock_name.data = item.get_stock_name()
        update_item.supplier_name.data = item.get_supplier_name()
        update_item.price.data = item.get_price()
        update_item.origin.data = item.get_origin()
        update_item.weight.data = item.get_weight()
        update_item.Dietary.data = item.get_dietary()
        update_item.category.data = item.get_category()
        update_item.amt_of_stock.data = item.get_amt_of_stock()
        update_item.ingredients.data = item.get_ingredients()
        update_item.description.data = item.get_description()

        return render_template('update_item.html', form=update_item)


@app.route('/delete_stock/<int:id>', methods=['GET', 'POST'])
def delete_stock(id):
    if request.method == 'POST':
        item_dict = {}
        db = shelve.open('Item.db', 'w')
        item_dict = db['item']

        item = item_dict.pop(id)

        db['item'] = item_dict
        db.close()

        session['item_deleted'] = item.get_stock_name()

    return redirect(url_for('stock'))


@app.route('/restock', methods=['GET', 'POST'])
def restock():
    count = 0
    create_restock = Restock(request.form)
    if request.method == 'POST':
        users_dict = {}
        db = shelve.open('Item.db', 'c')

        try:
            users_dict = db['restock']
            for key in users_dict:
                count += 1
            count += 1
        except:
            print('Error in retrieving users from db')

        shop_item = item.Restock(create_restock.email.data, create_restock.order_number.data)
        shop_item.set_id(count)
        users_dict[shop_item.get_id()] = shop_item
        session['current_id_restock'] = count
        db['restock'] = users_dict
        db.close()

        return redirect(url_for('summary_restock'))
    return render_template('restock.html', form=create_restock)


@app.route('/delete_shop/<int:id>', methods=['GET', 'POST'])
def delete_shop(id):
    if request.method == 'POST':
        item_dict = {}
        db = shelve.open('Item.db', 'w')
        item_dict = db['item']

        item_dict.pop(id)

        db['item'] = item_dict
        db.close()

    return redirect(url_for('shop'))


if __name__ == '__main__':
    app.run()