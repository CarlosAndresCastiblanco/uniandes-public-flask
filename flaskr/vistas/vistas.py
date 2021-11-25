from flask_restful import Resource

# from flaskr.tasks import convertir, convertirMod
from flaskr.models.modelos import db, Usuario, usuario_schema, Conversion, conversion_schema, conversiones_schema
from flaskr.storage.storage import *
from flask import request, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_jwt_extended import get_jwt_identity
import os
from datetime import date
import time

formatos = ["mp3", "ogg", "wav"]


class RecursoUsuario(Resource):
    def post(self):
        if not "username" in request.json:
            return {"ok": False, "msg": "username is required"}
        if not "email" in request.json:
            return {"ok": False, "msg": "email is required"}
        if not "password" in request.json:
            return {"ok": False, "msg": "password is required"}
        if not "password2" in request.json:
            return {"ok": False, "msg": "password2 is required"}
        if request.json['password'] != request.json['password2']:
            return {"ok": False, "msg": "passwords must be the same"}
        nuevo_usuario = Usuario(username=request.json['username'],
                                email=request.json['email'],
                                password=request.json['password'])
        db.session.add(nuevo_usuario)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return {"ok": False, "msg": 'email or username already used'}, 409
        return usuario_schema.dump(nuevo_usuario)


class RecursoLogin(Resource):
    def post(self):
        if not "username" in request.json:
            return {"ok": False, "msg": "username is required"}
        if not "password" in request.json:
            return {"ok": False, "msg": "password is required"}
        usuarioBD = Usuario.query.filter_by(
            username=request.json['username'],
            password=request.json['password']).all()
        if usuarioBD:
            return {
                       'token': create_access_token(identity=usuarioBD[0].id)
                   }, 200
        else:
            return {"ok": False, "msg": "wrong credentials"}, 400


class RecursoTareas(Resource):
    @jwt_required()
    def get(self):
        usuario = get_jwt_identity()
        tareas = Usuario.query.get_or_404(usuario)
        return conversiones_schema.dump(tareas.conversiones)

    @jwt_required()
    def post(self):
        usuario = get_jwt_identity()
        if not "fileName" in request.files:
            return {'ok': False, 'msg': 'fileName is required'}
        if not "newFormat" in request.form:
            return {'ok': False, 'msg': 'newFormat is required'}
        if not request.form['newFormat'] in formatos:
            return {"ok": False, 'msg': 'new Format only support the following types: mp3,ogg,wav'}
        f = request.files['fileName']
        txt = f.filename.split('.')
        extension = txt[1]
        name = txt[0]
        if not extension in formatos:
            return {"ok": False, 'msg': 'file only support the following types: mp3,ogg,wav'}

        nueva_conversion = Conversion(nombre=name,
                                      origen=extension,
                                      destino=request.form['newFormat'],
                                      estado="uploaded",
                                      usuario_id=usuario,
                                      fecha=str(date.today())
                                      )
        db.session.add(nueva_conversion)
        db.session.commit()
        response = conversion_schema.dump(nueva_conversion)

        f.filename = "origin-{}-{}.{}".format(usuario, response["id"], extension)
        f.save(
            "flaskr/originales/{}".format(f.filename)
        )
        object_name = get_object_name(f.filename)
        upload_file("flaskr/originales/{}".format(f.filename), object_name)
        remove_file("flaskr/originales/{}".format(f.filename))
        send_message_queue('firstqueue','autor','1','first Hi!!!!!!! message')
        receive_and_delete_messages_queue()
        return conversion_schema.dump(nueva_conversion)


class RecursoTarea(Resource):
    @jwt_required()
    def get(self, id_conversion):
        task = Conversion.query.get_or_404(id_conversion)
        return conversion_schema.dump(task)

    @jwt_required()
    def put(self, id_conversion):
        usuario = get_jwt_identity()
        if not request.json['newFormat'] in formatos:
            return {"ok": False, 'msg': 'only support the following types: mp3,ogg,wav'}
        task = Conversion.query.get_or_404(id_conversion)
        if task:
            if task.estado == 'processed':
                if find_object("destino-{}-{}.{}".format(usuario, id_conversion, task.destino)):
                    delete_object("destino-{}-{}.{}".format(usuario, id_conversion, task.destino))
                else:
                    print("The file does not exist")
            task.destino = request.json['newFormat']
            task.estado = "uploaded"
            db.session.commit()
            # with open("originales/origin-{}-{}.{}".format(usuario, task.id ,task.origen)) as f:
            #    data = f.read()
            # f=open("originales/origin-{}-{}.{}".format(usuario, task.id ,task.origen)).read()
            try:
                ruta = "flaskr/originales/origin-{}-{}.{}".format(usuario, task.id, task.origen)
                rutaDestino = ruta.replace('origin-', 'destino-')
                # convertirMod.delay("originales/origin-{}-{}.{}".format(usuario, task.id ,task.origen),
                # rutaDestino,task.origen,task.destino,id_conversion)
            except:
                return {"ok": False, "msg": "task not exist"}
            return conversion_schema.dump(task)
        else:
            return {"ok": False, "msg": "task not exist"}

    @jwt_required()
    def delete(self, id_conversion):
        task = Conversion.query.get_or_404(id_conversion)
        db.session.delete(task)
        db.session.commit()
        return {"ok": True, "msg": "task removed"}


class RecursoDescargar(Resource):
    @jwt_required()
    def get(self, name):
        try:
            downloading_files('flaskr/originales/{}'.format(name), name)
            return send_from_directory("originales/",
                                       path=name,
                                       as_attachment=True)
        except:
            return '', 404
