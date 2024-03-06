from src.hp import HolyPot
from src.config import *

if __name__ == "__main__":
    hp_set: HolyPotConfig = HolyPotConfig()
    hp_set.ports = [8080, 8081, 8082]

    server: HolyPot = HolyPot(
        holypot_config=hp_set
    )
    server.add_service(on_ports=[8825], service='ssh')
    server.add_service(on_ports=[9999], service='http')
    server.run()
