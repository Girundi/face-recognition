# import os
# from db import init_db_command
# import sqlite3
from Rest_api import app
# import argparse
# from stream import stream_background

if __name__ == "__main__":

    # if not os.path.isdir('video_output'):
    #     os.mkdir('video_output')
    # if not os.path.isdir('queue'):
    #     os.mkdir('queue')
    # if not os.path.isdir('recordings'):
    #     os.mkdir('recordings')
    # stream_background.apply_async(queue='2', priority=1)
    #
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-d', action='store', dest='debug', default=False, type=bool)
    # # parser.add_argument('-h', action='store', dest='host', default='0.0.0.0', type=str)
    # parser.add_argument('-p', action='store', dest='port', default='5000', type=str)
    # args = parser.parse_args()
    #
    # try:
    #     init_db_command()
    #     pass
    # except sqlite3.OperationalError:
    #     # Assume it's already been created
    #     pass

    app.run(host='0.0.0.0', port='80')
