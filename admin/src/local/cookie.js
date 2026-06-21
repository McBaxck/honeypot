import Cookies from 'js-cookie';

// js-cookie ne pose par défaut que des cookies de session (effacés à la fermeture du
// navigateur/de l'app Electron) : sans `expires` explicite, la connexion ne survivait
// jamais à un redémarrage. 30 jours par défaut, surchargeable au cas par cas via options.
const DEFAULT_EXPIRES_DAYS = 30;

export function addCookie(name, value, options = {}) {
    if (typeof value === "object") {
        value = JSON.stringify(value);
    }
    Cookies.set(name, value, {expires: DEFAULT_EXPIRES_DAYS, ...options});
}


export function getCookie(name) {
    let value = Cookies.get(name);
    try {
        value = JSON.parse(value);
    } catch (e) {
        // Si ce n'est pas un JSON valide, retourner la valeur telle quelle
    }
    return value;
}

export function removeCookie(name, options = {}) {
    Cookies.remove(name, options);
}