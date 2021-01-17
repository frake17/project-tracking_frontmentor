from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators,  IntegerField, DateField


class Shop(Form):
    stock_name = StringField('Stock Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    amt_of_stock = StringField('amt_of_stock', [validators.Length(min=1, max=150), validators.DataRequired()])
    supplier_name = StringField('Supplier Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    price = StringField('price', [validators.Length(min=1, max=150), validators.DataRequired()])
    origin = StringField('origin', [validators.Length(min=1, max=150), validators.DataRequired()])
    weight = StringField('weight', [validators.Length(min=1, max=150), validators.DataRequired()])
    Dietary = SelectField('dietary', [validators.Optional()], choices=[
        ('', 'Select'), ('Halal', 'Halal'), ('Healthier', 'Healthier choice'), ('Organic', 'Organic'),
        ('Vegetarian', 'Vegetarian'),
        ('Gluten-Free', 'Gluten-Free'), ('Trans-Fat-Free', 'Trans-Fat-Free'), ('Hypoallergenic', 'Hypoallergenic'),
        ('Lactose-Free', 'Lactose-Free')
    ], default='')
    category = SelectField('category', [validators.required()], choices=[('Fruit and veg', 'Fruit and vegetables'), ('Frozen', 'Frozen'),
                                                                       ('Dairy', 'Dairy'), ('Meat and seafood', 'Meat and seafood'), ('Drinks', 'Drinks'),
                                                                       ('Packaged food and snacks', 'Packaged food and snacks')])
    ingredients = TextAreaField('ingredients', [validators.Optional()])
    description = TextAreaField('description', [validators.Optional()])


class Restock(Form):
    email = StringField('email', [validators.Length(min=1, max=150), validators.DataRequired()])
    order_number = StringField('order_number', [validators.Length(min=1, max=150), validators.DataRequired()])


class Order(Form):
    name = StringField('name', [validators.DataRequired()])
    number = IntegerField('Phone_number', [validators.number_range(min=00000000, max=99999999), validators.DataRequired()])
    postal = IntegerField('Postal_code', [validators.number_range(min=1, max=999999), validators.DataRequired()])
    address = StringField('Address', [validators.Length(min=1, max=150), validators.DataRequired()])
    general_location = SelectField('General location', [validators.data_required()], choices=[('North', 'North'), ('South', 'South'),
                                                                                              ('East', 'East'), ('West', 'West'), ('Central', 'Central')])
    level = IntegerField('Level', [validators.number_range(min=1, max=50), validators.DataRequired()])
    door_number = StringField('Door_number', [validators.Length(min=1, max=150), validators.DataRequired()])
    card_number = StringField('Card_number', [validators.length(min=12, max=19), validators.DataRequired()])
    exp_date = DateField('Exp_date(mm/yyyy)', [validators.DataRequired()], format='%m/%Y')
    cvv = IntegerField('Card_cvv', [validators.number_range(min=000, max=999), validators.DataRequired()])
    card_type = SelectField('Card_type', choices=[('CC','Credit Card'), ('DC', 'Debit Card')])
    remarks = TextAreaField('Remarks')


class self_collect(Form):
    name = StringField('name', [validators.DataRequired()])
    card_number = StringField('Card_number', [validators.length(min=12, max=19), validators.DataRequired()])
    exp_date = DateField('Exp_date(mm/yyyy)', [validators.DataRequired()], format='%m/%Y')
    cvv = IntegerField('Card_cvv', [validators.number_range(min=000, max=999), validators.DataRequired()])
    card_type = SelectField('Card_type', choices=[('CC','Credit Card'), ('DC', 'Debit Card')])
    number = IntegerField('Phone_number', [validators.number_range(min=00000000, max=99999999), validators.DataRequired()])

