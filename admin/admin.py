# -*- coding: utf-8 -*-
import os
import urllib
import webapp2
from google.appengine.ext import ndb
from webapp2_extras import jinja2

from models_admin import *
import settings


actions_map = {
    "new": "Add",
    "all": "All",
    "edit": "Edit",
    "delete": "Delete",
    "view": "View"
}


class BaseHandler(webapp2.RequestHandler):
    """
    Request handler, which knows how to render himself into template.
    """

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, template, **context):
        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)


class AdminHandler(BaseHandler):
    """
    Admin panel main page.
    """
    #@admin_required
    def get(self):
        c = eval('Collection')
        collections = c.query().order(-Collection.date_translations_updated).fetch()
        self.render_template("admin_panel.html", **{"items": collections})


class CrudHandler(BaseHandler):
    """
    Admin CRUD UI.

    Model must have Meta class, e.g.:
    class Model(ndb.Model):
        ...

        class Meta():
            # templates
            # CRUD use '/admin/[model]/' path prefix, model name is lower case
            c = "" # new item template
            r = "" # items list template
            u = "" # edit item template
            d = "" # delete item template

            # sample
            def __init__(self):
                self.fields = [
                    fields.TextField("name", "Name:"),
                    fields.KeyField("site", "Select site:", query=Site.query()),
                    fields.MoneyField("budget", "Budget:", required=True),
                    fields.CheckboxField("is_active", "Active?"),
                    fields.DateField("due_date", "Due date")
                    ...
                ]
            }
    """

    # default template names
    new = "create.html"
    all = "read.html"
    edit = "update.html"
    delete = "delete.html"
    view = "view.html"

    # Decorator/auth usage for your consideration
    #@admin_required
    def get(self, model, action):
        item = None
        items = None
        items_count = 0
        cursor = self.request.get('cursor')
        next_c = None
        per_page = getattr(settings, "PER_PAGE", 10)
        item_id = self.request.GET.get("id", None)
        msg = self.request.GET.get("msg", None)
        children = None
        
        children_sorted = []

        if not model in MODELS:
            raise Exception(
                "Model `%s` not registered in `models_admin.py`" % model
            )

        m = eval(model.title())

        # model template for given action
        # here is where to specifically design for a model
        path = "/admin/%s/" % model.lower()
        # 先進入此  模型的 Meta 中，尋找此  模型自己給該  操作分的模板
        # Nice! 有一般的處理方法，也有  模型自己發揮的空間
        template = m.Meta.__dict__.get(action, getattr(self, action))
        fields = m.Meta().fields
        legend = m.Meta().legend

        # if no template - fallback to default one
        if not os.path.isfile('./templates' + path + template):
            path = "/admin/"

        # item
        if item_id:
            item = m.get_by_id(int(item_id))
            children_sorted = item.find_children()
            if action == "edit":
                for f in fields:
                    f.initial = nested_getattr(item, f.field)

        # 若新建，
        # 將網址所附參數逐一賦予作字段之初始值
        # 若參數名與表單字段所定義者不符
        # 則不予賦值
        if action == "new":
            for f in fields:
                f.initial = self.request.GET.get(f.field, "")

        # list
        if action == "all":
            items = m.query()
            if hasattr(m.Meta(), "order_by"):
                items = items.order(m.Meta().order_by)

            items_count = items.count()

            # -- PAGINATE RESULTS --
            cursor = ndb.Cursor(urlsafe=cursor)
            items, next_curs, more = items.fetch_page(per_page,
                start_cursor=cursor)
            if more:
                next_c = next_curs.urlsafe()
            else:
                next_c = None
        
        content = {
                   "model": model,
                   "model_plural": m.plural,
                   "action": actions_map[action],
                   "legend": legend,
                   "fields": fields,
                   "item": item,
                   "items": items,
                   "items_count": items_count,
                   "cursor": next_c,
                   "per_page": per_page,
                   "msg": msg,
                   
                   "children_sorted": children_sorted,
                   }
        self.render_template(path + template, **content)

    # Decorator/auth usage for your consideration
    #@admin_required
    def post(self, model, action):
        item = None
        item_id = self.request.GET.get("id", None)
        data = self.request.POST
        msg = ""

        if not model in MODELS:
            raise Exception(
                "Model `%s` not registered in `models_admin.py`" % model
            )

        m = eval(model.title())

        # item: Delete or Update
        if item_id:
            item = m.get_by_id(int(item_id))

            if action == "delete":
                msg = "%s '%s' has been removed" % (model.title(), item)
                item.key.delete()
            elif action == "edit":
                fields = m.Meta().fields
                for f in fields:
                    nested_setattr(item, f.field, f.parse(data.getall(f.field)))
                item.put()
                msg = "%s '%s' saved" % (model.title(), item)
        # Create
        elif action == "new":
            fields = m.Meta().fields
            item = m()
            for f in fields:
                nested_setattr(item, f.field, f.parse(data.getall(f.field)))
            # new: handles exceptions
            #for f in fields:
            #   try:
            #       nested_setattr(item, f.field, f.parse(data.getall(f.field)))
            #   except ValueError:
            #       notify(u"Oops, there is something wrong with the format of the data. Please check again. ")
            #       self.redirect(self.uri_for('admin_crud', model=model, action="new"))
            item.put()
            msg = "%s '%s' added" % (model.title(), item)

        # new method
        item.additional_mod()
        
        query_params = {"msg": msg.encode("utf-8")}
        self.redirect(self.uri_for('admin_crud', model=model, action="all") \
                      + "?" + urllib.urlencode(query_params))


def nested_getattr(obj, name):
    """ Same as getattr but can handle nested name, i.e. objectA.objectB.objectC. """
    return reduce(lambda o, n: getattr(o,n), name.split('.'), obj)


def nested_setattr(obj, name, value):
    """ Same as setattr but can handle nested name, i.e. objectA.objectB.objectC. """
    nested_names = name.split('.')
    for n in nested_names[:-1]:
        new_obj = getattr(obj, n)

        # StructuredProperty is not created yet and holds None
        if new_obj is None:
            struct_obj = obj._properties[n]._modelclass()
            setattr(obj, n, struct_obj)
            obj = struct_obj
        else:
            obj = new_obj
            
    setattr(obj, nested_names[-1], value)

class Ajax_translation_handler(BaseHandler):
    def get(self, id):
        # html template
        tpl_path = '/ajax/translation.html'
        
        # search by id
        trans = Translation.get_by_id(int(id))
        
        # return html code
        # lesson: do not use `return` but `self.response.write`
        if trans is not None:
            # new: locale logic
            direction = int(self.request.GET.get("direction", '0'))
            if direction == 0:
                source_locale = 'zh-Hant'
                target_locale = 'en'
            else:
                source_locale = 'en'
                target_locale = 'zh-Hant'
            
            content = {
                "translation": trans,
                "source_locale": source_locale,
                "target_locale": target_locale,
                }
            self.render_template(tpl_path, **content)
        else:
            self.response.write("<p>There is no this translation. </p>")
