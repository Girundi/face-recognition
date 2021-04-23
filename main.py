from rofl import ROFL, connect_jsons, vid_from_array
from recognizer import Recognizer
from encode import encode_cluster_sf, encode_cls
import api
import pickle
import os
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.discovery import build
import io
import pickle
import requests
import os
import os.path
import platform
import mimetypes
import base64
from apiclient import errors
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import pprint as pp
import json
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import stream
import user
import sqlite3
import pandas as pd
import configparser
import numpy as np
import requests
import time
import uuid
import video_maker

# print(os.path.isdir('video_output'))
model = "trained_knn_model.clf"
# recog = Recognizer()
# recog.train(n_neighbors=2, model_save_path=model)
# file = api.download_video_nvr('504','2020-09-30', '09:30')
# file = '2020-10-07_12_30_305_54_Trim.mp4'
# rofl = ROFL(recognizer_path=model, retina=True, on_gpu=True, emotions=True)
# filename = "jackle.mp4"
# filename1 = "twice.mp4"
# file = '2020-10-09_10-00_504_26.mp4'
# api.credentials = service_account.Credentials.from_service_account_file(api.SERVICE_ACCOUNT_FILE, scopes=api.SCOPES)
# api.service = build('drive', 'v3', credentials=api.credentials)
# with open('Emotions_Project-481579272f6a.json', 'r') as j:
#     api.data = json.load(j)
# api.build_service()
# GOOGLE_CLIENT_ID = api.GOOGLE_CLIENT_ID
# GOOGLE_CLIENT_SECRET = api.GOOGLE_CLIENT_SECRET
# GOOGLE_DISCOVERY_URL = (
#     "https://accounts.google.com/.well-known/openid-configuration"
# )
# data = {}
# data['room'] = '504'
# data['em'] = True
# data['recog'] = False
# data['remember'] = False
# data['date'] = '2020-10-09'
# data['time'] = '10:00'
# stream.processing_nvr_(data)

# file, folder = api.download_video_nvr('504', '2020-10-09', '10:00', need_folder=True)
# print(folder)
# date = '2020-10-09'
# time = '10:00'
# dt = datetime.datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')
# dt = dt.isoformat()
# print(dt)
# file = file.split('/')[1]


# file = '2020-09-30_09_30_504_27_Trim.mp4'
# file = 'twice.mp4'
# rofl.json_run('./queue', file, fps_factor=30, emotions=True, recognize=False)
# rofl.basic_run('./queue', file, fps_factor=30, emotions=True, recognize=True)

# u = user.User.get()
# db = sqlite3.connect('sqlite_db')
# table = pd.read_sql_query("SELECT * from recording", db)
# table = table.to_dict()
# print(table)

# rec = user.Recording.get('504', '2020-10-09', '9:30')
# print(rec)

# print(stream.load_config())
# config = configparser.ConfigParser()
# config.read('config.ini')
# list = {'confidence_threshold': config['ACTIVE']['confidence_threshold'],
#                         'top_k': config['ACTIVE']['top_k'],
#                         'nms_threshold': config['ACTIVE']['nms_threshold'],
#                         'keep_top_k': config['ACTIVE']['keep_top_k'],
#                         'vis_thres': config['ACTIVE']['vis_thres'],
#                         'network': config['ACTIVE']['network'],
#                         'distance_threshold': config['ACTIVE']['distance_threshold'],
#                         'samples': config['ACTIVE']['samples'],
#                         'eps': config['ACTIVE']['eps'],
#                         'fps_factor': config['ACTIVE']['fps_factor']
#                         }
# print(list)

# def load_config():
#     config = configparser.ConfigParser()
#     config.read('config.ini')
#     rofl = ROFL("trained_knn_model.clf", retina=True, on_gpu=False,
#          confidence_threshold=float(config['ACTIVE']['confidence_threshold']),
#          top_k=int(config['ACTIVE']['top_k']),
#          nms_threshold=float(config['ACTIVE']['nms_threshold']),
#          keep_top_k=int(config['ACTIVE']['keep_top_k']),
#          vis_thres=float(config['ACTIVE']['vis_thres']),
#          network=config['ACTIVE']['network'],
#          distance_threshold=float(config['ACTIVE']['distance_threshold']),
#          samples=int(config['ACTIVE']['samples']),
#          eps=float(config['ACTIVE']['eps']))
#     return rofl, int(config['ACTIVE']['fps_factor'])
#
# rofl, fps_factor = load_config()
# print(fps_factor)
# rofl.vid_from_json('recordings', 'twice.json', headcount=True)

# with open('recordings/twice.json', "r") as f:
#     data = json.load(f)
#
# array = data["frames"]
#
# new = np.repeat(array, 2).tolist()
# print(new)
# rofl.json_run('./queue', '2020-10-09_09_30_504_26.mp4', fps_factor=30, emotions=True)
# rofl.json_run('./queue', '2020-10-09_10-00_504_26.mp4', fps_factor=30, emotions=True)
# rofl.json_run('./queue', '2020-10-09_10_30_504_26.mp4', fps_factor=30, emotions=True)

# files = ['2020-10-09_09_30_504_26.json', '2020-10-09_10-00_504_26.json', '2020-10-09_10_30_504_26.json']
# frames, fps = rofl.connect_jsons('recordings', files, one_array=True)
# rofl.vid_from_array('new_vid_2.mp4', frames, fps, headcount=True)

# date = '2020-10-09'
# time = '10:01'
# dt = datetime.datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')
# # dt = dt.isoformat()
# dt2 = dt + datetime.timedelta(minutes=25)
# dt2 = dt2.isoformat()
# header = {'key': '5652ef4d-44f8-457c-be55-2a56dc715996'}
# data = {'start_time': dt.isoformat(),
#         'end_time': dt2,
#         'room': '504'}
# r = requests.put('http://127.0.0.1:5000/api/plot', headers=header, json=data)
# print(r)

# file = rofl.streamline_run('queue', '2020-02-06_09-30_504_26.mp4', 600, emotions=True)
# print(file)

# r = requests.get('http://facerecog.miem.tv/config')
# print(r)

# filename, parent_folder = api.download_video_nvr('504', '2020-02-06', '09:30', need_folder=True)

# with open('recordings/2020-10-09_10_30_504.json', 'r') as f:
#     data = json.load(f)
# frames = data["frames"]
# l = len(frames)
# print(l)
# i = 0
# while l // 3 <= len(frames):
#     if i % 3 == 0:
#         frames.pop(i)
#     else:
#         i += 1
# print(len(frames))
# data["fps"] = data["fps"] / 3
# data["frames"] = frames
# f.close()
# with open('recordings/2020-10-09_10_30_504_26.json', 'w') as f:
#     json.dump(data, f)


# r = api.upload_video_nvr("video_output/2020-10-09_10-00_504_26.mp4", dt, '504', 'МИЭМ-504')
# r = api.upload_video_nvr("video_output/2020-10-09_10-00_504_26.mp4", dt, "504")
# print(r)

# # rofl.basic_run("./queue", "twice.mp4", fps_factor=30, recognize=True, emotions=True)
# # rofl.run_emotions(".", filename1, fps_factor=30)
# # rofl.basic_run(".", filename, fps_factor=30)
# # rofl.run_and_remember_strangers(filename, fps_factor=30)
#
# # encode_cluster_sf("./strangers", "./test.pickle")
# # rofl.clust.remember_strangers("enc_cluster.pickle", save_path="known_faces")
#
# # with open('known_faces/enc_cls.pickle', 'rb') as f:
# #     print(pickle.load(f))
# encode_cls('known_faces', 'known_faces/enc_cls.pickle')
# rofl.recog.train(model_save_path=model, n_neighbors=2)
# rofl.basic_run('./queue', file, fps_factor=30, recognize=True)
# tic = time.time()
# array, fps = connect_jsons('recordings', ['recordings/2020-10-09_09_30_504.json',
#                                           'recordings/2020-10-09_10-00_504_26.json',
#                                           'recordings/2020-10-09_10_30_504.json'],
#                            one_array=True)
# # vid_from_array('test4.mp4', array, fps, headcount=True)
# video_maker.optimized_render('video_output', 'test7.mp4', array, fps, headcount=True)
# print(time.time() - tic)

# tic = time.time()
# rofl.streamline_run('queue', '2020-02-06_09-30_504_26.mp4', 30, emotions=True)
# print(time.time() - tic)

lesson = api.get_lessons_erudite(datetime.datetime(2021, 4, 20, hour=11, minute=00),
                                 datetime.datetime(2021, 4, 20, hour=12, minute=30), 305)[0]
lesson_datetime = datetime.datetime.strptime(lesson['date'] + ' ' + lesson['start_time'], '%Y-%m-%d %H:%M')

lesson_start = datetime.datetime.strptime(lesson['start_time'] + ' ' + lesson['date'], '%H:%M %Y-%m-%d')
lesson_end = datetime.datetime.strptime(lesson['end_time'] + ' ' + lesson['date'], '%H:%M %Y-%m-%d')
# start = datetime.datetime(2021, 4, 13, hour=11, minute=0)
# end = datetime.datetime(2021, 4, 13, hour=12, minute=30)
#
# start_difference = lesson_start - start
# end_difference = lesson_end - end
# recordings = ['recordings/2021-04-13_11-00_305_54.json', 'recordings/2021-04-13_11-30_305_54.json',
#               'recordings/2021-04-13_12-00_305_54.json']
# array, fps = connect_jsons('recordings', recordings, one_array=True)
# if start_difference.seconds != 0:
#     amount = int(start_difference.seconds * fps)
#     array = array[amount:].copy()
# if end_difference.seconds != 0:
#     amount = -int(end_difference.seconds * fps)
#     array = array[:amount].copy()
#
# video = video_maker.optimized_render('video_output', str(uuid.uuid4()) + '.mp4', array, fps, headcount=True)
# video = 'video_output/0709b81c-482f-4d54-99c2-18770f3abb45.mp4'
# res, file_id = api.upload_video_nvr(video, lesson_datetime.isoformat(), lesson['ruz_auditorium'],
#                                     name_on_folder='emotions ' + lesson['course_code'])
# lesson_recordings = api.get_recordings_erudite(lesson_start, lesson_end, lesson['ruz_auditorium'])
# nvr_key = {"key": "99a1dfb5342546319e3d5f4de7150f05"}
# # data = {
# #     'url': 'https://drive.google.com/drive/u/1/folders/1IGlRJiv1CzNCzFw7j0NOD0mzFM0x3o7k/preview'
# # }
# # res = requests.get("https://nvr.miem.hse.ru/api/erudite/records?url=%27https%3A%2F%2Fdrive.google.com%2Fdrive%2Fu%2F1%2Ffolders%2F1IGlRJiv1CzNCzFw7j0NOD0mzFM0x3o7k%2Fpreview%27&page_number=0&with_keywords_only=false&ignore_autorec=false", headers=nvr_key)
# # records = api.get_recordings_erudite()
# # res = json.loads(res.text)[0]
# # emotion_video_url = api.get_url_by_id_erudite(res['id'])
# emotion_video_url = 'https://drive.google.com/file/d/1K5TDMVvOTX4R-SPl94NczMai9cpwHwl4/preview'
# for rec in lesson_recordings:
#     data = {
#         'emotions_url': 'https://drive.google.com/file/d/1Qfc2VOYhdR090aScYt92ZGZ0bb_lAiOq/preview'
#     }
#     api.update_url_erudite(rec['id'], data)
# day = datetime.datetime(2021, 4, 20)
# rooms = ['305']
# stream.stream_one_day(day, rooms)
# list_of_rec = ['recordings/2021-04-20_11-00_305_54.json', 'recordings/2021-04-20_11-30_305_54.json',
#                'recordings/2021-04-20_12-00_305_54.json']
# array = connect_jsons('recordings', list_of_rec, one_array=True)
# print(array[0])
# print(type(array[0]))
# stream.processing_lesson(lesson)


video = 'video_output/c312b219-40d5-46f7-8a4e-1e731242c829.mp4'
# res, file_id = api.upload_video_nvr(video, lesson_datetime.isoformat(), lesson['ruz_auditorium'],
#                                     name_on_folder='emotions ' + lesson['course_code'])
lesson_recordings = api.get_recordings_erudite(lesson_start, lesson_end, lesson['ruz_auditorium'])
# for rec in lesson_recordings:
#     data = {
#         'emotions_url': res['file_url']
#     }
#     api.update_url_erudite(rec['id'], data)
print(lesson_recordings)