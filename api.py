import datetime
import threading
import time

from flask_cors import CORS
from flask import Flask, request, jsonify
from src.hp import HolyPot
from src.config import HolyPotConfig, HostConfig

BASE_ROUTE: str = "/holypot-api/v1"

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": ["*"]}})


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
        return jsonify({"devices": self.hp_set.devices})

    def get_config(self):
        return jsonify(self.hp_set.__dict__)

    def add_service(self):
        data = request.json
        self.holypot.add_service(data['on_ports'], data['service'])
        return jsonify({"message": "OK"})

    def set_config(self):
        data = request.json
        self.hp_set.host = data['host']
        self.hp_set.ports = data['ports']
        self.hp_set.name = data['name']
        self.hp_set.fw_security = data['fw_security']
        self.hp_set.mode = data['mode']
        return jsonify({"message": "OK"})


hp_set: HolyPotConfig = HolyPotConfig()
holy_pot_app = HolyPotApp(hp_set)


@app.route(f'{BASE_ROUTE}/run', methods=['GET'])
def run():
    return holy_pot_app.run()


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


if __name__ == '__main__':
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        holy_pot_app.shutdown()
        print(f"Ending holypot process at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
