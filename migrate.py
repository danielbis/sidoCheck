from flask import Flask
from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"

app = Flask(__name__)
Bootstrap(app)
# Configurations
app.config.from_object('config')


# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)
db.drop_all()