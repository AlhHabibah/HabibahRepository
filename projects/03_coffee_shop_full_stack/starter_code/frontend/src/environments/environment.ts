/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'fsnd-habibah.us', // the auth0 domain prefix
    audience: 'Coffee-Shop', // the audience set for the auth0 app
    clientId: 'TyW3HeImMOfVn54oolbBbpzEfkH4iNjK', // the client id generated for the auth0 app
    callbackURL: 'https://localhost:4200/login-results', // the base url of the running ionic application. 
  }
};
