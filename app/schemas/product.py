# app/schemas/product.py

from app import ma
from app.models.product import Product

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        include_fk = True

# Add these two lines at the end of the file
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)