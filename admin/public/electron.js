const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
    const win = new BrowserWindow({
        width: 1000,
        height: 600,
        backgroundColor: '#fff',
        webPreferences: {
            nodeIntegration: true,
        },
        frame: false,
        roundedCorners: true,
    });

    // En dev (npm start), ELECTRON_START_URL pointe vers le serveur CRA (hot-reload).
    // En usage desktop autonome, on charge le build de production déjà généré — pas
    // besoin de Docker/nginx pour faire tourner l'app. Ce fichier vit à deux endroits
    // selon le contexte : dans public/ (source, copié tel quel par CRA) quand on lance
    // `electron .` directement sans empaqueter, et à la racine de l'asar une fois
    // empaqueté par electron-builder (où index.html est juste à côté, plus dans build/).
    if (process.env.ELECTRON_START_URL) {
        win.loadURL(process.env.ELECTRON_START_URL)
            .catch(err => console.error(err));
    } else {
        const indexPath = app.isPackaged
            ? path.join(__dirname, 'index.html')
            : path.join(__dirname, '..', 'build', 'index.html');
        win.loadFile(indexPath)
            .catch(err => console.error(err));
    }
}

app.whenReady().then(createWindow);
