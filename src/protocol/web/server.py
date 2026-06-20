import os
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from src.config import DEFAULT_FILE_WEBPAGE_PATH
from src.db.postgres import HTTPServerDB
from src.network.utils import get_private_ip_and_iface
from src.protocol.web.page_mirroring import PageMirror

http_logger = logging.getLogger('HTTP')


class WebServer(BaseHTTPRequestHandler):
    gate = None
    listen_port = None

    def do_GET(self):
        client_ip, client_port = self.client_address[0], self.client_address[1]
        if self.gate is not None and not self.gate.intake(client_ip, client_port, get_private_ip_and_iface()[0],
                                                           self.listen_port, 'http'):
            self.send_response(403)
            self.end_headers()
            return

        self.path = 'src/protocol/web/cache/index.html'
        user_agent = self.headers['User-Agent']

        # Tests protected datas via stdout
        db_handler: HTTPServerDB = HTTPServerDB()
        log: dict = {
            "source_ip": client_ip,
            "source_port": client_port,
            "dest_ip": get_private_ip_and_iface()[0],
            "dest_port": self.listen_port,
            "user_agent": user_agent,
            "url": self.path
        }
        http_logger.info(f"Received request from {client_ip} with data from {user_agent}: \n {log}")
        db_handler.add_log(log)
        try:
            # Construction du chemin absolu du fichier demandé
            with open(self.path) as f:
                file_to_open = f.read()
            self.send_response(200)
        except FileNotFoundError:
            # Gestion des fichiers non trouvés
            self.send_response(404)
            file_to_open = "Fichier non trouvé"
        except Exception as e:
            # Gestion des autres erreurs
            self.send_response(500)
            file_to_open = "Erreur : " + str(e)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))


def launch_web_server(web_page, port: int, gate, server_class=HTTPServer, handler_class=WebServer):
    if os.path.exists(DEFAULT_FILE_WEBPAGE_PATH):
        http_logger.info("Removing actual index.html mirror page...")
        os.remove(DEFAULT_FILE_WEBPAGE_PATH)
    page_mirror_cursor: PageMirror = PageMirror(web_page,
                                                o='index.html')
    page_mirror_cursor.clone()
    handler_class.gate = gate
    handler_class.listen_port = port
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    try:
        print(f"Web Server is starting on {port}...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Interrupting by User Event, stopping the Web Server...")
        httpd.server_close()
