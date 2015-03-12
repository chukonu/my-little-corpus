from webapp2_extras.routes import RedirectRoute as Route

import admin


urlpatterns = [
    # Admin panel
##    Route('/', MainPage, 'index', strict_slash=True),
##    Route('/submit-translation/', Submit_Translation, 'submit-translation', strict_slash=True),
##    Route('/create-collection/', Create_Collection, 'create-collection', strict_slash=True),
    # Real life usage:
    Route('/', admin.AdminHandler, 'admin_panel', strict_slash=True),
    # and CRUD - new, edit, all, view, delete items
    Route('/<model>/<action>/', admin.CrudHandler, 'admin_crud',
          strict_slash=True),
    # AJAX - Translation
    Route('/<id:\d+>/', admin.Ajax_translation_handler, 'ajax_translation', strict_slash=True),
]

# mylittlecorpus.appspot.com/
# /
# /collections/
# /translations/
# /collection/<id>/<action>/
# /translation/<id>/<action>/
