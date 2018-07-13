from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.methods.users import GetUserInfo
from xmlrpc.client import Transport

#authenticate
wp_url = "<WEBSITE>"
wp = None

class SpecialTransport(Transport):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'

def add_photo(article, filename):
        data = {
        'name': 'picture.jpg',
        'type': 'image/jpeg',  # mimetype
        }
        with open(filename, 'rb') as img:
                data['bits'] = xmlrpc_client.Binary(img.read())

        response = wp.call(media.UploadFile(data))
        article.append('<img class="alignnone size-medium wp-image-12" src="' + response['url']  + '" alt="" width="300" height="300" hspace="20" />')

def add_text(article, text):
        article.append(text)

categories = ['test']

def post_article(data, title):
        article = []
        for d in data:
                if d.startswith('/home'): # i still dont like this
                        add_photo(article, d)
                else:
                        add_text(article, d)
        post = WordPressPost()
        post.title = title
        post.content = '\n'.join(article) # oof
        post.post_status = 'publish'
        post.terms_names = {
                'post_tag': ['test', 'firstpost'],
                'category': categories
        }
        id = wp.call(NewPost(post))
        a = wp.call(posts.GetPost(id))
        return a.link

def auth(username, password):
        global wp
        wp = Client(wp_url, username, password, transport=SpecialTransport())
        wp.call(GetUserInfo())
