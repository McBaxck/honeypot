from src.hp import HolyPot
from src.config import *
import logging.config

logging.config.dictConfig(GLOBAL_LOGGING_CONFIG)


if __name__ == "__main__":
    hp_set: HolyPotConfig = HolyPotConfig()
    hp_set.ports = [8080, 8081, 8082]

    server: HolyPot = HolyPot(
        holypot_config=hp_set
    )
    server.add_service(on_ports=[8825], service='ssh')
    server.add_service(on_ports=[9999], service='http')
    server.add_service(on_ports=[9924], service='smtp')
    server.add_service(on_ports=[9925], service='telnet')
    server.add_service(on_ports=[9926], service='ftp')
    server.run()
