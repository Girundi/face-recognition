from flask import Flask, request
from flask_restful import Api, Resource
from bson import dumps
from datetime import datetime, timedelta
import configparser
from user import Recording, Api_key
from rofl import vid_from_array, connect_jsons
import uuid
from api import upload_video_nvr
import os
import sqlite3
from db import init_db_command, init_db
from dateutil.parser import isoparse
from celery import Celery

app = Flask(__name__)
api = Api(app)
app.config.update(BEDUG=True, TESTING=True,
                  ALLOWED_EXTENSIONS=['mp4'], LOGFILE='app.log',
                  UPLOAD_FOLDER='queue', RESULT_FOLDER='video_output',
                  CELERY_BROKER_URL='redis://localhost:6379',
                  CELERY_RESULT_BACKEND='redis://localhost:6379')

celery = Celery(app.name)
celery.config_from_object('celeryconfig')

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

    def get(self, room_num, date, time):
        try:
            # date = datetime.datetime.strptime(date, '%Y-%m-%d')
            # time = datetime.datetime.strptime(time, '%H:%M')
            rec = Recording.get(room_num, date, time)
            print(rec)
            if rec is None:
                return "Video not found", 404
            rec = rec.json
            return rec, 200
        except:
            return "Server error", 500


@app.route("/api", methods=['PUT'])
def api_():
    if 'key' in request.headers:
        keys = list(Api_key.get_dataframe()['uuid'])
        if request.headers['key'] in keys:
            json = request.json
            if 'room' in json and 'start_time' in json and 'end_time' in json:
                print(json)
                start = isoparse(json['start_time'])
                end = isoparse(json['end_time'])
                if start.strftime('%Y-%m-%d') != end.strftime('%Y-%m-%d') or \
                        not (start.strftime('%M') == '00' or start.strftime('%M') == '30') or \
                        not (end.strftime('%M') == '00' or end.strftime('%M') == '30'):
                    return "Bad request", 400
                recordings = []
                delta = timedelta(minutes=30)
                while start != end + delta:
                    rec = Recording.get(json['room'], start.strftime('%Y-%m-%d'), start.strftime('%H:%M'))
                    print(rec)
                    if rec is None:
                        return "Video not found", 404
                    recordings.append(rec.json)
                    start += delta

                json_recall.apply_async(args=('recordings', recordings, isoparse(json['start_time']), json['room'], ),
                                        queue='high', priority=1)
                # array, fps = connect_jsons('recordings', recordings, one_array=True)
                # video = vid_from_array(str(uuid.uuid4()) + '.mp4', array, fps, headcount=True)
                # print('sending file to NVR')

                # upload_video_nvr(video, start.isoformat(), request.json['room'], name_on_folder='emotions')
                return "File will be sent soon", 200
            else:
                return "Bad request", 400
    return "Access denied", 500


@celery.task(name='Rest_api.json_recall')
def json_recall(in_dir, recordings, time, room):
    array, fps = connect_jsons(in_dir, recordings, one_array=True)
    video = vid_from_array(str(uuid.uuid4()) + '.mp4', array, fps, headcount=True)
    print('sending file to NVR')
    upload_video_nvr(video, time.isoformat(), room, name_on_folder='emotions')


api.add_resource(Config, '/config',
                 '/config/<int:id_>',

                 '/config/<float:confidence_threshold>/<float:top_k>/<float:nms_threshold>/' +
                 '<float:keep_top_k>/<float:vis_thres>/<string:network>/<float:distance_threshold>/' +
                 '<float:samples>/<float:eps>/<float:fps_factor>')
api.add_resource(Record, '/record/<string:room_num>/<string:date>/<string:time>')
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

    app.run(debug=True)
    # flower celery (пишем в терминале1)
    # celery purge
    # celery -A Rest_api.celery worker --loglevel=info -n high -Q high -P eventlet
