from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts

#authenticate
wp_url = '<WPWEBSITE>/xmlrpc.php'
wp_username = 'USERNAME'
wp_password = 'PASSWORD'
wp = Client(wp_url, wp_username, wp_password)

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
        wp.call(NewPost(post))
