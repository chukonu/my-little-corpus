import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

import settings
import urls

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_COLLECTION_NAME = 'default_collection'

def collection_key(collection_name=DEFAULT_COLLECTION_NAME):
    """Constructs a Datastore key for a Collection entity with collection_name."""
    return ndb.Key('Collection', collection_name)

##class Collection(ndb.Model):
##    editor = ndb.UserProperty()
##    date_created = ndb.DateTimeProperty(auto_now_add=True)
##    name = ndb.StringProperty()
##    date = ndb.DateProperty()
##
##class Translation(ndb.Model):
##    editor = ndb.UserProperty()
##    date_submitted = ndb.DateTimeProperty(auto_now_add=True)
##    author = ndb.UserProperty()
##    source_text = ndb.TextProperty()
##    target_text = ndb.TextProperty()
##    date = ndb.DateProperty()
##    interpreting = ndb.BooleanProperty()

##class MyHandler(webapp2.RequestHandler):
##    user = users.get_current_user()
##    def dispatch(self):
##        if self.user is None:
##            self.redirect(users.create_login_url(self.request.uri))
##        else:
##            super(MyHandler, self).dispatch()

class MainPage(webapp2.RequestHandler):
    def get(self):
##        template_values = {
##            'username': self.user.nickname()
##        }
##        template = JINJA_ENVIRONMENT.get_template('index.html')
##        self.response.write(template.render(template_values))
        user = users.get_current_user()
        if user:
            template_values = {
                'username': user.nickname()
            }
            template = JINJA_ENVIRONMENT.get_template('templates/index.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class Submit_Translation(webapp2.RequestHandler):
    def get(self):

        template = JINJA_ENVIRONMENT.get_template('templates/submit-translation.html')
        self.response.write(template.render())
##    def post(self)

class Create_Collection(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/create-collection.html')
        self.response.write(template.render())
##    def post(self)
##
##class Search(webapp2.RequestHandler)

##application = webapp2.WSGIApplication([
##    ('/', MainPage),
##    ('/submit-translation', Submit_Translation),
##    ('/create-collection', Create_Collection),
####    ('/search', Search)
##], debug=True)
application = webapp2.WSGIApplication(urls.urlpatterns,
                                      debug=settings.DEBUG, config=settings.CONFIG)
