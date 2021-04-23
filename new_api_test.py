import requests
import pprint as pp
from api import get_recordings_erudite, get_lessons_erudite
from datetime import datetime
import json

nvr_key = {"key": "99a1dfb5342546319e3d5f4de7150f05"}
# data = {
#     'room_name': '504',
#     'fromdate': '2021-04-09',
#     'todate': '2021-04-09',
#     'start_time': '9:30',
#     'end_time': '10:30',
#     'type': 'Offline'
# # }
# res = requests.get("https://nvr.miem.hse.ru/api/erudite/records?fromdate=2020-04-10T0:00&todate=2021-04-10T10:30&room_name=504",
#                    headers=nvr_key)
# data = {
#     'emotions_url': "https://drive.google.com/file/d/1rp1YG8GsIO9fGYHp1NTVvK4yotn4pEri/preview"
# }
# res = requests.patch("https://nvr.miem.hse.ru/api/erudite/records/600ef2d1caaa139a238a4d9a", json=data, headers=nvr_key)
# res = get_recordings_erudite(datetime(2020, 10, 9, hour=9, minute=30), datetime(2020, 10, 9, hour=20, minute=00), 504)
# # # res = requests.get("https://nvr.miem.hse.ru/api/erudite/lessons?fromdate=2021-04-20T0:00&todate=2021-04-20T20:30&ruz_auditorium=305" +
# # #                    "&ruz_kind_of_work=Семинар", headers=nvr_key)
# # # res = get_lessons_erudite(datetime(2021, 4, 20), datetime(2021, 4, 20, hour=15, minute=0), 305)
# j = json.loads(res.text)
# id = j[0]['id']
# res = requests.get("https://nvr.miem.hse.ru/api/erudite/records/" + id, headers=nvr_key)
#
# pp.pprint(res.text)
# print('Семинар' == 'Семинар on-line')
# l = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
# i = 0
# while i != len(l):
#     print(l[i])
#     if not l[i] % 2:
#         l.pop(i)
#     else:
#         i += 1
    # print(el)

res = requests.get("https://nvr.miem.hse.ru/api/erudite/equipment?")