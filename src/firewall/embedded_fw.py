import subprocess


class EmbeddedFirewall:
    def __init__(self, connection_limit=100, is_active=True):
        self.blocked_ips: set = set()  # IPs effectivement bloquées au niveau iptables (best-effort)
        self.rate_limited_ips: set = set()  # IPs au-dessus du seuil, décision en mémoire (toujours fiable)
        self.ip_connections: dict = {}
        self.connection_limit: int = connection_limit
        self.is_active: bool = is_active

    def add_connection(self, ip_address) -> bool:
        """Compte les connexions pour une adresse IP. Retourne False si la connexion doit être
        rejetée (IP au-dessus du seuil), True si elle peut être acceptée."""
        if not self.is_active:
            return True

        if ip_address in self.rate_limited_ips:
            return False

        self.ip_connections[ip_address] = self.ip_connections.get(ip_address, 0) + 1

        if self.ip_connections[ip_address] > self.connection_limit:
            self.rate_limited_ips.add(ip_address)
            print(f"Adresse IP {ip_address} a dépassé la limite de connexion et est maintenant bloquée.")
            # Best-effort : tente aussi un blocage au niveau OS (iptables). Si indisponible
            # (ex: conteneur sans privilèges), le rejet en mémoire ci-dessus reste effectif.
            self.block_ip(ip_address)
            return False

        return True

    def is_blocked(self, ip_address) -> bool:
        return ip_address in self.rate_limited_ips or ip_address in self.blocked_ips

    def block_ip(self, ip_address):
        """Bloque une adresse IP en utilisant iptables."""
        if ip_address not in self.blocked_ips:
            cmd = ["sudo", "iptables", "-A", "INPUT", "-s", ip_address, "-j", "DROP"]
            try:
                subprocess.run(cmd, check=True)
                self.blocked_ips.add(ip_address)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Erreur lors du blocage iptables de l'adresse IP {ip_address} (rejet en mémoire toujours actif): {e}")

    def unblock_ip(self, ip_address):
        """Débloque une adresse IP précédemment bloquée."""
        self.rate_limited_ips.discard(ip_address)
        if ip_address in self.ip_connections:
            del self.ip_connections[ip_address]
        if ip_address in self.blocked_ips:
            cmd = ["sudo", "iptables", "-D", "INPUT", "-s", ip_address, "-j", "DROP"]
            try:
                subprocess.run(cmd, check=True)
                self.blocked_ips.remove(ip_address)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Erreur lors du déblocage iptables de l'adresse IP {ip_address}: {e}")

    def list_blocked_ips(self):
        """Affiche la liste des adresses IP actuellement bloquées."""
        print("Adresses IP bloquées :")
        for ip in self.blocked_ips:
            print(ip)

