import socket
import dns.resolver
import requests


def nslookup_with_geolocation(ip):
    results = {}

    # Résolution inverse pour obtenir le nom d'hôte
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        results['Hostname'] = hostname
    except socket.herror:
        results['Hostname'] = 'Inconnu'

    # Obtenir les enregistrements DNS
    # ... (même code que précédemment pour les enregistrements DNS) ...

    # Obtenir des informations de géolocalisation
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}')
        geo_data = response.json()
        if geo_data['status'] == 'success':
            results['country'] = geo_data['country']
            results['region'] = geo_data['regionName']
            results['city'] = geo_data['city']
            results['zip'] = geo_data['zip']
            results['isp'] = geo_data['isp']
        else:
            results['location'] = 'information unavailable'
    except requests.RequestException:
        results['location'] = 'error when retrieving data for location'

    return results
