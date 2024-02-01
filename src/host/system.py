DEFAULT_USER: str = 'john'


class FHS:
    def __init__(self):
        self.root = {
            'home': {
                DEFAULT_USER: {
                    'Documents': {},
                    'Downloads': {},
                    'Desktop': {},
                    'Images': {},
                    'Musics': {},
                    'Videos': {},
                }
            },
            'usr': {
                'bin': {},
                'lib': {},
            },
            'var': {
                'log': {},
            }
        }
        self.current_dir = self.root
        self.current_path = '/'

    def show(self, dossier, prefix=''):
        for nom, content in dossier.items():
            print(prefix + nom)
            if isinstance(content, dict):
                self.show(content, prefix + '    ')

    def cd(self, path):
        path_elements = path.split('/')
        target_dir = self.root
        for element in path_elements:
            if element == '..':
                target_dir = self.current_dir
                continue
            if element and element in target_dir:
                target_dir = target_dir[element]
            else:
                print(f"cd: aucun fichier ou dossier de ce type: {path}")
                return
        self.current_dir = target_dir
        self.current_path = path

    def ls(self):
        for name in self.current_dir:
            print(name)

    def nano(self, filename):
        if filename in self.current_dir:
            print(f"Ouverture de {filename} pour édition...")
        else:
            print(f"Création de {filename}...")
            self.current_dir[filename] = None  # Ajouter un fichier fictif

    def pwd(self):
        print(self.current_path)


if __name__ == "__main__":
    faux_fs = FHS()
    faux_fs.pwd()
    faux_fs.ls()
    faux_fs.cd('home/thon/Documents')
    faux_fs.pwd()
    faux_fs.ls()
    faux_fs.nano('rapport.txt')
    faux_fs.ls()
