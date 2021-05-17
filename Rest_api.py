from flask import Flask, request, send_from_directory
from flask_restful import Api, Resource
from datetime import datetime, timedelta
import configparser
from user import Recording, Api_key
import pandas as pd
from rofl import vid_from_array, connect_jsons
import uuid
import api as API
import os
import sqlite3
from db import init_db_command, init_db
from dateutil.parser import isoparse
from celery import Celery
from stream import stream
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
from stream import json_recall, stream_background
from flask_cors import CORS

app = Flask(__name__, static_folder='./build', static_url_path='/')
api = Api(app)
app.config.update(BEDUG=True, TESTING=True,
                  ALLOWED_EXTENSIONS=['mp4'], LOGFILE='app.log',
                  UPLOAD_FOLDER='queue', RESULT_FOLDER='video_output',
                  CELERY_BROKER_URL='redis://localhost:6379',
                  CELERY_RESULT_BACKEND='redis://localhost:6379')
CORS(app)
celery = Celery(app.name)
celery.config_from_object('celeryconfig')

API.credentials = service_account.Credentials.from_service_account_file(API.SERVICE_ACCOUNT_FILE, scopes=API.SCOPES)
API.service = build('drive', 'v3', credentials=API.credentials)
with open('Emotions_Project-481579272f6a.json', 'r') as j:
    API.data = json.load(j)
# api.build_service()
GOOGLE_CLIENT_ID = API.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = API.GOOGLE_CLIENT_SECRET
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


class Config(Resource):

    def get(self, id_=0):
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            list = {}
            if id_ != 0:
                list = {'confidence_threshold': config[str(id_)]['confidence_threshold'],
                        'top_k': config[str(id_)]['top_k'],
                        'nms_threshold': config[str(id_)]['nms_threshold'],
                        'keep_top_k': config[str(id_)]['keep_top_k'],
                        'vis_thres': config[str(id_)]['vis_thres'],
                        'network': config[str(id_)]['network'],
                        'distance_threshold': config[str(id_)]['distance_threshold'],
                        'samples': config[str(id_)]['samples'],
                        'eps': config[str(id_)]['eps'],
                        'fps_factor': config[str(id_)]['fps_factor']
                        }
                return list, 200
            else:
                i = 1
                while i <= len(config.sections()) - 1:
                    list[i] = {'confidence_threshold': config[str(i)]['confidence_threshold'],
                               'top_k': config[str(i)]['top_k'],
                               'nms_threshold': config[str(i)]['nms_threshold'],
                               'keep_top_k': config[str(i)]['keep_top_k'],
                               'vis_thres': config[str(i)]['vis_thres'],
                               'network': config[str(i)]['network'],
                               'distance_threshold': config[str(i)]['distance_threshold'],
                               'samples': config[str(i)]['samples'],
                               'eps': config[str(i)]['eps'],
                               'fps_factor': config[str(i)]['fps_factor']
                               }
                    i += 1
                return list, 200
        except:
            return "Internal Server Error", 500

    def put(self, confidence_threshold, top_k, nms_threshold,
            keep_top_k, vis_thres, network,
            distance_threshold, samples, eps, fps_factor, id_=0):
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            if id_ == 0:
                id_ = len(config.sections())
            config[str(id_)] = {'confidence_threshold': confidence_threshold,
                               'top_k': top_k,
                               'nms_threshold': nms_threshold,
                               'keep_top_k': keep_top_k,
                               'vis_thres': vis_thres,
                               'network': network,
                               'distance_threshold': distance_threshold,
                               'samples': samples,
                               'eps': eps,
                               'fps_factor': fps_factor
                                }
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            return id_, 201
        except:
            return "Internal Server Error", 500

    def patch(self, id_=0):
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            if id_ == 0:
                return "Config not changed", 200
            else:
                config['ACTIVE'] = config[str(id_)]
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            return 202
        except:
            return "Config not found", 404


class Record(Resource):

    def get(self, room_num=0, date=0, time=0):
        try:
            # date = datetime.datetime.strptime(date, '%Y-%m-%d')
            # time = datetime.datetime.strptime(time, '%H:%M')
            if room_num != 0 and date != 0 and time != 0:
                rec = Recording.get(room_num, date, time)
                print(rec)
                if rec is None:
                    return "Video not found", 404
                rec = json.loads(rec.json)
                return rec, 200
            else:
                db = sqlite3.connect('sqlite_db')
                table = pd.read_sql_query("SELECT * from recording", db)
                table = table.to_dict()
                return table, 200
        except:
            return "Server error", 500

    def delete(self, room_num, date, time):
        try:
            # date = datetime.datetime.strptime(date, '%Y-%m-%d')
            # time = datetime.datetime.strptime(time, '%H:%M')
            try:
                Recording.delete(room_num, date, time)
            except:
                return "Video not found", 404
            # rec = json.loads(rec.json)
            return 'Recording deleted', 200
        except:
            return "Server error", 500


@app.route("/api/plot", methods=['PUT'])
def api_():
    if 'key' in request.headers:
        keys = list(Api_key.get_dataframe()['uuid'])
        if request.headers['key'] in keys:
            json = request.json
            if 'room' in json and 'start_time' in json and 'end_time' in json:
                print(json)
                start = isoparse(json['start_time'])
                end = isoparse(json['end_time'])
                if start.strftime('%Y-%m-%d') != end.strftime('%Y-%m-%d'):
                    return "Bad request", 400
                buffer_start = start
                buffer_end = end
                if start.minute != 30 or start.minute != 0:
                    if start.minute > 30:
                        start -= timedelta(minutes=start.minute - 30)
                    if start.minute < 30:
                        start -= timedelta(minutes=start.minute)
                if end.minute != 30 or end.minute != 0:
                    if end.minute > 30:
                        end += timedelta(minutes=end.minute - 30)
                    if end.minute < 30:
                        end += timedelta(minutes=30 - end.minute)

                recordings = []
                delta = timedelta(minutes=30)
                extra_start = start
                while extra_start != end:
                    rec = Recording.get(json['room'], extra_start.strftime('%Y-%m-%d'), extra_start.strftime('%H:%M'))
                    print(rec)
                    if rec is None:
                        return "Video not found", 404
                    recordings.append(rec.json)
                    extra_start += delta

                start_difference = buffer_start - start
                end_difference = end - buffer_end
                json_recall.apply_async(args=('recordings', recordings, isoparse(json['start_time']), json['room'],start_difference, end_difference),
                                        queue='4', priority=1)
                # json_recall('recordings', recordings, isoparse(json['start_time']), json['room'],start_difference, end_difference)
                # array, fps = connect_jsons('recordings', recordings, one_array=True)
                # video = vid_from_array(str(uuid.uuid4()) + '.mp4', array, fps, headcount=True)
                # print('sending file to NVR')

                # API.upload_video_nvr(video, start.isoformat(), request.json['room'], name_on_folder='emotions')
                return "File will be sent soon", 200
            else:
                return "Bad request", 400
    return "Access denied", 500


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/build/<file>')
def build(file):
    return send_from_directory('build', file)


@app.route('/build/src/<file>')
def src(file):
    return send_from_directory('build/src', file)


@app.route('/build/public/<file>')
def pub(file):
    return send_from_directory('build/public', file)

# @celery.task(name='stream.json_recall')
# def json_recall(in_dir, recordings, time, room):
#     array, fps = connect_jsons(in_dir, recordings, one_array=True)
#     video = vid_from_array(str(uuid.uuid4()) + '.mp4', array, fps, headcount=True)
#     print('sending file to NVR')
#     API.upload_video_nvr(video, time.isoformat(), room, name_on_folder='emotions')
#
#
# @celery.task(name='stream.stream_background')
# def stream_background():
#     while True:
#         stream('2020-02-06', '9:30', '16:00')


api.add_resource(Config, '/config',
                 '/config/<int:id_>',

                 '/config/<float:confidence_threshold>/<float:top_k>/<float:nms_threshold>/' +
                 '<float:keep_top_k>/<float:vis_thres>/<string:network>/<float:distance_threshold>/' +
                 '<float:samples>/<float:eps>/<float:fps_factor>')
api.add_resource(Record, '/record',
                 '/record/<string:room_num>/<string:date>/<string:time>')
if __name__ == "__main__":
    if not os.path.isdir('video_output'):
        os.mkdir('video_output')
    if not os.path.isdir('queue'):
        os.mkdir('queue')
    if not os.path.isdir('recordings'):
        os.mkdir('recordings')

    try:
        init_db_command()
        pass
    except sqlite3.OperationalError:
        # Assume it's already been created
        pass
    # stream_background.apply_async(queue='2', priority=1)
    app.run(host='127.0.0.1')
    # flower celery (пишем в терминале1)
    # celery purge
    #  celery worker -A stream.celery --loglevel=info -n 0 -Q 0 -P eventlet --detach
    #  celery worker -A stream.celery --loglevel=info -n 1 -Q 1 -P eventlet --detach
    #  celery worker -A stream.celery --loglevel=info -n 2 -Q 2 -P eventlet --detach
    #  celery worker -A stream.celery --loglevel=info -n 3 -Q 3 -P eventlet --detach
    #  celery worker -A stream.celery --loglevel=info -n 4 -Q 4 -P eventlet --detach
    #  celery worker -A stream.celery --loglevel=info -n 5 -Q 5 -P eventlet --detach
    #  celery worker -A stream.celery --loglevel=info -n 6 -Q 6 -P eventlet --detach
    #  celery worker -A stream.celery --loglevel=info -n 7 -Q 7 -P eventlet --detach
    #  celery -A Rest_api.celery worker --loglevel=info -n 0 -Q 0 -P eventlet
    #  celery -A Rest_api.celery worker --loglevel=info -n 1 -Q 1 -P eventlet
