import subprocess


class EmbeddedFirewall:
    def __init__(self, connection_limit=100, is_active=True):
        self.blocked_ips: set = set()
        self.ip_connections: dict = {}
        self.connection_limit: int = connection_limit
        self.is_active: bool = is_active

    def add_connection(self, ip_address):
        if self.is_active:
            """Compte les connexions pour une adresse IP et bloque l'IP si le seuil est dépassé."""
            if ip_address in self.blocked_ips:
                return  # Ne rien faire si l'IP est déjà bloquée

            # Compter la connexion
            if ip_address not in self.ip_connections:
                self.ip_connections[ip_address] = 0
            self.ip_connections[ip_address] += 1

            # Vérifier si le seuil est dépassé et bloquer l'IP si nécessaire
            if self.ip_connections[ip_address] > self.connection_limit:
                self.block_ip(ip_address)
                print(f"Adresse IP {ip_address} a dépassé la limite de connexion et est maintenant bloquée.")
        else:
            pass

    def block_ip(self, ip_address):
        """Bloque une adresse IP en utilisant iptables."""
        if ip_address not in self.blocked_ips:
            cmd = ["sudo", "iptables", "-A", "INPUT", "-s", ip_address, "-j", "DROP"]
            try:
                subprocess.run(cmd, check=True)
                self.blocked_ips.add(ip_address)
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors du blocage de l'adresse IP {ip_address}: {e}")

    def unblock_ip(self, ip_address):
        """Débloque une adresse IP précédemment bloquée."""
        if ip_address in self.blocked_ips:
            cmd = ["sudo", "iptables", "-D", "INPUT", "-s", ip_address, "-j", "DROP"]
            try:
                subprocess.run(cmd, check=True)
                self.blocked_ips.remove(ip_address)
                if ip_address in self.ip_connections:
                    del self.ip_connections[ip_address]
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors du déblocage de l'adresse IP {ip_address}: {e}")

    def list_blocked_ips(self):
        """Affiche la liste des adresses IP actuellement bloquées."""
        print("Adresses IP bloquées :")
        for ip in self.blocked_ips:
            print(ip)

