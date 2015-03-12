# -*- coding: utf-8 -*-
# This is sample models
# Note Meta() class inside model - it is define form fields for CRUD
# and templates for list/new/edit/delete operations.
# Default templates located inside /templates/admin/
# To subclass template: create a folder inside /templates/admin/
# with model name lowercase.

from google.appengine.ext import ndb

from admin import fields

def truncate(raw, limit=30, asian=False):
    """
    功能：砍字符串的頭
    """
    try:
        limit = int(limit)
    except ValueError:
        return raw

    raw = unicode(raw)

    if len(raw) <= limit:
        return raw

    if asian == True:
        return raw[:limit] + ' ... '
    else:
        raw = raw[:limit]
        words = raw.split(' ')[:-1]
        return ' '.join(words) + ' ... '

class Item(ndb.Model):
    """
    Sample item model
    """
    name = ndb.StringProperty()
    description = ndb.TextProperty()
    image = ndb.BlobProperty()

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    # this is where Admin CRUD form lives
    class Meta():
        def __init__(self):
            self.fields = [
                fields.TextField("name", "Name", required=True),
                fields.BigTextField("description", "Description"),
                fields.FileField("image", "Image")
            ]
            self.order_by = Item.name


class Order(ndb.Model):
    """
    More complex mdoel
    """
    item = ndb.KeyProperty(Item)
    is_payed = ndb.BooleanProperty()
    date_added = ndb.DateProperty()
    customer = ndb.StringProperty()
    memo = ndb.TextProperty()
    price = ndb.FloatProperty()
    item_struct = ndb.StructuredProperty(Item)
    

    def __unicode__(self):
        return "%s ordered %s" % (self.customer, self.item.get())

    def __str__(self):
        return self.__unicode__()

    class Meta():
        def __init__(self):
            self.fields = [
                fields.KeyField("item", "Item", required=True,
                    query=Item.query()),
                fields.DateField("date_added", "Date", required=True),
                fields.CheckboxField("is_payed", "Payed"),
                fields.TextField("customer", "Customer", required=True),
                fields.BigTextField("memo", "Memo"),
                fields.FloatField("price", "Price"),
                fields.TextField("item_struct.name", "Item Name", required=True),
                fields.BigTextField("item_struct.description", "Item Description"),
                fields.FileField("item_struct.image", "Item Image")
            ]

# class NewModel(ndb.Model):

class Collection(ndb.Model):
    editor = ndb.UserProperty()
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    name = ndb.StringProperty()
    date = ndb.DateProperty()
    plural = "Collections"
    stream = ndb.IntegerProperty()
    type = ndb.IntegerProperty()
    date_translations_updated = ndb.DateTimeProperty(auto_now=True)
    times_translations_updated = ndb.IntegerProperty()

    def __unicode__(self):
        return self.name
    # self.name + " " + self.date.strftime("%d/%m/%y")

    def __str__(self):
        return self.__unicode__()

    def find_children(self):            
        translations_query = Translation.query(Translation.collection == self.key).order(Translation.date).order(Translation.date_submitted)
        children_count = translations_query.count()
        translations = translations_query.fetch()
        list_translations_sorted = []
        d = translations[0].date
        l = []
        for translation in translations:
            if d != translation.date:
                d = translation.date
                list_translations_sorted.append(l)
                l = []
            l.append(translation)
        list_translations_sorted.append(l)
        return list_translations_sorted

    def additional_mod(self):
        return None

    class Meta():
        view = "view.html"
        def __init__(self):
            self.legend = "Collection"
            self.fields = [
                fields.TextField("name", "Name", required=True),
                fields.DateField("date", "Date", required=True),
                fields.RadioField("stream", "Stream", options=['Chinese to English', 'English to Chinese']),
                fields.RadioField("type", "Type", options=['Translation', 'Simultaneous Interpreting', 'Consecutive Interpreting'])
            ]
            self.order_by = -Collection.date

class Translation(ndb.Model):
    editor = ndb.UserProperty()
    date_submitted = ndb.DateTimeProperty(auto_now_add=True)
    author = ndb.StringProperty()
    source_text = ndb.TextProperty()
    target_text = ndb.TextProperty()
    date = ndb.DateProperty()
    interpreting = ndb.BooleanProperty()
    plural = "Translations"
    # new param
    collection = ndb.KeyProperty(kind=Collection)

    def __unicode__(self):
        return "%s" % truncate(self.target_text, 140, False)
        # I do not know why I got stuck here for a long time :-(

    def __str__(self):
        return self.__unicode__()

    def find_children(self):
        return None

    def additional_mod(self):
        # retrieving an entity from a key
        parent_collection = self.collection.get()
        # parent_collection.times_translations_updated = parent_collection.times_translations_updated + 1
        return parent_collection.put()

    class Meta():
        # new = "create.html"
        def __init__(self):
            self.legend = "Translation"
            collections_query = Collection.query().order(-Collection.date)
            self.fields = [
                fields.BigTextField("source_text", "Source Text", required=True),
                fields.BigTextField("target_text", "Target Text", required=True),
                fields.KeyField("collection", "Collection", required=True,
                                query=collections_query),
                fields.DateField("date", "Date", required=True),
                fields.TextField("author", "Translator", required=True)
            ]
