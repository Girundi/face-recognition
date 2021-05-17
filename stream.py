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
from google_drive_downloader import GoogleDriveDownloader as gdd
import subprocess

celery = Celery(__name__)
celery.config_from_object('celeryconfig')
# celery.control.purge()
rofl_folder = "14Xsw4xk6vUFINsyy1OH5937Rq98W4JHw"

api.credentials = service_account.Credentials.from_service_account_file(api.SERVICE_ACCOUNT_FILE, scopes=api.SCOPES)
api.service = build('drive', 'v3', credentials=api.credentials)
with open('Emotions_Project-481579272f6a.json', 'r') as j:
    api.data = json.load(j)
api.build_service()
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
    r = api.upload_video(filename, filename, folder_id=rofl_folder)
    _id = r['id']
    """Show result endpoint."""
    return "https://drive.google.com/file/d/" + _id + "/" + link


@celery.task(name='stream.processing_nvr_', time_limit=14000)  # name='stream.processing_nvr_'
def processing_nvr_(data, filename=None, email=None):
    """Celery function for the image processing."""

    room = data['room']
    date = data['date']
    time = data['time']
    filename = 'queue/' + str(uuid.uuid4()) + '.mp4'
    try:
        gdd.download_file_from_google_drive(file_id=data['link'].split('/')[-2],
                                            dest_path=filename,
                                            unzip=True)
        sleep(35)
    except:

        try:
            filename, parent_folder = api.download_video_nvr(room, date, time, need_folder=True)
            sleep(35)
        except:
            msg = f'Searching file in NVR archive something went wrong'
            return None

    i = 30
    while not os.path.isfile(filename):
        sleep(5)
        i -= 1
        if i == 0:
            return None

    sleep(60)

    if filename is not None:
        rofl, fps_factor = load_config()
        print(filename)
        print("queue/" + filename.split('/')[1])
        # json_filename = rofl.json_run("queue", filename.split('/')[1], emotions=data['em'],
        #                recognize=data['recog'], remember=data['remember'],
        #                fps_factor=fps_factor)
        json_filename = rofl.streamline_run('queue', filename.split('/')[1], fps_factor, emotions=data['em'],
                                            recognize=data['recog'], remember=data['remember'])

        print(json_filename)

        sleep(60)
        i = 30
        while not os.path.isfile(json_filename):
            sleep(5)
            i -= 1
            if i == 0:
                return None
        with open('recordings/2021-04-13_11-00_305_54.json', "r") as f:
            json_data = json.load(f)
        json_data = json.dumps(data)

        Recording.create(filename, room, date, time, json_data)
        # vid_link = send_file(json_filename, link='view')

        dt = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')
        dt = dt.isoformat()

        resp, file_id = api.upload_video_nvr('filename', dt, room, 'emotions ' + dt)


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
    array, fps = connect_jsons(recordings, one_array=True)
    if start_dif.seconds != 0:
        amount = int(start_dif.seconds * fps)
        array = array[amount:].copy()
    if end_dif.seconds != 0:
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
    start = datetime.strptime(lesson['start_time'] + ' ' + lesson['date'], '%H:%M %Y-%m-%d')
    end = datetime.strptime(lesson['end_time'] + ' ' + lesson['date'], '%H:%M %Y-%m-%d')
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
        if file is not None:
            recordings.append(file)
        extra_start += delta
    if len(recordings) == 3:
        start_difference = lesson_start - start
        end_difference = end - lesson_end
        array, fps = connect_jsons(recordings, one_array=True)
        if start_difference.seconds != 0:
            amount = int(start_difference.seconds * fps)
            array = array[amount:].copy()
        if end_difference.seconds != 0:
            amount = -int(end_difference.seconds * fps)
            array = array[:amount].copy()

        video = video_maker.optimized_render('video_output', str(uuid.uuid4()) + '.mp4', array, fps, [], headcount=True)
        res, file_id = api.upload_video_nvr(video, lesson_datetime.isoformat(), lesson['ruz_auditorium'],
                                            name_on_folder='emotions ' + lesson['course_code'])
        lesson_recordings = api.get_recordings_erudite(lesson_start, lesson_end, lesson['ruz_auditorium'])

        # emotion_video_url = api.get_url_by_id_erudite(file_id)

        for rec in lesson_recordings:
            data = {
                'emotions_url': res['file_url']
            }
            api.update_url_erudite(rec['id'], data)
        return lesson['course_code'] + ' ' + lesson_datetime.isoformat() + ' was processed'
    print('Something went wrong')
    return 'Something went wrong'


def stream_optimized(rooms, n=2):
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
                load = min(n, len(lessons))
                for i in range(load):
                    p[str(i)] = processing_lesson.apply_async(args=[lessons[i]], queue=str(i), priority=i)
                    sleep(5)
                j = load
                while j < len(lessons):
                    for i in range(load):
                        if p[str(i)].status == 'SUCCESS' or p[str(i)].status == 'FAILURE':
                            p[str(i)] = processing_lesson.apply_async(args=[lessons[j]], queue=str(i), priority=i)
                            j += 1
                            if j >= len(lessons):
                                break
                            sleep(5)
                    if j >= len(lessons):
                        break

            else:
                sleep(10*60)


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


def stream_one_day(date, rooms, n=2):
    now = date
    lessons = []
    for room in rooms:
        # if now.hour == 22:
        fromdate = datetime(year=now.year, month=now.month, day=now.day, hour=9, minute=30)
        todate = datetime(year=now.year, month=now.month, day=now.day, hour=21, minute=30)
        # if len(api.get_recordings_erudite(fromdate, todate, room)):
        lessons += api.get_lessons_erudite(fromdate, todate, room)

    p = {}
    load = min(n, len(lessons))
    for i in range(load):
        p[str(i)] = processing_lesson.apply_async(args=[lessons[i]], queue=str(i), priority=i)
        # processing_lesson(lessons[i])
        sleep(5)
    j = load
    while j < len(lessons):
        for i in range(load):
            if p[str(i)].status == 'SUCCESS' or p[str(i)].status == 'FAILURE':
                p[str(i)] = processing_lesson.apply_async(args=[lessons[j]], queue=str(i), priority=i)
                j += 1
                if j >= len(lessons):
                    break
                sleep(5)
        if j >= len(lessons):
            break


@celery.task(name='stream.processing_recording')
def processing_recording(recording):
    """Celery function for the image processing."""
    room = recording['room_name']
    rec_datetime = datetime.strptime(recording['date'] + ' ' + recording['start_time'], '%Y-%m-%d %H:%M:%S')
    date = rec_datetime.strftime('%Y-%m-%d')
    time = rec_datetime.strftime('%H:%M')
    filename = 'queue/' + str(uuid.uuid4()) + '.mp4'
    # try:
    #     # gdd.download_file_from_google_drive(file_id=recording['url'].split('/')[-2],
    #     #                                     dest_path=filename, unzip=True)
    #     api.download_file_from_google_drive(recording['url'].split('/')[-2], filename)
    #     sleep(35)
    # except:

    try:
        filename = api.download_video_nvr_via_link(recording['url'], filename)
        sleep(35)
    except:
        msg = f'Searching file in NVR archive something went wrong'
        return None, None, recording, msg

    i = 30
    while not os.path.isfile(filename):
        sleep(5)
        i -= 1
        if i == 0:
            return None, None, recording, 'Video file was not created'

    sleep(60)

    if filename is not None:
        rofl, fps_factor = load_config()
        print(filename)
        print("queue/" + filename.split('/')[1])
        # json_filename = rofl.json_run("queue", filename.split('/')[1], emotions=data['em'],
        #                recognize=data['recog'], remember=data['remember'],
        #                fps_factor=fps_factor)
        json_filename = rofl.streamline_run('queue', filename.split('/')[1], fps_factor, emotions=True,
                                            recognize=False, remember=False)
        retries = 0
        while json_filename is None and retries < 7:
            json_filename = rofl.streamline_run('queue', filename.split('/')[1], fps_factor, emotions=True,
                                                recognize=False, remember=False)
            retries += 1

        print(json_filename)
        if json_filename is None:
            return None, recording['metrics_lapse'], recording, 'JSON file was not created'
        with open(json_filename, "r") as f:
            data = json.load(f)
        array = data['frames']
        fps = data['fps']

        sleep(60)
        i = 30
        while not os.path.isfile(json_filename):
            sleep(5)
            i -= 1
            if i == 0:
                return None, None, recording, 'JSON file was not created'
        rec = Recording.get(room, date, time)
        if rec is not None:
            Recording.update(room, date, time, json.dumps(data))
        else:
            Recording.create(filename, room, date, time, json.dumps(data))
        # vid_link = send_file(json_filename, link='view')

        dt = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')
        dt = dt.isoformat()

        video, metrics_lapse = video_maker.optimized_render('video_output', str(uuid.uuid4()) + '.mp4', array, fps,
                                                            recording['metrics_lapse'], headcount=True)
        resp, file_id = api.upload_video_nvr(video, dt, room, 'emotions ' + dt)
        data = {
            'emotions_url': resp['file_url']
        }
        api.update_url_erudite(recording['id'], data)

        # if email is not None:
        #     api.send_file_with_email(email, "Processed video",
        #                              "Thank you, that's your processed video\nHere is your video:\n" + vid_link)
        os.remove(video)
        os.remove(filename)
        return video, metrics_lapse, recording, 'SUCCESS'
    return None, recording['metrics_lapse'], recording, 'Video file was not created'


def stream_metrics_only(date, n=2):
    now = date
    recordings = api.get_emotion_recordings(now)

    if recordings:
        recordings = sorted(recordings, key=lambda k: k['start_time'])
        metrics_lapse_buffer = {}
        for recording in recordings:
            if recording['room_name'] not in metrics_lapse_buffer:
                metrics_lapse_buffer[recording['room_name']] = []
        p = {}
        # load = min(n, len(lessons))
        for i in range(n):
            recordings[i]['metrics_lapse'] = metrics_lapse_buffer[recordings[i]['room_name']]
            p[str(i)] = processing_recording.apply_async(args=[recordings[i]], queue=str(i), priority=i)
            # processing_lesson(lessons[i])
            sleep(5)
        j = n
        while j < len(recordings):
            for i in range(n):
                if p[str(i)].status == 'SUCCESS' or p[str(i)].status == 'FAILURE':
                    recordings[j]['metrics_lapse'] = []
                    if p[str(i)].status == 'SUCCESS':
                        metrics_lapse_buffer[p[str(i)].result[2]['room_name']] = p[str(i)].result[1]
                        recordings[j]['metrics_lapse'] = metrics_lapse_buffer[recordings[j]['room_name']]
                    p[str(i)] = processing_recording.apply_async(args=[recordings[j]], queue=str(i), priority=i)
                    j += 1
                    if j >= len(recordings):
                        break
                    sleep(5)
            if j >= len(recordings):
                break
    return 0


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-w', action='store', dest="workers", default=2, type=int)
    parser.add_argument('-d', action='store', dest='start_date', default='2021-04-20', type=str)
    parser.add_argument('-o', action='store', dest='optimized', default=0, type=int)
    args = parser.parse_args()
    date_begin = isoparse(args.start_date)
    is_optimized = args.optimized == 1

    # date_begin = date(2020, 2, 6)
    # time_begin = datetime(1, 1, 1, 9, 30)  # время 9:30
    # time_begin = datetime(1, 1, 1, int(args.start_time.split(':')[0]), int(args.start_time.split(':')[1]))
    # time_begin = datetime.strptime(args.start_time, '%H:%M')
    # time_end = datetime(1, 1, 1, int(args.end_time.split(':')[0]), int(args.end_time.split(':')[1]))  # время 16:00
    # time_end = datetime.strptime(args.end_time, '%H:%M')
    workers = args.workers  # сюда писать количество воркеров
    delta = timedelta(days=1)

    data = {}
    data['date'] = date_begin.strftime('%Y-%m-%d')
    # data['time'] = time_begin.strftime('%H:%M')
    # processing_nvr_(data)
    rooms = ['305', '306', '504']
    for i in range(workers):
        str_command = ['celery', 'worker', '-A', 'stream.celery', '--loglevel=info', '-n', str(i), '-Q', str(i), '-P', 'eventlet']
        p = subprocess.Popen(str_command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=os.environ)
    if is_optimized:
        stream_optimized(rooms, workers)
    else:
        while True:
            now = datetime.now()
            if date_begin < datetime(now.year, now.month, now.day, 23, 59, 59) - delta:
                stream_metrics_only(date_begin, workers)
                date_begin += delta
            sleep(15*60)

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
