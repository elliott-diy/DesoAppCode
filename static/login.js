function login() {
    const h = 1000;
    const w = 800;
    const y = window.outerHeight / 2 + window.screenY - h / 2;
    const x = window.outerWidth / 2 + window.screenX - w / 2;
    identityWindow = window.open(
        "https://identity.deso.org/log-in?accessLevelRequest=2",
        null,
        `toolbar=no, width=${w}, height=${h}, top=${y}, left=${x}`
    );
}

function postMessage(req) {
    if (initialized) {
        iframe.contentWindow.postMessage(req, "*");
    } else {
        pendingRequests.push(req);
    }
}

function respond(window, id, payload) {
    window.postMessage({ id, service: "identity", payload }, "*");
}

function handleRequest(event) {
    const { data: { method, payload } } = event;
    if (method === "initialize") {
        handleInitialize(event);
    } else if (method === "login") {
        handleLogin(payload);
    }
}

function handleInitialize(event) {
    if (!initialized) {
        initialized = true;
        iframe = document.getElementById("identity");
        for (const request of pendingRequests) {
            postMessage(request);
        }
        pendingRequests = [];
    }
    // Acknowledge, provides hostname data
    respond(event.source, event.data.id, {});
}

function handleLogin(payload) {
    identityWindow.close();
    identityWindow = null;

    console.log(payload.publicKeyAdded);
    console.log(payload.users[payload.publicKeyAdded].encryptedSeedHex);
    // globals.identityWindowSubject.next(payload);
    // globals.identityWindowSubject.complete();
    // globals.identityWindowSubject = null;
}

var initialized = false;
var iframe = null;
var pendingRequests = [];
var identityWindow = null;

window.addEventListener("message", (event) => handleRequest(event));
login()
