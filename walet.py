from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os,re
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.dirname(os.path.abspath(__file__))}/walet.db?check_same_thread=False"

db = SQLAlchemy(app)


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

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(1), nullable=False)
    value = db.Column(db.Float, nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    cashback = db.Column(db.Float, nullable=False)
    purchase = db.relationship("Purchase",
                    secondary=association_table, backref=db.backref('purchase', lazy = 'dynamic'))

    def validate_product(self):
        validation_list = ['A','B','C']
        if len(self.type) !=1 or type(self.value)!=float or type(self.qty) != int:
            return False
        return True

    def generate_cash_back(self):
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

def verify_values(purchase,products):
    if purchase.total != sum(f.product_total() for f in products):
        return False
    return True

