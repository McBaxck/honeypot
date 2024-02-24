import redis
from src.config import PORT, HOST


class RedisCache:
    def __init__(self, host='localhost', port=PORT.REDIS, db=0):
        self.r = redis.Redis(host=host, port=port, db=db)

    def set_value(self, key, value, expire=None):
        """
        Stocke une valeur dans le cache.

        :param key: La clé sous laquelle stocker la valeur.
        :param value: La valeur à stocker.
        :param expire: Le délai d'expiration en secondes. Si None, la clé n'expire pas.
        """
        self.r.set(key, value, ex=expire)

    def get_value(self, key):
        """
        Récupère une valeur du cache.

        :param key: La clé de la valeur à récupérer.
        :return: La valeur stockée ou None si la clé n'existe pas.
        """
        return self.r.get(key)

    def delete_key(self, key):
        """
        Supprime une clé (et sa valeur associée) du cache.

        :param key: La clé à supprimer.
        """
        self.r.delete(key)

    def flush_all(self):
        """
        Supprime toutes les clés du cache.
        """
        self.r.flushall()


# Exemple d'utilisation
if __name__ == "__main__":
    cache = RedisCache()

    # Mise en cache d'une valeur
    cache.set_value('test_key', 'Hello, Redis!', expire=10)

    # Récupération d'une valeur
    print(cache.get_value('test_key'))

    # Suppression d'une clé
    cache.delete_key('test_key')

    # Vider le cache
    cache.flush_all()