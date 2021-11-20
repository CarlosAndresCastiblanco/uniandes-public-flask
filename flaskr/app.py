#from flaskr import create_app
from vistas.vistas import RecursoDescargar, RecursoLogin, RecursoTarea, RecursoTareas, RecursoUsuario
from models.modelos import db, Usuario
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:12345678@converter.cmkisbgiomh9.us-east-1.rds.amazonaws.com:3306/converter'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'k#4ASfdfjo4343@$.-'
app.config['UPLOAD_FOLDER'] = './originales'
app.config['PROPAGATE_EXCEPTIONS'] = True

app_context = app.app_context()
app_context.push()


db.init_app(app)
api = Api(app)
jwt = JWTManager(app)

api.add_resource(RecursoUsuario, '/api/auth/signup')
api.add_resource(RecursoLogin, '/api/auth/login')
api.add_resource(RecursoTareas, '/api/tasks')
api.add_resource(RecursoTarea, '/api/tasks/<int:id_conversion>')
api.add_resource(RecursoDescargar, '/api/files/<string:name>')
#testing
with app.app_context():
    u = Usuario(username='cris', password='p', email='q@q.com')
    print(Usuario.query.all())


