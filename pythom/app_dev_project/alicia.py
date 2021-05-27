from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
from Forms import CreateUserForm, SearchUserForm
import shelve, User

alicia = Flask(__name__)
alicia.secret_key = 'any_random_string'
alicia = Blueprint('alicia', __name__, template_folder='templates')


@alicia.route('/temp_record', methods=['GET', 'POST'])
def create_user():
    create_user_form = CreateUserForm(request.form)
    if request.method == 'POST' and create_user_form.validate():
        users_dict = {}
        db = shelve.open('storage.db', 'c')

        try:
            users_dict = db['Users']
        except:
            print("Error in retrieving Users from storage.db.")

        user = User.Temp(create_user_form.outlet.data, create_user_form.date.data,
                         create_user_form.cust_ic.data, create_user_form.cust_no.data,
                         create_user_form.temp.data,
                         create_user_form.time_enter.data, create_user_form.time_leave.data)
        users_dict[user.get_user_id()] = user
        db['Users'] = users_dict
        db.close()

        session['user_created'] = user.get_cust_ic()

        return redirect(url_for('create_user'))
    return render_template('temp_record.html', form=create_user_form)


@alicia.route('/temp_search_user', methods=['GET', 'POST'])
def search_user():
    search_user_form = SearchUserForm(request.form)
    search_list = []

    if request.method == "POST":
        users_dict = {}
        db = shelve.open('storage.db', 'r')
        users_dict = db['Users']
        db.close()

        for key in users_dict:
            search = users_dict.get(key)
            if search_user_form.search_outlet.data == search.get_outlet():
                if search_user_form.search_date.data == search.get_date():
                    search_list.append(search)

    return render_template('temp_search_user.html', form=search_user_form, search_list=search_list)


@alicia.route('/temp_updateUser/<int:id>/', methods=['GET', 'POST'])
def update_user(id):
    update_user_form = CreateUserForm(request.form)
    if request.method == 'POST' and update_user_form.validate():
        users_dict = {}
        db = shelve.open('storage.db', 'w')
        users_dict = db['Users']

        user = users_dict.get(id)
        user.set_outlet(update_user_form.outlet.data)
        user.set_date(update_user_form.date.data)
        user.set_cust_ic(update_user_form.cust_ic.data)
        user.set_cust_no(update_user_form.cust_no.data)
        user.set_temp(update_user_form.temp.data)
        user.set_time_enter(update_user_form.time_enter.data)
        user.set_time_leave(update_user_form.time_leave.data)

        db['Users'] = users_dict
        db.close()

        return redirect(url_for('search_user'))

    else:
        users_dict = {}
        db = shelve.open('storage.db', 'r')
        users_dict = db['Users']
        db.close()

        user = users_dict.get(id)
        update_user_form.outlet.data = user.get_outlet()
        update_user_form.date.data = user.get_date()
        update_user_form.cust_ic.data = user.get_cust_ic()
        update_user_form.cust_no.data = user.get_cust_no()
        update_user_form.temp.data = user.get_temp()
        update_user_form.time_enter.data = user.get_time_enter()
        update_user_form.time_leave.data = user.get_time_leave()

        return render_template('temp_updateUser.html', form=update_user_form)
