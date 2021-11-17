from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os,re, datetime.datetime

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

    def validate_doc_len(self):
        if not re.match(r'\d{11}', cpf):
            return False
        return True

    def validate_doc_digits(self):
        numbers = [int(digit) for digit in self.customer_doc if digit.isdigit()]
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
    purchase = db.relationship("Purchase",
                    secondary=association_table, backref=db.backref('purchase', lazy = 'dynamic'))

    def product_total(self):
        return self.value * self.qty

    def validate_product(self):
        validation_list = ['A','B','C']
        if self.type not in validation_list or len(self.type) !=1:
            return False
        return True
