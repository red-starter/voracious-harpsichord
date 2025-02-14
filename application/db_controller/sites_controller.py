import re
import requests
#create DB session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI)
session = sessionmaker(bind=engine)()
session._model_changes = {}

#import tables
from db_models.sites import Article, Blog, User_site

#URL UTILITIES
def remove_protocol(full_url):
    return re.sub(r'https?://', '', full_url)

def get_protocol(full_url):
    return re.sub(r'//.*', '', full_url) + '//'

def add_protocol(unsure_url):
    if not 'http' in unsure_url:
        return 'http://' + unsure_url
    else:
        return unsure_url

def type_of(full_url):
    if re.search(r'/.', remove_protocol(full_url)):
        return 'article'
    else:
        return 'blog'

def make_absolute(full_url, partial_url):
    protocol = get_protocol(full_url)
    host = get_host(full_url)
    return protocol + host + partial_url

#FETCHTING/PARSING META DATA
def fetch_html(full_url):
    try:
        r = requests.get(full_url)
    except:
        return None
    return r.text

def get_host(full_url):
    return re.sub(r'/.*', '', remove_protocol(full_url))

def get_description(html):
    #<meta name="description" content="GRAB_THIS">
    description = re.search(r'<meta (property|name)=".*?description" content="(.+?)"', html)
    if description:
        return description.group(2)
    return ""

def get_image_ref(html, full_url):
    #<meta name="image" content="GRAB_THIS" />
    image = re.search(r'<meta (property|name)=".*?image" content="(.+?)"', html)
    if image:
        image = image.group(2)
        #adjust for relative url
        if image[0] == '/':
            image = make_absolute(full_url, image)
        return image
    return ""

def get_author(html):
    #<meta name="author" content="GRAB_THIS">
    description = re.search(r'<meta (property|name)=".*?author" content="(.+?)"', html)
    if description:
        return description.group(2)
    return ""

def get_article_title(html):
    title = re.search(r'<title>(.+?)</title>', html)
    if title:
        return title.group(1)
    return ""

def get_site_info(url):
    full_url = add_protocol(url)
    site_type = type_of(full_url)
    source = get_host(full_url)    
    site = {
        'url': full_url,
        'site_type': site_type,
        'site_name': source,
        #defaults
        'article_name': '',
        'author_name': '',
        'image': '',
        'description': ''
    }
    html = fetch_html(full_url)
    if html:
        image_ref = get_image_ref(html, full_url)
        author = get_author(html)
        title = get_article_title(html)
        description = get_description(html)
        site["image"] = image_ref
        site["description"] = description
        if site_type == 'article':
            site["article_name"] = title
            site["author_name"] = author
    return site

#DB READ/WRITE
def query_by_id_and_type(site_id, site_type):
    if site_type == 'article':
        query = session.query(Article).filter(Article.id == site_id)
        if query.count() > 0:
            return query
    elif site_type == 'blog':
        query = session.query(Blog).filter(Blog.id == site_id)
        if query.count() > 0:
            return query
    return None

# # Depreciated
# def verify_site_by_url(url):
#     site_type = type_of(url)
#     url = remove_protocol(url)
#     if site_type: 'article':
#         return session.query(Article).filter(remove_protocol(Article.url) == url).count() > 0
#     elif site_type: 'blog':
#         return session.query(Blog).filter(remove_protocol(Blog.url) == url).count() > 0
#     else:
#         return False

def get_id_from_url(url):
    site_type = type_of(url)
    if site_type == 'article':
        try:
            Q = session.query(Article).filter(Article.url == url).one().id
        except:
            Q = None
    elif site_type == 'blog':
        try:
            Q = session.query(Blog).filter(Blog.url == url).one().id
        except:
            Q = None
    return Q

# # Depreciated
# def verify_site_by_id_and_type(site_id, site_type):
#     return query_by_id_and_type(site_id, site_type).count() > 0

def get_sites_by_user_id(user_id):
    user_sites = session.query(User_site).filter(User_site.user_id == user_id).all()
    
    sites = []
    for s in user_sites:
        site = {}
        site['user_site_id'] = s.id
        site['type'] = s.site_type
        site['comment'] = s.comment
        site_Q = query_by_id_and_type(s.site_id, s.site_type).one()
        for column in site_Q.__table__.columns:
            site[column.name] = getattr(site_Q, column.name)
        sites.append(site)
    return {'sites':sites}

def add_or_update_site(info):
    url = info["url"]
    site_type = type_of(url)
    site_id = get_id_from_url(url)
    if site_id:
        site_Q = query_by_id_and_type(site_id, site_type)
        if site_type == 'article':
            site_Q.update({
                'site_name': info['site_name'],
                'article_name': info['article_name'],
                'author_name': info['author_name'],
                'image': info['image'],
                'description': info['description']
            })
        if site_type == 'blog':
            site_Q.update({
                'site_name': info['site_name'],
                'image': info['image'],
                'description': info['description']
            })
        session.commit()
    else:
        if site_type == 'article':
            session.add(Article(info['site_name'], info['article_name'], info['author_name'], info['url'], info['image'], info['description']))
        if site_type == 'blog':
            session.add(Blog(info['site_name'], info['url'], info['image'], info['description']))
        session.commit()
        site_id = get_id_from_url(url)
    return site_id

# # Depreciated
# def add_site_to_sites(name, url, article):
#     session.add(Site(name, url, article))
#     session.commit()
#     return session.query(Site).filter(Site.id == id).one().id

def add_user_to_site(user_id, site_id, site_type, comment):
    Q = session.query(User_site).filter(User_site.user_id == user_id, User_site.site_id == site_id, User_site.site_type == site_type)

    #Check if user hasn't already added site
    if Q.count() == 0:
        site = User_site(int(user_id), int(site_id), site_type, comment)
        session.add(site)
        session.commit()
    else:
        return None
    user_site_id = session.query(User_site).order_by(User_site.id.desc()).first().id
    response = {'user_site_id': user_site_id, 'site_id': site_id, 'site_type': site_type, 'comment': comment}
    site_info_Q = query_by_id_and_type(site_id, site_type).one()
    for column in site_info_Q.__table__.columns:
        response[column.name] = getattr(site_info_Q, column.name)
    return response

def edit_user_to_site(id, comment):
    user_site_Q = session.query(User_site).filter(User_site.id == id)
    user_site = user_site_Q.one()
    site_id = user_site.site_id
    site_type = user_site.site_type

    if not user_site_Q.count() > 0:
        return None
    else:
        user_site_Q.update({'comment':comment})
        session.commit()

    site = {'user_site_id': id, 'site_id': site_id, 'site_type': site_type, 'comment': comment}
    site_info = query_by_id_and_type(site_id, site_type).one()
    for column in site_info.__table__.columns:
        site[column.name] = getattr(site_info, column.name)
    return site

def remove_user_from_site(id):
    user_site_Q = session.query(User_site).filter(User_site.id == id)
    if not user_site_Q.count() > 0:
        return None
    else:
        session.delete(user_site_Q.one())
        session.commit()
        return id

def get_comments(user_id, site_type, site_id):
    try:
        return session.query(User_site).filter(User_site.user_id == user_id, User_site.site_type == site_type, User_site.site_id == site_id).one().comment
    except:
        return ""
