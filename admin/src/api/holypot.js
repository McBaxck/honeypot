const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5050/holypot-api/v1'

export function getHolypotGlobalLogs() {
    return fetch(`${BASE_URL}/logs`);
}

export function getSrvLogs(service){
    return fetch(`${BASE_URL}/service/logs`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({"service": service}),
})}

export function testConnection(ip){
    return fetch(`http://${ip}:5000/holypot-api/v1/status/ip/${ip}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
})}

export function signInHP(hp){
    return fetch(`${BASE_URL}/signin`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(hp)
    })}

export function saveNetworkConf(data){
    return fetch(`${BASE_URL}/network/conf`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })}

export function registerHP(hp){
    return fetch(`${BASE_URL}/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(hp)
    })}

export function getStatusInfo(){
    return fetch(`${BASE_URL}/host`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })}

export function getAccountData(username){
    return fetch(`${BASE_URL}/account/${username}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })}

export function getNetworkConf(honeypot_id){
    return fetch(`${BASE_URL}/network/conf/${honeypot_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })}

export function getHoneypotState(honeypot_id){
    return fetch(`${BASE_URL}/status/${honeypot_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })}

export function setHoneypotState(data){
    return fetch(`${BASE_URL}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })}

export function addTimeOutToPromise(promise, timeoutMs) {
    let timeoutHandle;
    const timeoutPromise = new Promise((resolve, reject) => {
        timeoutHandle = setTimeout(() => reject(new Error('Operation timed out')), timeoutMs);
    });

    return Promise.race([promise, timeoutPromise]).then((result) => {
        clearTimeout(timeoutHandle);
        return result;
    }, (error) => {
        clearTimeout(timeoutHandle);
        throw error;
    });
}

export function postModuleConfiguration(configuration){
    return fetch(`${BASE_URL}/service/configuration`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(configuration),
    });
}

// --- Ajouts : ces endpoints reflètent le vrai honeypot (toujours actif, service
// d'infrastructure indépendant), pas une instance pilotée à distance comme avant. ---

export function getStats(){
    return fetch(`${BASE_URL}/stats`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })}

export function streamLogsUrl(){
    return `${BASE_URL}/stream/logs`
}

export function getSshLogs(){
    return fetch(`${BASE_URL}/logs/ssh`)
}

export function getHttpLogs(){
    return fetch(`${BASE_URL}/logs/http`)
}

export function getTelnetLogs(){
    return fetch(`${BASE_URL}/logs/telnet`)
}

export function getFtpLogs(){
    return fetch(`${BASE_URL}/logs/ftp`)
}

export function getBlockedIps(){
    return fetch(`${BASE_URL}/firewall/blocked`)
}

export function blockIp(ip, reason){
    return fetch(`${BASE_URL}/firewall/block`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ip, reason}),
    })}

export function unblockIp(ip){
    return fetch(`${BASE_URL}/firewall/unblock`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ip}),
    })}
