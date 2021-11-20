from flaskr import create_app
from .vistas import RecursoDescargar, RecursoLogin, RecursoTarea, RecursoTareas, RecursoUsuario
from .models import db, Usuario
from flask_restful import Api
from flask_jwt_extended import JWTManager

app = create_app('default')
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


