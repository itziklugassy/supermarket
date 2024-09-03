import os
from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from app.models.product import Product
from app.schemas.product import product_schema, products_schema
from app import db

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'avif'}


class ProductList(Resource):
    def get(self):
        products = Product.query.all()
        return products_schema.dump(products)

    @jwt_required()
    def post(self):
        print("Request Headers:", dict(request.headers))
        print("Request Form Data:", request.form)
        print("Request Files:", request.files)

        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')
        
        if not name or not price or not stock:
            missing_fields = []
            if not name:
                missing_fields.append('name')
            if not price:
                missing_fields.append('price')
            if not stock:
                missing_fields.append('stock')
            return {'message': f'Missing required fields: {", ".join(missing_fields)}'}, 400

        try:
            new_product = Product(
                name=name,
                description=description,
                price=float(price),
                stock=int(stock)
            )

            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    new_product.image_filename = filename
                    print(f"Image saved at: {file_path}")
                else:
                    print("Invalid file or filename")

            db.session.add(new_product)
            db.session.commit()

            return product_schema.dump(new_product), 201
        except Exception as e:
            print(f"Error creating product: {str(e)}")
            db.session.rollback()
            return {'message': f'An error occurred while creating the product: {str(e)}'}, 500

class ProductResource(Resource):
    def get(self, product_id):
        product = Product.query.get_or_404(product_id)
        return product_schema.dump(product)

    @jwt_required()
    def put(self, product_id):
        product = Product.query.get_or_404(product_id)

        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')

        if name:
            product.name = name
        if description:
            product.description = description
        if price:
            product.price = float(price)
        if stock:
            product.stock = int(stock)

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                product.image_filename = filename
                print(f"Image saved at: {file_path}")
            else:
                print("Invalid file or filename")

        try:
            db.session.commit()
            return product_schema.dump(product)
        except Exception as e:
            print(f"Error updating product: {str(e)}")
            db.session.rollback()
            return {'message': f'An error occurred while updating the product: {str(e)}'}, 500

    @jwt_required()
    def delete(self, product_id):
        product = Product.query.get_or_404(product_id)
        try:
            db.session.delete(product)
            db.session.commit()
            return '', 204
        except Exception as e:
            print(f"Error deleting product: {str(e)}")
            db.session.rollback()
            return {'message': f'An error occurred while deleting the product: {str(e)}'}, 500