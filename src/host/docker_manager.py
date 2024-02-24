import os
import pty
import select
import signal
import subprocess
import threading

import docker
import logging
import docker.errors
import docker.types
import paramiko
import pexpect
from docker.models.resource import Model

# Configuration du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.container_id: str = ''

    def create_and_run_container(self, img, on_ports=None):
        try:
            logging.info(f"Tentative de lancement du conteneur avec l'image {img}")
            ctn = self.client.containers.run(img, detach=True, ports=on_ports, network_mode="bridge",
                                             command='tail -f /dev/null')
            logging.info(f"Conteneur {ctn.id} lancé avec succès")
            return ctn
        except docker.errors.ImageNotFound:
            logging.warning(f"L'image {img} n'existe pas. Tentative de récupération...")
            self.pull_image(img)
            return self.create_and_run_container(img, on_ports)
        except Exception as e:
            logging.error(f"Erreur lors de la création du conteneur: {e}")
            return None

    def pull_image(self, img):
        """
        Récupère une image Docker depuis le Docker Hub.
        """
        try:
            logging.info(f"Récupération de l'image {img}")
            pulled_image = self.client.images.pull(img)
            logging.info(f"Image {img} récupérée avec succès: {pulled_image.tags}")
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'image {img}: {e}")

    def build_image_from_dockerfile(self, path, dockerfile, tag):
        """
        Construit une image Docker à partir d'un Dockerfile-ubuntu.

        :param path: Chemin vers le répertoire contenant le Dockerfile-ubuntu.
        :param tag: Tag à attribuer à l'image construite.
        """
        try:
            logging.info(f"Construction de l'image {tag} à partir du Dockerfile-ubuntu dans {path}")
            img, build_logs = self.client.images.build(path=path, tag=tag, rm=True, dockerfile=dockerfile)
            for chunk in build_logs:
                if 'stream' in chunk:
                    logging.info(chunk['stream'].strip())
            logging.info(f"Image {tag} construite avec succès")
            return img
        except Exception as e:
            logging.error(f"Erreur lors de la construction de l'image {tag}: {e}")
            return None

    def get_container_id(self, container_name):
        """
        Récupère l'ID d'un conteneur Docker en fonction de son nom.

        :param container_name: Nom du conteneur Docker.
        :return: L'ID du conteneur si trouvé, sinon None.
        """
        try:
            container = self.client.containers.get(container_name)
            return container.id
        except docker.errors.NotFound:
            print(f"Le conteneur {container_name} n'a pas été trouvé.")
            return None
        except Exception as e:
            print(f"Une erreur s'est produite lors de la récupération de l'ID du conteneur {container_name}: {e}")
            return None

    def list_containers(self, all_containers=True):
        """
        Liste tous les conteneurs Docker, actifs ou non, avec leurs noms.

        :param all_containers: Si True, liste tous les conteneurs. Sinon, seulement ceux en cours d'exécution.
        :return: Une liste de tuples (conteneur ID, conteneur noms).
        """
        containers_list = []
        try:
            for ctn in self.client.containers.list(all=all_containers):
                # Les noms des conteneurs sont préfixés par '/', donc on les nettoie
                container_names = [name.strip("/") for name in ctn.names]
                containers_list.append((ctn.id, container_names))
            logging.info("Liste des conteneurs récupérée avec succès.")
        except docker.errors.APIError as e:
            logging.error(f"Erreur Docker API lors de la liste des conteneurs: {e}")
        return containers_list

    def run_container(self, image_name, container_name):
        """
        Lance un conteneur Docker à partir d'une image spécifiée.

        :param container_name: the container name to run
        :param image_name: Nom de l'image à utiliser pour lancer le conteneur.
        """
        try:
            # Exécuter le conteneur
            container = self.client.containers.run(image_name,
                                                   detach=True,
                                                   name=container_name,
                                                   ports={'22/tcp': 2222}
                                                   )
            self.container_id = container.id
            print(f"Conteneur {container.id} lancé avec succès à partir de l'image {image_name}.")
            return container
        except Exception as e:
            print(f"Erreur lors du lancement du conteneur à partir de l'image {image_name}: {e}")
            return None

    def stop_container(self, container_id):
        """
        Arrête un conteneur Docker spécifié par son ID.
        """
        try:
            ctn = self.client.containers.get(container_id)
            ctn.stop()
            logging.info(f"Conteneur {container_id} (nom(s): {ctn.names}) arrêté avec succès")
        except docker.errors.NotFound:
            logging.warning(f"Conteneur {container_id} non trouvé")
        except docker.errors.APIError as e:
            logging.error(f"Erreur Docker API lors de l'arrêt du conteneur {container_id}: {e}")

    def create_network(self, name, subnet, gateway):
        """
        Crée un réseau Docker avec un sous-réseau et une passerelle spécifiques.

        :param name: Nom du réseau.
        :param subnet: Sous-réseau, par exemple "172.18.0.0/16".
        :param gateway: Passerelle, par exemple "172.18.0.1".
        :return: L'objet réseau créé.
        """
        ipam_pool = docker.types.IPAMPool(
            subnet=subnet,
            gateway=gateway
        )
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
        network = self.client.networks.create(name, ipam=ipam_config, driver="bridge")
        return network

    def run_container_with_network_settings(self, image_name, network_name, container_name=None, ipv4_address=None):
        """
        Lance un conteneur et le connecte à un réseau spécifié avec des paramètres réseau personnalisés.

        :param image_name: Nom de l'image Docker à utiliser.
        :param network_name: Nom du réseau Docker auquel connecter le conteneur.
        :param container_name: Nom optionnel à attribuer au conteneur.
        :param ipv4_address: Adresse IP v4 à attribuer au conteneur dans le réseau.
        :return: L'objet conteneur lancé.
        """
        container = self.client.containers.create(image_name, name=container_name, detach=True)
        network = self.client.networks.get(network_name)
        network.connect(container, ipv4_address=ipv4_address)
        container.start()
        return container

    def exec_command_in_container(self, container_id_or_name, command, channel: paramiko.Channel):
        """
        Exécute une commande à l'intérieur d'un conteneur Docker spécifié.

        :param channel:
        :param container_id_or_name: ID ou nom du conteneur dans lequel exécuter la commande.
        :param command: Commande à exécuter à l'intérieur du conteneur.
        :param client_channel: Canal Paramiko pour envoyer la sortie de la commande au client.
        """
        # try:
        #     # Exécute la commande dans un conteneur Docker et redirige la sortie vers le canal du client via Paramiko
        #     exec_id = self.client.api.exec_create(container=container_id_or_name,
        #                                           cmd=command, stdout=True, stderr=True,
        #                                           privileged=True)
        #     output_generator = self.client.api.exec_start(exec_id, stream=True, tty=True, detach=False)
        #     # Lit en temps réel la sortie de la commande et l'envoie au client
        #     for output_chunk in output_generator:
        #         output: str = '\r\n'+output_chunk.decode("utf-8").replace('\r', '\r\n').replace('\n', '\r\n').replace('\t', '\r\n')
        #         print('output-> ', output)
        #         channel.sendall(output.encode('utf-8'))
        # except Exception as e:
        #     print(f"Erreur lors de l'exécution de la commande dans le conteneur {container_id_or_name}: {e}")
        #     channel.sendall(f"error: {e}".encode('utf-8'))
        try:
            # Exécute un shell interactif dans le conteneur Docker
            exec_id = self.client.api.exec_create(container=container_id_or_name, cmd="/bin/sh", stdin=True,
                                                  stdout=True, stderr=True, tty=True)
            stream = self.client.api.exec_start(exec_id, stream=True, tty=True)

            # Redirige le flux de sortie du shell vers le canal Paramiko
            for line in stream:
                try:
                    channel.sendall(line)
                except Exception as e:
                    print(f"Erreur lors de la transmission du shell: {e}")
                    break
        except Exception as e:
            print(f"Erreur lors du démarrage du shell dans le conteneur {container_id_or_name}: {e}")

    def handle_signal(self, client_channel, stop_event):
        """
        Surveille les signaux de terminaison du client.

        :param client_channel: Canal Paramiko pour envoyer la sortie de la commande au client.
        :param stop_event: Objet Event pour indiquer l'arrêt de la commande.
        """
        try:
            while True:
                # Vérifie si le client a fermé la connexion SSH
                if client_channel.closed:
                    stop_event.set()
                    break
                # Vérifie si le client a envoyé un signal de terminaison (Ctrl+C)
                if client_channel.recv_ready():
                    client_input = client_channel.recv(1024).decode("utf-8")
                    if client_input == "\x03":  # Ctrl+C
                        stop_event.set()
                        break
        except Exception as e:
            print(f"Erreur lors de la gestion des signaux du client : {e}")

    def kill_all(self, container_id_or_name, proc_name: str, channel: paramiko.Channel) -> None:
        command: str = f'killall {proc_name}'
        self.exec_command_in_container(container_id_or_name, command, channel)

# Exemple d'utilisation
# if __name__ == "__main__":
#     manager = DockerManager()
#     image_tag = "device_simulation_test2"
#     ports = {"80/tcp": 8080}  # Exemple de redirection de port
#     image = manager.build_image_from_dockerfile(path='./src/host/devices', tag=image_tag)
#     manager.run_container(image_tag, container_name='malagangx667')
