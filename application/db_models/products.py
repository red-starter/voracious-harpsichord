from server import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(120), unique=True)
    brand_name = db.Column(db.String(80))
    user_products = db.relationship('User_product',backref='product',lazy='dynamic')

    def __init__(self, product_name, brand_name):
        self.product_name = product_name
        self.brand_name = brand_name

    def __repr__(self):
        return '<product %r>' % self.product_name


class User_product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # set up foreign keys to User and Product
    product_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

    def __init__(self, product_id, user_id):
        return None

    def __repr__(self):
        return '<User %r>' % self.username

db.create_all()