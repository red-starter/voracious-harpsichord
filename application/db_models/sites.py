from server import db

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(120)) #Name of publicaction ie. NY times
    article_name = db.Column(db.String(120)) #Name of specific article
    author_name = db.Column(db.String(60))
    url = db.Column(db.String(500), unique=True)
    image = db.Column(db.String(500))
    description = db.Column(db.String(500))

    def __init__(self, site_name, article_name, author_name, url, image, description):
        self.site_name = site_name
        self.article_name = article_name
        self.author_name = author_name
        self.url = url
        self.image = image
        self.description = description

    def __repr__(self):
        return '<article %r>' % self.article_name

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(120))
    url = db.Column(db.String(500), unique=True)
    image = db.Column(db.String(500))
    description = db.Column(db.String(500))

    def __init__(self, site_name, url, image, description):
        self.site_name = site_name
        self.url = url
        self.image = image
        self.description = description

    def __repr__(self):
        return '<blog %r>' % self.site_name

class User_site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    site_id = db.Column(db.Integer)
    site_type = db.Column(db.String(60))
    comment = db.Column(db.String(500))

    def __init__(self, user_id, site_id, site_type, comment):
        self.user_id = user_id
        self.site_id = site_id
        self.site_type = site_type
        self.comment = comment

    def __repr__(self):
        return '<site_id %r>' % self.site_id

db.create_all()
