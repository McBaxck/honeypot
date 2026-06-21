export function addItemToLocalStorage(key, value) {
    if (typeof value === "object") {
        value = JSON.stringify(value);
    }
    localStorage.setItem(key, value);
}

export function getItemFromLocalStorage(key) {
    let value = localStorage.getItem(key);
    try {
        value = JSON.parse(value);
    } catch (e) {
        // Si ce n'est pas un JSON valide, retourner la valeur telle quelle
    }
    return value;
}


export function removeItemFromLocalStorage(key) {
    localStorage.removeItem(key);
}


export function clearLocalStorage() {
    localStorage.clear();
}

export function updateItemInLocalStorage(key, updateCallback) {
    let currentValue = localStorage.getItem(key);
    try {
        currentValue = JSON.parse(currentValue);
    } catch (e) {
        // Si ce n'est pas un JSON valide, laisser la valeur telle quelle
    }
    const newValue = updateCallback(currentValue);
    if (typeof newValue === "object") {
        localStorage.setItem(key, JSON.stringify(newValue));
    } else {
        localStorage.setItem(key, newValue);
    }
}

