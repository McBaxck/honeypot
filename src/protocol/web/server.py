import json
import time

import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import os


class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.path = 'src/protocol/web/index.html'
        client_ip = self.client_address[0]
        user_agent = self.headers['User-Agent']
        request_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # Tests protected datas via stdout
        print(f"Requête reçue de {client_ip} à {request_time}")
        print(f"User-Agent: {user_agent}")
        print(f"Chemin demandé: {self.path}")
        try:
            # Construction du chemin absolu du fichier demandé
            file_to_open = open(self.path).read()
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


def launch_web_server(port: int, server_class=HTTPServer, handler_class=WebServer):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    try:
        print(f"Web Server is starting on {port}...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Interrupting by User Event, stopping the Web Server...")
        httpd.server_close()


