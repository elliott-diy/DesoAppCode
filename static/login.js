function login(accessLevel = 2) {
    const h = 1000;
    const w = 800;
    const y = window.outerHeight / 2 + window.screenY - h / 2;
    const x = window.outerWidth / 2 + window.screenX - w / 2;
    identityWindow = window.open(
        `https://identity.deso.org/log-in?accessLevelRequest=${accessLevel}`,
        null,
        `toolbar=no, width=${w}, height=${h}, top=${y}, left=${x}`
    );
}
