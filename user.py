from flask_login import UserMixin
from db import get_db
import pandas as pd


class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic, access):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.access = access

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3], access=user[4]
        )
        return user

    @staticmethod
    def get_email(email):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE email = ?", (email,)
        ).fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3], access=user[4]
        )
        return user

    @staticmethod
    def update(user):
        db = get_db()
        db.execute(
            "UPDATE user SET name = ? , email = ? , profile_pic = ? , access = ?  WHERE id = ?",
            (user.name, user.email, user.profile_pic, user.access, user.id_),
        )
        db.commit()
        return user

    @staticmethod
    def create(id_, name, email, profile_pic, access):
        db = get_db()
        db.execute(
            "INSERT INTO user (id, name, email, profile_pic, access) "
            "VALUES (?, ?, ?, ?, ?)",
            (id_, name, email, profile_pic, access),
        )
        db.commit()

    @staticmethod
    def get_dataframe():
        db = get_db()
        return pd.read_sql_query("SELECT * from user", db)


class Recording:
    def __init__(self, file, room_num, rec_date, rec_time, json):
        self.file = file
        self.room = room_num
        self.rec_date = rec_date
        self.rec_time = rec_time
        self.json = json

    @staticmethod
    def get(room_num, rec_date, rec_time):
        db = get_db()
        recording = db.execute(
            "SELECT * FROM recording WHERE room_num = ? AND rec_date = ? AND rec_time = ?", (room_num, rec_date, rec_time)
        ).fetchone()
        if not recording:
            return None

        recording = Recording(
            file=recording[0], room_num=recording[1], rec_date=recording[2], rec_time=recording[3], json=recording[4]
        )
        return recording

    @staticmethod
    def create(file, room_num, rec_date, rec_time, json):
        db = get_db()
        db.execute(
            "INSERT INTO recording (file, room_num, rec_date, rec_time, json) "
            "VALUES (?, ?, ?, ?, ?)",
            (file, room_num, rec_date, rec_time, json),
        )
        db.commit()

    @staticmethod
    def get_dataframe():
        db = get_db()
        return pd.read_sql_query("SELECT * from recording", db)

    @staticmethod
    def delete(room_num, rec_date, rec_time):
        db = get_db()
        db.execute(
            "DELETE FROM recording WHERE room_num = ? AND rec_date = ? AND rec_time = ?",
            (room_num, rec_date, rec_time),
        )
        db.commit()


class Room:
    def __init__(self, room_num, google_folder, tag):
        self.room_num = room_num
        self.google_folder = google_folder
        self.tag = tag

    @staticmethod
    def get(room_num):
        db = get_db()
        room = db.execute(
            "SELECT * FROM room WHERE room_num = ?", (room_num,)
        ).fetchone()
        if not room:
            return None

        room = Room(
            room_num=room[0], google_folder=room[1], tag=room[2]
        )
        return room

    @staticmethod
    def update(room):
        db = get_db()
        db.execute(
            "UPDATE room SET google_folder = ? , tag = ? WHERE room_num = ?",
            (room.google_folder, room.tag, room.room_num),
        )
        db.commit()
        return room

    @staticmethod
    def create(room_num, google_folder, tag):
        db = get_db()
        db.execute(
            "INSERT INTO room (room_num, google_folder, tag) "
            "VALUES (?, ?, ?)",
            (room_num, google_folder, tag),
        )
        db.commit()

    @staticmethod
    def get_dataframe():
        db = get_db()
        return pd.read_sql_query("SELECT * from room", db)


class Api_key:
    def __init__(self, uuid):
        self.uuid = uuid

    @staticmethod
    def create(uuid):
        db = get_db()
        db.execute(
            "INSERT INTO api_key (uuid) "
            "VALUES (?)",
            (uuid),
        )
        db.commit()

    @staticmethod
    def get_dataframe():
        db = get_db()
        return pd.read_sql_query("SELECT * from api_key", db)



