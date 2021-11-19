from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
import os,re,json
from datetime import datetime, timedelta
import requests
from werkzeug.security import check_password_hash

mock_url = 'https://5efb30ac80d8170016f7613d.mockapi.io/api/mock/Cashback'
mock_header = {'Content-Type': 'application/json'}
mock_data = '{"document": "33535353535",	"cashback": "10"}'


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.dirname(os.path.abspath(__file__))}/walet.db?check_same_thread=False"

db = SQLAlchemy(app)

password = 'MAISTodos' #inserido apenas para criação da API, não seria usado em produção.

association_table = db.Table('association', db.Model.metadata,
    db.Column('purchase_id', db.ForeignKey('purchase.id')),
    db.Column('product_id', db.ForeignKey('product.id'))
)


class Purchase(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    sold_at = db.Column(db.DateTime, nullable = False)
    name = db.Column(db.String(50), unique=True, nullable = False)
    document = db.Column(db.String(11), unique=True, nullable=False)
    total = db.Column(db.Float, nullable=False)


    def execute_all_methods(self):
        self.convert_upper()
        if not self.check_date_hour:
            return False
        if not self.validate_doc():
            return False
        self.get_purchase_cashback()
        return True

    def check_date_hour(self):
        self.sold_at = datetime.strptime(self.sold_at,('%Y-%m-%d %H:%M:%S'))
        limit_max,limit_min = datetime.now() + timedelta(minutes=1), datetime.now() - timedelta(minutes=1)
        if limit_min < self.sold_at < limit_max:
            return True
        return False

    def convert_upper(self):
        self.name = self.name.upper()

    def validate_doc(self):
        if not re.match(r'\d{11}', self.document):
            return False
        numbers = [int(digit) for digit in self.document if digit.isdigit()]
        sum_of_products = sum(a * b for a, b in zip(numbers[0:9], range(10, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if numbers[9] != expected_digit:
            return False
        sum_of_products = sum(a*b for a, b in zip(numbers[0:10], range(11, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if numbers[10] != expected_digit:
            return False
        return True

    def get_purchase_cashback(self):
        self.purchase_cashback = sum(item.cashback for item in self.purchase)

    def verify_values(self):
        if self.total != sum(item.total for item in self.products):
            return False
        else:
            self.get_purchase_cashback()
            return True

    def to_json(self):
        return {'document': self.document, 'cashback': self.purchase_cashback}

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(1), nullable=False)
    value = db.Column(db.Float, nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    cashback = db.Column(db.Float, nullable=False)
    purchase = db.relationship("Purchase",
                    secondary=association_table, backref=db.backref('purchase', lazy = 'dynamic'))

    def execute_all_methods(self):
        if not self.validate_product():
            print('Erro ao validar produto')
            return False
        self.calculate_cash_back()
        return True

    def validate_product(self):
        self.type = self.type.upper()
        if len(self.type) != 1:
            return False
        try:
            self.value = float(self.value)
            self.qty = int(self.qty)
        except ValueError:
            return False
        return True

    def calculate_cash_back(self):
        self.total = round(float(self.value * self.qty),2)
        if self.type=='A':
            self.cashback = self.total*0.1
        elif self.type=='B':
            self.cashback = self.total*0.05
        elif self.type=='C':
            self.cashback = self.total * 0.07
        else:
            self.cashback = 0
        return self.cashback

### functions to validate and show api information
def add_products(purchase_obj, items):
    for item in items:
        product = Product(type=item.get('type'),value=item.get('value'),qty=item.get('qty'))
        if not product.execute_all_methods():
            return False
        else:
            db.session.add(product)
            product.purchase.append(purchase_obj)
    return True

def create_response(status, nome_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_conteudo] = conteudo
    if mensagem:
        body['mensagem'] = mensagem
    return Response(json.dumps(body), status=status, mimetype='application/json')

def more_everyone_api(data):
    r = requests.post(mock_url, data=mock_data, headers=mock_header)
    if r.status_code != 201:
        return False
    return True

def check_received_params(params):
    required_params = ['sold_at','customer','total','products']
    required_customer_params = ['document','name']
    required_products_params = ['type', 'value', 'qty']
    for key in required_params:
        if key not in params.keys():
            return 'Missing purchase parameter'
    for key in required_customer_params:
        if key not in params['customer'].keys():
            return 'Missing customer parameter'
    for product in params['products']:
        for key in required_products_params:
            if key not in product.keys():
                return 'Missing product parameter'
    return True

@app.route('/api/cashback', methods=['POST'])
def insere_cashback():
    body = request.get_json()
    checked_ok = check_received_params(body)
    if checked_ok != True:
        return create_response(400, 'error', {}, checked_ok)

    try:
        purchase = Purchase(sold_at=body['sold_at'], name=body['customer']['name'],document=body['customer']['document'],total=body['total'])
        products = body.get('products')
        if not add_products(purchase_obj=purchase,items=products):
            return create_response(400, 'error', {}, 'Invalid product information')
        purchase.execute_all_methods()
        db.session.add(purchase)
        db.session.commit()
        more_everyone_api(purchase.to_json())
        return create_response(201, 'usuario', {}, 'Cashback successfully created')
    except Exception as e:
        print(e)
        return create_response(400, 'usuario', {}, 'Error creating cashback')

#check_password_hash(auth.password, password)



if __name__ == "__main__":
    app.run()