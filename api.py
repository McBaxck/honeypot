import datetime
import logging.config
import logging
import threading
import time
import os
from flask_cors import CORS
from flask import Flask, request, jsonify
from src.db.supabase import HoneyPotHandler, HTTPServerDB
from src.hp import HolyPot
from src.config import HolyPotConfig, HostConfig, GLOBAL_LOGGING_CONFIG

BASE_ROUTE: str = "/holypot-api/v1"

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": ["*"]}})

logging.config.dictConfig(GLOBAL_LOGGING_CONFIG)


def list_content_folder(path):
    content = os.listdir(path)  # Liste tous les fichiers et dossiers
    res = {}
    for name in content:
        full_path = os.path.join(path, name)
        if os.path.isdir(full_path):
            res[name] = 'folder'
        else:
            res[name] = 'file'
    return res


class HolyPotApp:
    def __init__(self, hp_set):
        self.hp_set = hp_set
        self.holypot = None
        self.host_set: HostConfig = HostConfig()
        self.is_running: bool = False

    def run(self):
        time.sleep(5)
        if not self.is_running:
            self.holypot = HolyPot(self.hp_set)
            thread = threading.Thread(target=self.holypot.run)
            thread.start()
            self.is_running = True
            return jsonify({"message": "OK"})
        else:
            return jsonify({"message": "Already running..."})

    def shutdown(self):
        if self.holypot:
            self.holypot.shutdown()
        return jsonify({"message": "OK"})

    def devices(self):
        return jsonify({"devices": self.host_set.devices})

    def get_config(self):
        return jsonify(self.hp_set.__dict__)

    def add_service(self):
        data = request.json
        self.holypot.add_service(data['on_ports'], data['service'])
        return jsonify({data['service']: "OK"})

    def set_config(self):
        data = request.json
        self.hp_set.host = data['host']
        self.hp_set.ports = data['ports']
        self.hp_set.name = data['name']
        self.hp_set.fw_security = data['fw_security']
        self.hp_set.mode = data['mode']
        return jsonify({"message": "OK"})

    def get_service_logs(self):
        data = request.json
        service: str = data["service"]
        return jsonify(list_content_folder("src/protocol/{service}/logs/".format(service=service)))

    @staticmethod
    def get_logs():
        db_handler: HoneyPotHandler = HoneyPotHandler()
        return db_handler.fetch_all_logs().data

    @staticmethod
    def get_ssh_logs():
        db_handler: HoneyPotHandler = HoneyPotHandler()
        return db_handler.fetch_all(table='ssh_logs').data

    @staticmethod
    def get_http_logs():
        try:
            db_handler: HTTPServerDB = HTTPServerDB()
            if db_handler.fetch_all(table='http_logs').data is None:
                return jsonify({"message": "No logs found"})
            return db_handler.fetch_all_logs().data
        except (TypeError, Exception):
            return jsonify({"message": "error fetching logs"})


hp_set: HolyPotConfig = HolyPotConfig()
holy_pot_app = HolyPotApp(hp_set)


@app.route(f'{BASE_ROUTE}/run', methods=['GET'])
def run():
    return holy_pot_app.run()


@app.route(f'{BASE_ROUTE}/service/logs', methods=['GET'])
def get_srv_logs():
    return holy_pot_app.get_service_logs()


@app.route(f'{BASE_ROUTE}/shutdown', methods=['GET'])
def shutdown():
    return holy_pot_app.shutdown()


@app.route(f'{BASE_ROUTE}/devices', methods=['GET'])
def devices():
    return holy_pot_app.devices()


@app.route(f'{BASE_ROUTE}/config', methods=['GET'])
def get_config():
    return holy_pot_app.get_config()


@app.route(f'{BASE_ROUTE}/service/add', methods=['POST'])
def add_service():
    return holy_pot_app.add_service()


@app.route(f'{BASE_ROUTE}/config', methods=['POST'])
def set_config():
    return holy_pot_app.set_config()


@app.route(f'{BASE_ROUTE}/logs', methods=['GET'])
def get_all_logs():
    return holy_pot_app.get_logs()


@app.route(f'{BASE_ROUTE}/logs/ssh', methods=['GET'])
def get_ssh_logs():
    return holy_pot_app.get_ssh_logs()


@app.route(f'{BASE_ROUTE}/logs/http', methods=['GET'])
def get_http_logs():
    return holy_pot_app.get_http_logs()


if __name__ == '__main__':
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        holy_pot_app.shutdown()
        print(f"Ending holypot process at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
