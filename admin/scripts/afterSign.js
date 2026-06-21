const { execSync } = require('child_process');
const path = require('path');

// Pas de certificat Developer ID disponible sur cette machine : electron-builder
// produit donc un .app totalement non signé. Sur Apple Silicon, macOS exige une
// signature (même ad-hoc) pour tout binaire exécuté — sans ça, Gatekeeper affiche
// "... est endommagée et ne peut pas être ouverte" au lieu du message habituel
// "développeur non identifié". Une signature ad-hoc (`-`) suffit à éviter ce message
// et fait retomber sur le flux classique "clic droit > Ouvrir" déjà documenté sur la
// page de téléchargement.
module.exports = async function (context) {
    const appPath = path.join(context.appOutDir, `${context.packager.appInfo.productFilename}.app`);
    execSync(`codesign --force --deep --sign - "${appPath}"`, {stdio: 'inherit'});
};
