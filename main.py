from rofl import ROFL
from recognizer import Recognizer
from encode import encode_cluster_sf, encode_cls
# import api
import pickle
import os
# from google.oauth2 import service_account
# from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
# from googleapiclient.discovery import build
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
# # api.build_service()
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

date = '2020-10-09'
time = '10:00'
dt = datetime.datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')
# dt = dt.isoformat()
dt2 = dt + datetime.timedelta(minutes=30)
dt2 = dt2.isoformat()
header = {'key': '5652ef4d-44f8-457c-be55-2a56dc715996'}
data = {'start_time': dt.isoformat(),
        'end_time': dt2,
        'room': '504'}
requests.put('http://127.0.0.1:5000/api', headers=header, json=data)

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
