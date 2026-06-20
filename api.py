import datetime
import logging
import random
import threading
import time
import os
from dataclasses import dataclass

from flask_cors import CORS
from flask import Flask, request, jsonify, abort, Response
from src.db.postgres import HoneyPotHandler, HTTPServerDB, AccountDB, ModuleConfDB, StateDB, NetworkConfDB
from src.hp import HolyPot
from src.config import HolyPotConfig, HostConfig, GLOBAL_LOGGING_CONFIG
from src.network.utils import scan, get_memory_info, get_network_ip_with_cidr, hash_password, \
    check_password, get_own_ip, get_public_ip, get_own_mac_addr, get_os_version
import warnings

from src.network.func.scan import NetworkScanner

# Ignorer tous les avertissements
warnings.filterwarnings("ignore")

BASE_ROUTE: str = "/holypot-api/v1"

app = Flask(__name__)
CORS(app, resources={r"/holypot-api/v1/*": {"origins": "*"}})

global_logger = logging.getLogger('GLOBAL_SET')


@dataclass
class WaitingService:
    service: str
    on_ports: list[int]


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
        # self.host_set: HostConfig = HostConfig()
        self.is_running: bool = False
        self._waiting_services: list[WaitingService] = []

    def run(self):
        time.sleep(3)
        if not self.is_running:
            self.holypot = HolyPot(self.hp_set)
            for waiting_service in self._waiting_services:
                print("Adding waiting service", waiting_service.service)
                print("Adding waiting ports", waiting_service.on_ports)
                self.holypot.add_service(service=waiting_service.service, on_ports=waiting_service.on_ports)
            thread = threading.Thread(target=self.holypot.run)
            thread.start()
            self.is_running = True
            return jsonify({"message": "OK"})
        else:
            return Response("Already running", status=403)

    @staticmethod
    def status(honeypot):
        status_db: StateDB = StateDB()
        return jsonify(status_db.get_state(honeypot))

    @staticmethod
    def get_ip_status(ip):
        status_db: StateDB = StateDB()
        return jsonify(status_db.get_state_by_ip(ip))

    def shutdown(self):
        if self.holypot:
            self.holypot.shutdown()
        self.is_running = False
        return jsonify({"message": "OK"})

    def get_config(self):
        return jsonify(self.hp_set.__dict__)

    def add_service(self):
        data = request.json
        payload: WaitingService = WaitingService(service=data['service'], on_ports=data['on_ports'])
        if payload not in self._waiting_services:
            self._waiting_services.append(payload)
            return jsonify({data['service']: "OK"})
        else:
            return jsonify({data['service']: "Ports already saved as use!"})

    def set_config(self):
        data = request.json
        print("/set_config ---> ", data)
        self.hp_set.host = data['host']
        self.hp_set.ports = data['ports']
        self.hp_set.name = data['name']
        self.hp_set.fw_security = data['fw_security']
        self.hp_set.mode = data['mode']
        return jsonify({"message": "OK"})

    @staticmethod
    def set_status():
        data = request.json
        state_db: StateDB = StateDB()
        state_db.set_honeypot_state(data)
        return jsonify({"message": "OK"})

    @staticmethod
    def get_service_logs():
        data = request.json
        service: str = data["service"]
        return jsonify([list_content_folder("src/protocol/{service}/logs/".format(service=service))])

    @staticmethod
    def get_account(username):
        account_db: AccountDB = AccountDB()
        return jsonify(account_db.get_account_by_username(username).data[0])

    @staticmethod
    def register():
        data: dict = request.json
        account_data: dict = {
            "user": data["username"],
            "password": hash_password(data["password"]).decode(),
            "email": data["email"] if data.get("email") else f"{data['username']}@holypot-domain.fr",
            "name": data["name"] if data.get("name") else f"honeypot{random.randint(1, 100000)}",
        }
        account_handler: AccountDB = AccountDB()
        account_handler.insert("accounts", account_data)
        return jsonify(account_handler.get_account(name=account_data['name']).data[0])

    @staticmethod
    def signin():
        data: dict = request.json
        db_handler: AccountDB = AccountDB()
        try:
            if db_handler.verify_user_credentials(username=data["username"], password=data["password"]):
                return jsonify(
                    db_handler.get_hp_name(username=data["username"]).data[0]
                )
            else:
                return Response("Bad Request", status=400)
        except Exception as e:
            print("error_request (signin) -> ", e)
            return Response("Bad Request", status=400)

    @staticmethod
    def post_service_conf():
        data: dict = request.json
        db_handler: ModuleConfDB = ModuleConfDB()
        db_handler.post_conf_json(data)
        return "Saving configuration for {}".format(data.get("module"))

    @staticmethod
    def add_service_account():
        data: dict = request.json
        username = data.get("username")
        password = data.get("password")
        module = data.get("module")

    @staticmethod
    def get_network_devices():
        return jsonify(scan(get_network_ip_with_cidr()))

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

    @staticmethod
    def save_network_conf():
        data = request.json
        honeypot_id = data["honeypot_id"]
        conf = data["conf"]
        net_handler: NetworkConfDB = NetworkConfDB()
        net_handler.save_conf(honeypot_id, conf)
        return jsonify({"message": "ok"})

    @staticmethod
    def get_network_conf(honeypot_id):
        net_handler: NetworkConfDB = NetworkConfDB()
        return net_handler.get_network_conf(honeypot_id).data[0]


hp_set: HolyPotConfig = HolyPotConfig()
holy_pot_app = HolyPotApp(hp_set)


@app.route(f'{BASE_ROUTE}/run', methods=['GET'])
def run():
    return holy_pot_app.run()


@app.route(f'{BASE_ROUTE}/status/:hid', methods=['GET'])
def status(hid):
    time.sleep(3)
    return holy_pot_app.status(hid)


@app.route(f'{BASE_ROUTE}/status/ip/:ip', methods=['GET'])
def status_ip(ip):
    time.sleep(3)
    return holy_pot_app.get_ip_status(ip)


@app.route(f'{BASE_ROUTE}/status', methods=['POST'])
def set_hp_status():
    time.sleep(3)
    return holy_pot_app.set_status()


@app.route(f'{BASE_ROUTE}/service/logs', methods=['GET', 'POST'])
def get_srv_logs():
    return holy_pot_app.get_service_logs()


@app.route(f'{BASE_ROUTE}/service/configuration', methods=['POST'])
def save_service_conf():
    return holy_pot_app.post_service_conf()


@app.route(f'{BASE_ROUTE}/shutdown', methods=['GET'])
def shutdown():
    return holy_pot_app.shutdown()


@app.route(f'{BASE_ROUTE}/account/<username>', methods=['GET'])
def get_account_username(username):
    return holy_pot_app.get_account(username)


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


@app.route(f'{BASE_ROUTE}/network/scan', methods=['GET'])
def get_net_scan_devices():
    network_scanner: NetworkScanner = NetworkScanner()
    return network_scanner.start()


@app.route(f'{BASE_ROUTE}/host', methods=['GET'])
def get_host_infos():
    return jsonify({
        "lo": get_own_ip(),
        "pub": get_public_ip(),
        "mac": get_own_mac_addr(),
        "os": get_os_version(),
        "memory": get_memory_info()
    })


@app.route(f'{BASE_ROUTE}/register', methods=['POST'])
def hp_register():
    return holy_pot_app.register()


@app.route(f'{BASE_ROUTE}/signin', methods=['POST'])
def hp_signin():
    return holy_pot_app.signin()


@app.route(f'{BASE_ROUTE}/network/conf', methods=['POST'])
def set_netconf():
    return holy_pot_app.save_network_conf()


@app.route(f'{BASE_ROUTE}/run/status', methods=['GET'])
def get_run_status():
    return jsonify({"is_running": holy_pot_app.is_running})


@app.route(f'{BASE_ROUTE}/network/conf/<honeypot_id>', methods=['GET'])
def get_netconf(honeypot_id):
    return holy_pot_app.get_network_conf(honeypot_id)


if __name__ == '__main__':
    try:
        app.run(
            host=os.environ.get('API_HOST', '0.0.0.0'),
            port=int(os.environ.get('API_PORT', 5000)),
            debug=os.environ.get('FLASK_DEBUG', '0') == '1',
        )
    except KeyboardInterrupt:
        holy_pot_app.shutdown()
        print(f"Ending holypot process at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
