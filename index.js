import Deso from 'deso-protocol';
const deso = new Deso();
const response = await deso.identity.login('3');
console.log(response);
