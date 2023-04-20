# :cat2: Advanced
## :closed_lock_with_key: API Authentication

In order to authenticate endpoints, it is necessary to include the `API_KEY=your-key-here` variable in the `.env` file. Multiple keys can be accepted by separating them with a pipe (`|`) as follows: `API_KEY=your-key-here|secondary_client_key`.

After configuration, all endpoints will require an `access_token` header for authentication, such as `access_token: your-key-here`. Failure to provide the correct access token will result in a 403 error.

!!! warning

    This kind of athentication is weak and it's intended for machine to machine communication, please do not rely on it and enforce other kind of stronger authentication such as OAuth2 for the client side.
 
!!! example
    **Authenticated API call:**
    === "Python"
        ```python
        import requests
        
        server_url = 'http://localhost:1865/'
        api_key = 'your-key-here'
        access_token = {'access_token': api_key}
        
        response = requests.get(server_url, headers=access_token)
        
        if response.status_code == 200:
            print(response.text)
        else:
            print('Error occurred: {}'.format(response.status_code))
        ```
    === "Node"
        ```javascript
        const request = require('request');
        
        const serverUrl = 'http://localhost:1865/';
        const apiKey = 'your-key-here';
        const access_token = {'access_token': apiKey};
        
        request({url: serverUrl, headers: access_token}, (error, response, body) => {
            if (error) {
                console.error(error);
            } else {
                if (response.statusCode === 200) {
                    console.log(body);
                } else {
                    console.error(`Error occurred: ${response.statusCode}`);
                }
            }
        });
        ```   
   
By adding the variable to the `.env` file, all Swagger endpoints (`localhost:1865/docs`) will require authentication and can be accessed on the top right-hand corner of the page through the green **Authorize** button.   
  