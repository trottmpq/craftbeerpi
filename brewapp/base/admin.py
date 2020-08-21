from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from .. import app, db
from .model import (Config, Fermenter, FermenterStep, Hardware,
                                Hydrometer, Kettle, RecipeBooks,
                                RecipeBookSteps, Step)

admin = Admin(app)
admin.add_view(ModelView(Step, db.session))
admin.add_view(ModelView(RecipeBooks, db.session))
admin.add_view(ModelView(RecipeBookSteps, db.session))
admin.add_view(ModelView(Kettle, db.session))
admin.add_view(ModelView(Hardware, db.session))
admin.add_view(ModelView(Config, db.session))
admin.add_view(ModelView(Fermenter, db.session))
admin.add_view(ModelView(FermenterStep, db.session))
admin.add_view(ModelView(Hydrometer, db.session))
