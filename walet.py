from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.dirname(os.path.abspath(__file__))}/walet.db?check_same_thread=False"

db = SQLAlchemy(app)



class Purchase(db.Model):
    sold_at = db.Column(db.DateTime, nullable = False)
    customer_name = db.Column(db.String(50), unique=True, nullable = False)
    customer_doc = db.Column(db.String(11), unique=True, nullable=False, primary_key=True)
    purchase_total = db.Column(db.Float, nullable=False)

class Products(db.Model):
    customer_doc = db.Column(db.String(11), unique=True, nullable=False, primary_key=True)
    type = db.Column(db.String(1), nullable=False)
    value_un = db.Column(db.Float, nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    def product_total(self):
        return self.value_un * self.qty

    def to_json(self):
        return {'id': self.id, 'nome': self.nome, 'cpf': self.cpf, 'email': self.email, 'product_total':self.product_total()}
