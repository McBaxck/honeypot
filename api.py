import datetime
import json
import logging
import random
import time
import os

from flask_cors import CORS
from flask import Flask, request, jsonify, abort, Response
from src.db.postgres import HoneyPotHandler, HTTPServerDB, AccountDB, ModuleConfDB, StateDB, NetworkConfDB, \
    TelnetServerCommandHandler, FTPServerLogHandler, BlockedIPDB
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

    @staticmethod
    def status(honeypot):
        status_db: StateDB = StateDB()
        return jsonify(status_db.get_state(honeypot))

    @staticmethod
    def get_ip_status(ip):
        status_db: StateDB = StateDB()
        return jsonify(status_db.get_state_by_ip(ip))

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
    def get_telnet_logs():
        db_handler: TelnetServerCommandHandler = TelnetServerCommandHandler()
        return db_handler.fetch_all_logs().data

    @staticmethod
    def get_ftp_logs():
        db_handler: FTPServerLogHandler = FTPServerLogHandler()
        return db_handler.fetch_all_logs().data

    @staticmethod
    def get_stats():
        db_handler: HoneyPotHandler = HoneyPotHandler()
        stats = db_handler.get_stats()
        stats['blocked_ips_count'] = len(BlockedIPDB().list_blocked().data)
        return jsonify(stats)

    @staticmethod
    def block_ip():
        data: dict = request.json
        db_handler: BlockedIPDB = BlockedIPDB()
        return jsonify(db_handler.block(data['ip'], data.get('reason')).data[0])

    @staticmethod
    def unblock_ip():
        data: dict = request.json
        db_handler: BlockedIPDB = BlockedIPDB()
        db_handler.unblock(data['ip'])
        return jsonify({"message": "OK"})

    @staticmethod
    def get_blocked_ips():
        db_handler: BlockedIPDB = BlockedIPDB()
        return jsonify(db_handler.list_blocked().data)

    @staticmethod
    def stream_logs():
        """Flux SSE : pousse les nouvelles lignes de la table `logs` (alimentée par
        ConnectionGate.intake pour chaque connexion, tous protocoles confondus) au fur
        et à mesure de leur écriture, par polling Postgres toutes les ~1.5s."""
        db_handler: HoneyPotHandler = HoneyPotHandler()
        last_id = db_handler.get_max_id()

        def _generate():
            nonlocal last_id
            while True:
                result = db_handler.fetch_since(last_id)
                for row in result.data:
                    last_id = row['id']
                    yield f"data: {json.dumps(row, default=str)}\n\n"
                time.sleep(1.5)

        return Response(_generate(), mimetype='text/event-stream')

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


@app.route(f'{BASE_ROUTE}/account/<username>', methods=['GET'])
def get_account_username(username):
    return holy_pot_app.get_account(username)


@app.route(f'{BASE_ROUTE}/logs', methods=['GET'])
def get_all_logs():
    return holy_pot_app.get_logs()


@app.route(f'{BASE_ROUTE}/logs/ssh', methods=['GET'])
def get_ssh_logs():
    return holy_pot_app.get_ssh_logs()


@app.route(f'{BASE_ROUTE}/logs/http', methods=['GET'])
def get_http_logs():
    return holy_pot_app.get_http_logs()


@app.route(f'{BASE_ROUTE}/logs/telnet', methods=['GET'])
def get_telnet_logs():
    return holy_pot_app.get_telnet_logs()


@app.route(f'{BASE_ROUTE}/logs/ftp', methods=['GET'])
def get_ftp_logs():
    return holy_pot_app.get_ftp_logs()


@app.route(f'{BASE_ROUTE}/stream/logs', methods=['GET'])
def stream_logs():
    return holy_pot_app.stream_logs()


@app.route(f'{BASE_ROUTE}/stats', methods=['GET'])
def get_stats():
    return holy_pot_app.get_stats()


@app.route(f'{BASE_ROUTE}/firewall/block', methods=['POST'])
def firewall_block():
    return holy_pot_app.block_ip()


@app.route(f'{BASE_ROUTE}/firewall/unblock', methods=['POST'])
def firewall_unblock():
    return holy_pot_app.unblock_ip()


@app.route(f'{BASE_ROUTE}/firewall/blocked', methods=['GET'])
def firewall_blocked():
    return holy_pot_app.get_blocked_ips()


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


@app.route(f'{BASE_ROUTE}/network/conf/<honeypot_id>', methods=['GET'])
def get_netconf(honeypot_id):
    return holy_pot_app.get_network_conf(honeypot_id)


if __name__ == '__main__':
    try:
        app.run(
            host=os.environ.get('API_HOST', '0.0.0.0'),
            port=int(os.environ.get('API_PORT', 5000)),
            debug=os.environ.get('FLASK_DEBUG', '0') == '1',
            threaded=True,
        )
    except KeyboardInterrupt:
        print(f"Ending API process at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
