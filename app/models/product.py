# app/models/product.py

from app import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_filename = db.Column(db.String(255))

    def __init__(self, name, description, price, stock, image_filename=None):
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.image_filename = image_filename

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'image_filename': self.image_filename
        }