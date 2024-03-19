import requests


class PageMirror:
    def __init__(self, url: str, o='index.html') -> None:
        self.url = url
        self._output = o

    def clone(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                contenu_page = response.text
                with open(f'src/protocol/web/cache/{self._output}', 'a+', encoding='utf-8') as f:
                    f.write(contenu_page)
                print("page_mirror> successfully cloned!")
            else:
                print("La requête a échoué avec le code d'état :", response.status_code)
                return None
        except Exception as e:
            print("Une erreur s'est produite lors de la récupération de la page :", e)
            return None
