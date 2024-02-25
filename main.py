from hp import HoneyPot
from src.config import *
from src.host import nslookup_with_geolocation


if __name__ == "__main__":
    hp_set: HolyPotConfig = HolyPotConfig()
    hp_set.ports = [8080, 8081, 8082]
    host_set: HostConfig = HostConfig()
    server: HoneyPot = HoneyPot(
        holypot_config=hp_set
    )
    # server.add_interactive_shell(on_ports=[8825], mode='ssh')
    # server.add_interactive_shell(on_ports=[9999], mode='http')
    server.run()
