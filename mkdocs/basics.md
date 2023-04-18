The Cheshire Cat is composed of two main parts: the core functionality resides in the `/core` folder, and the frontend interface is located in the `/admin` folder. This document will provide an overview of The Cheshire Cat, including its basic functions and how to access them.

## :anatomical_heart: The Cat Core

The core functionalities of The Cheshire Cat resides in the `/core` folder. The core exposes all of its APIs via the address `localhost:1865/`.
The program has several endpoints that can be accessed via this address. All of these endpoints are thoroughly documented and can be easily tested using Swagger (available at `localhost:1865/docs`) or ReDoc (available at `localhost:1865/redoc`).

Examples of some of these endpoints include:

- `/` - This endpoint will return the message `"We're all mad here, dear!"` if the cat is functioning properly.
- `/ws/` - Use this endpoint to start a chat with the cat using a websocket.
- `/rabbithole/` - This endpoint allows you to send a file (text, markdown or pdf) to the cat, which will then be saved into its memory. This allows you to share information directly with the cat and for it to access it whenever needed.
   
Interacting with Rabbithole:

=== "Python"
    ```python
    import requests
    
    url = 'http://localhost:1865/rabbithole/'
    
    with open('alice.txt', 'rb') as f:
        files = {
            'file': ('alice.txt', f, 'text/plain')
        }
    
        headers = {
            'accept': 'application/json',
        }
    
        response = requests.post(url, headers=headers, files=files)
    
    print(response.text)
    ```
=== "Node"
    ```javascript
    const request = require('request');
    const fs = require('fs');
    
    const url = 'http://localhost:1865/rabbithole/';
    
    const file = fs.createReadStream('alice.txt');
    const formData = {
      file: {
        value: file,
        options: {
          filename: 'alice.txt',
          contentType: 'text/plain'
        }
      }
    };
    
    const options = {
      url: url,
      headers: {
        'accept': 'application/json'
      },
      formData: formData
    };
    
    request.post(options, function(err, res, body) {
      if (err) {
        return console.error('Error:', err);
      }
      console.log('Body:', body);
    });
    ```

## :yarn: The Admin Interface

The frontend interface of The Cheshire Cat is located in the `admin` folder and can be accessed via `localhost:3000`. This interface provides users with an easy-to-use chat that act as playground and can be used to interact with your application.   
   
All the cat's settings are available under this GUI's `Settings` menu.