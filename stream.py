from time import sleep
from datetime import datetime, date, timedelta
import api
import os
from rofl import ROFL, vid_from_array, connect_jsons
from celery import Celery
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import configparser
from user import Recording
import argparse
import uuid
from dateutil.parser import isoparse
import video_maker

celery = Celery(__name__)
celery.config_from_object('celeryconfig')

rofl_folder = "14Xsw4xk6vUFINsyy1OH5937Rq98W4JHw"

api.credentials = service_account.Credentials.from_service_account_file(api.SERVICE_ACCOUNT_FILE, scopes=api.SCOPES)
api.service = build('drive', 'v3', credentials=api.credentials)
# with open('Emotions_Project-481579272f6a.json', 'r') as j:
#     api.data = json.load(j)
# api.build_service()
GOOGLE_CLIENT_ID = api.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = api.GOOGLE_CLIENT_SECRET
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    rofl = ROFL("trained_knn_model.clf", retina=True, on_gpu=True, emotions=True,
         confidence_threshold=float(config['ACTIVE']['confidence_threshold']),
         top_k=int(config['ACTIVE']['top_k']),
         nms_threshold=float(config['ACTIVE']['nms_threshold']),
         keep_top_k=int(config['ACTIVE']['keep_top_k']),
         vis_thres=float(config['ACTIVE']['vis_thres']),
         network=config['ACTIVE']['network'],
         distance_threshold=float(config['ACTIVE']['distance_threshold']),
         samples=int(config['ACTIVE']['samples']),
         eps=float(config['ACTIVE']['eps']))
    return rofl, int(config['ACTIVE']['fps_factor'])


def send_file(filename, link=''):
    r = api.upload_video("video_output/" + filename, filename.split('/')[-1], folder_id=rofl_folder)
    _id = r['id']
    """Show result endpoint."""
    return "https://drive.google.com/file/d/" + _id + "/" + link


@celery.task(name='stream.processing_nvr_', time_limit=14000)  # name='stream.processing_nvr_'
def processing_nvr_(data, filename=None, email=None):
    """Celery function for the image processing."""

    room = data['room']
    date = data['date']
    time = data['time']
    try:
        filename, parent_folder = api.download_video_nvr(room, date, time, need_folder=True)
    except:
        msg = f'Searching file in NVR archive something went wrong'
        return msg

    i = 30
    while not os.path.isfile(filename):
        sleep(5)
        i -= 1
        if i == 0:
            return 'Problem creating file ' + filename

    sleep(60)

    if filename is not None:
        rofl, fps_factor = load_config()
        print(filename)
        print("queue/" + filename.split('/')[1])
        # json_filename = rofl.json_run("queue", filename.split('/')[1], emotions=data['em'],
        #                recognize=data['recog'], remember=data['remember'],
        #                fps_factor=fps_factor)
        json_filename = rofl.streamline_run('queue', filename.split('/')[1], fps_factor, emotions=data['em'],
                                            recognize=data['recog'], remember=['remember'])

        print(json_filename)

        sleep(60)
        i = 30
        while not os.path.isfile(json_filename):
            sleep(5)
            i -= 1
            if i == 0:
                return 'Problem creating file ' + json_filename

        Recording.create(filename, room, date, time, json_filename)
        vid_link = send_file(json_filename, link='view')

        dt = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')
        dt = dt.isoformat()

        # api.upload_video_nvr('filename', dt, room, parent_folder)

        # if email is not None:
        #     api.send_file_with_email(email, "Processed video",
        #                              "Thank you, that's your processed video\nHere is your video:\n" + vid_link)
        os.remove(filename)
        print(filename + ' was successfully analysed and result is saved in ' + json_filename)
        return json_filename
    return None


def stream_timing(date_begin, time_begin, time_end, n=4):
    data = {}
    data['room'] = '504'
    data['em'] = True
    data['recog'] = False
    data['remember'] = False
    date_end = date_begin
    p = {}
    m = 60
    h = 3600
    while date_begin <= date_end:
        data['date'] = date_begin.strftime('%Y-%m-%d')
        # time_begin = datetime(1, 1, 1, 9, 30)
        while time_begin <= time_end:
            for i in range(n):
                data['time'] = time_begin.strftime('%H:%M')
                print(data)
                p[str(i)] = processing_nvr_.apply_async(args=[data], queue=str(i), priority=i)
                sleep(5)
                time_begin += timedelta(minutes=30)
            flag = False
            while not flag:
                flag = True
                for i in range(n):
                    if p[str(i)].status == 'SUCCESS' or p[str(i)].status == 'FAILURE':
                        flag = False
                        break
                # sleep(5 * m)
        while date_begin == date_end:
            sleep(18 * h)
            date_end = datetime.now().date()
        date_begin += timedelta(days=1)


def stream(date_begin, time_begin, time_end, n=4):
    data = {}
    data['room'] = '504'
    data['em'] = True
    data['recog'] = False
    data['remember'] = False
    date_end = date_begin
    p = {}
    m = 60
    h = 3600
    data['date'] = date_begin.strftime('%Y-%m-%d')

    for i in range(n):
        data['time'] = time_begin.strftime('%H:%M')
        print(data)
        p[str(i)] = processing_nvr_.apply_async(args=[data], queue=str(i), priority=i)
        sleep(5)
        time_begin += timedelta(minutes=30)

    while time_begin <= time_end:
        for i in range(n):
            if p[str(i)].status == 'SUCCESS' or p[str(i)].status == 'FAILURE':
                data['time'] = time_begin.strftime('%H:%M')
                print(data)
                p[str(i)] = processing_nvr_.apply_async(args=[data], queue=str(i), priority=i)
                sleep(5)
                time_begin += timedelta(minutes=30)
                if time_begin == time_end:
                    break
            if time_begin == time_end:
                break


@celery.task(name='stream.json_recall')
def json_recall(in_dir, recordings, time, room, start_dif=0, end_dif=0):
    array, fps = connect_jsons(in_dir, recordings, one_array=True)
    if start_dif != 0:
        amount = int(start_dif.seconds * fps)
        array = array[amount:].copy()
    if end_dif != 0:
        amount = -int(end_dif.seconds * fps)
        array = array[:amount].copy()

    video = vid_from_array(str(uuid.uuid4()) + '.mp4', array, fps, headcount=True)
    print('sending file to NVR')
    api.upload_video_nvr(video, time, room, name_on_folder='emotions_last')


@celery.task(name='stream.stream_background')
def stream_background(time='2020-02-06'):
    date_begin = isoparse(time)
    while True:
        time_begin = datetime.strptime('09:30', '%H:%M')
        time_end = datetime.strptime('16:00', '%H:%M')
        if date_begin == datetime.now().date():
            sleep(18 * 3600)
        stream(date_begin, time_begin, time_end, n=2)
        date_begin = date_begin + timedelta(days=1)


# @celery.task(name='stream.stream_erudite')
def stream_erudite(room, n=4):
    while True:
        now = datetime.now()
        if now.hour == 22:
            fromdate = datetime(year=now.year, month=now.month, day=now.day, hour=9, minute=30)
            todate = datetime(year=now.year, month=now.month, day=now.day, hour=21, minute=30)
            lessons = api.get_lessons_erudite(fromdate, todate, room)
            for lesson in lessons:
                start = datetime.strptime(lesson['start_time'], '%H:%M')
                end = datetime.strptime(lesson['end_time'], '%H:%M')
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
                delta = timedelta(minutes=30)
                while start != end:
                    data = {}
                    data['room'] = str(room)
                    data['em'] = True
                    data['recog'] = False
                    data['remember'] = False
                    data['date'] = fromdate.strftime('%Y-%m-%d')
                    data['time'] = start.strftime('%H:%M')
                    processing_nvr_(data)
                    start += delta


@celery.task(name='stream.processing_lesson')
def processing_lesson(lesson):
    start = datetime.strptime(lesson['start_time'], '%H:%M')
    end = datetime.strptime(lesson['end_time'], '%H:%M')
    lesson_start = start
    lesson_end = end
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

    delta = timedelta(minutes=30)
    recordings = []
    extra_start = start
    lesson_datetime = datetime.strptime(lesson['date'] + ' ' + lesson['start_time'], '%Y-%m-%d %H:%M')

    while extra_start != end:
        data = {}
        data['room'] = str(lesson['ruz_auditorium'])
        data['em'] = True
        data['recog'] = False
        data['remember'] = False
        data['date'] = lesson['date']
        data['time'] = extra_start.strftime('%H:%M')
        file = processing_nvr_(data)
        recordings.append(file)
        extra_start += delta
    if len(recordings) == 3:
        start_difference = lesson_start - start
        end_difference = lesson_end - end
        array, fps = connect_jsons('recordings', recordings, one_array=True)
        if start_difference != 0:
            amount = int(start_difference.seconds * fps)
            array = array[amount:].copy()
        if end_difference != 0:
            amount = int(end_difference.seconds * fps)
            array = array[:amount].copy()

        video = video_maker.optimized_render('video_output', uuid.uuid4(), array, fps, headcount=True)
        res, file_id = api.upload_video_nvr(video, lesson_datetime.isoformat(), lesson['ruz_auditorium'],
                                            name_on_folder='emotions ' + lesson['cource_code'])
        lesson_recordings = api.get_recordings_erudite(lesson_start, lesson_end, lesson['ruz_auditorium'])

        emotion_video_url = api.get_url_by_id_erudite(file_id)
        for rec in lesson_recordings:
            api.update_url_erudite(rec['id'], emotion_video_url)
        return lesson['course_code'] + ' ' + lesson_datetime.isoformat() + ' was processed'


def stream_optimized(rooms, n=4):
    while True:
        now = datetime.now()
        lessons = []
        for room in rooms:
            if now.hour == 22:
                fromdate = datetime(year=now.year, month=now.month, day=now.day, hour=9, minute=30)
                todate = datetime(year=now.year, month=now.month, day=now.day, hour=21, minute=30)
                # if len(api.get_recordings_erudite(fromdate, todate, room)):
                lessons += api.get_lessons_erudite(fromdate, todate, room)

        p = {}
        for i in range(n):
            p[str(i)] = processing_lesson.apply_async(args=[lesson], queue=str(i), priority=i)
            sleep(5)
        j = n
        while j < len(lesson):
            if p[str(i)].status == 'SUCCESS' or p[str(i)].status == 'FAILURE':
                for i in range(n):
                    p[str(i)] = processing_lesson.apply_async(args=[lessons[j]], queue=str(i), priority=i)
                    j += 1
                    sleep(5)


        # i = 0
        # while i != len(lessons):
        #     t = datetime.strptime(lesson['start_time'], '%H:%M')
        #     lesson_time = datetime(year=now.year, month=now.month, day=now.day, hour=t.hour, minute=t.minute)
        #     for i in range(1, 4):
        #         if not len(api.get_recordings_erudite(lesson_time, lesson_time+i*delta, lesson['ruz_auditorium'])):
        #             print("Haven't found recording(s) for " + lesson_time.isoformat() + " " + lesson['ruz_auditorium'])
        #             lessons.pop(i)
        #             break
        #     i += 1




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-w', action='store', dest="workers", default=4, type=int)
    parser.add_argument('-d', action='store', dest='start_date', default='2020-02-06', type=str)
    parser.add_argument('-s', action='store', dest='start_time', default='09:30', type=str)
    parser.add_argument('-e', action='store', dest='end_time', default='16:00', type=str)
    args = parser.parse_args()
    date_begin = isoparse(args.start_date)


    # date_begin = date(2020, 2, 6)
    # time_begin = datetime(1, 1, 1, 9, 30)  # время 9:30
    # time_begin = datetime(1, 1, 1, int(args.start_time.split(':')[0]), int(args.start_time.split(':')[1]))
    time_begin = datetime.strptime(args.start_time, '%H:%M')
    # time_end = datetime(1, 1, 1, int(args.end_time.split(':')[0]), int(args.end_time.split(':')[1]))  # время 16:00
    time_end = datetime.strptime(args.end_time, '%H:%M')
    workers = args.workers  # сюда писать количество воркеров
    delta = timedelta(days=1)

    data = {}
    data['room'] = '504'
    data['em'] = True
    data['recog'] = False
    data['remember'] = False
    data['date'] = date_begin.strftime('%Y-%m-%d')
    data['time'] = time_begin.strftime('%H:%M')
    # processing_nvr_(data)
    while True:
        stream(date_begin, time_begin, time_end, workers)
        date_begin += delta

    #  celery purge
    #  celery worker -A stream.celery --loglevel=info -n 0 -Q 0 -P eventlet &
    #  celery worker -A stream.celery --loglevel=info -n 1 -Q 1 -P eventlet &
    #  celery worker -A stream.celery --loglevel=info -n 2 -Q 2 -P eventlet &
    #  celery worker -A stream.celery --loglevel=info -n 3 -Q 3 -P eventlet &
    #  celery worker -A stream.celery --loglevel=info -n 4 -Q 4 -P eventlet &
    #  celery worker -A stream.celery --loglevel=info -n 5 -Q 5 -P eventlet
    #  celery worker -A stream.celery --loglevel=info -n 6 -Q 6 -P eventlet
    #  celery worker -A stream.celery --loglevel=info -n 7 -Q 7 -P eventlet
    #  celery -A Rest_api.celery worker --loglevel=info -n 0 -Q 0 -P eventlet
    #  celery -A Rest_api.celery worker --loglevel=info -n 1 -Q 1 -P eventlet
