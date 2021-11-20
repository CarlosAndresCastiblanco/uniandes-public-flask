from datetime import datetime
from celery import Celery
from celery.utils.log import get_task_logger
from pydub import AudioSegment
import os
from pathlib import Path
from celery.schedules import crontab
from datetime import timedelta
from pydub.utils import which
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.sqltypes import DateTime
import smtplib

engine = create_engine('mysql+pymysql://admin:12345678@converter.cmkisbgiomh9.us-east-1.rds.amazonaws.com:3306/converter', echo = True)
Session = sessionmaker(bind = engine)
session = Session()
Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(50))
    conversiones = relationship("Conversion")

class Conversion(Base):
    __tablename__ = 'conversion'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    origen = Column(String(50))
    destino = Column(String(50))
    estado = Column(String(50))
    fecha = Column(String(50))
    usuario_id = Column(Integer, ForeignKey('usuario.id'))

AudioSegment.converter = which("ffmpeg")
appC = Celery('tasks', broker='redis://127.0.0.1:6379/0')
logger = get_task_logger(__name__)
PATH = str(Path().absolute(), )

appC.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'tasks.add',
        'schedule': 5.0,
    },
}
appC.conf.timezone = 'UTC'





@appC.task(name="tasks.add")
def test():
    logger.info('hola mundo')
    print(engine.table_names())
    result = session.query(Conversion).all()
    print(result)
    for row in result:
        print(row)
        if row.estado == 'uploaded':
            try:
                archivo = AudioSegment.from_file("/nfs/general/originales/origin-{}-{}.{}".format(row.usuario_id, row.id, row.origen),
                                            str(row.origen))
                archivo.export("/nfs/general/originales/destino-{}-{}.{}".format(row.usuario_id, row.id, row.destino),
                        format=row.destino)
                row.estado = "processed"
                session.commit()
                print('convertido satisfactoriamente',"/nfs/general/originales/destino-{}-{}.{}".format(row.usuario, row.id, row.destino))
                #usuario = session.query(Usuario).filter(row.usuario_id)
                #remitente = "Desde gnucita <ebahit@member.fsf.org>" 
                #destinatario = "Mama de Gnucita <{}>".format(usuario.email)
                #asunto = "E-mal HTML enviado desde Python" 
                #mensaje = """Audio Converter!<br/> <br/> 
                #Este es un <b>e-mail</b> confirmando la finalización de la conversión """
                ##email = """From: %s 
                #To: %s 
                #MIME-Version: 1.0 
                #Content-type: text/html 
                #Subject: %s 
                #%s
                #""" % (remitente, destinatario, asunto, mensaje)
                #smtp = smtplib.SMTP('localhost')
                #smtp.sendmail(remitente, destinatario, email)
            except Exception as err: 
                print('error convirtiendo')
                print(err)
                print(err.args)

    """ with app.app_context:
        audios = Conversion.query.all()
        logger.info(audios)
        print('hola mundo')  """


@appC.task()
def sumar_numeros(x, y):
    print("-> Se generó una tarea [{}]: {} + {}".format(datetime.now(), x, y))
    logger.info('Adding {0} + {1}'.format(x, y))
    return x + y

"""@app.task
def convertir(file, origin, destino, identificador):
        txt = file.filename.split('.')
        archivo = AudioSegment.from_file("originales/{}".format(file.filename),
                                        str(origin))
        archivo.export("originales/{}.{}".format(
            txt[0].replace("origin", "destino"), destino),
                    format=destino)
        task = Conversion.query.get_or_404(identificador)
        task.estado = "processed"
        db.session.commit()

@app.task
def convertirMod(nombre,outputname, origin, destino, identificador):
        archivo = AudioSegment.from_file(nombre,
                                        str(origin))
        archivo.export(outputname.replace(origin,destino),
                    format=destino)
        task = Conversion.query.get_or_404(identificador)
        task.estado = "processed"
        db.session.commit()
 """