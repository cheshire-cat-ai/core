# :anatomical_heart: The Cat Core

The core exposes all of its APIs via the address `localhost:1865/`.

A full documentation with Swagger is inside the Cat itself and can be reached at `localhost:1865/docs`.

| Endpoint           | Method      | Description                                                                         |
|--------------------|:------------|:------------------------------------------------------------------------------------|
| ___/___            | `GET`       | :handshake: Return the message `"We're all mad here, dear!"` if the cat is running. |
| ___/ws/___         | `WEBSOCKET` | :speech_balloon: Start a chat with the cat using websockets.                        |
| ___/rabbithole/___ | `POST`      | :rabbit: Send a file (`.txt`, `.md` or `.pdf`) to the cat.                          |


## :speech_balloon: Interacting with the Cat

Example of how to implement a simple chat system using the websocket endpoint at `localhost:1865/ws/`.
!!! info "Request JSON schema"
    Sending input will request you to do it in the following specific JSON format `{"text": "input message here"}`.

!!! example

    === "Python"
        ```python
        import asyncio
        import websockets
        import json

        async def cat_chat():

            try:
                # Creating a websocket connection
                async with websockets.connect('ws://localhost:1865/ws') as websocket:

                    # Running a continuous loop until broken
                    while True:

                        # Taking user input and sending it through the websocket
                        user_input = input("Human: ")
                        await websocket.send(json.dumps({"text": user_input}))

                        # Receiving and printing the cat's response
                        cat_response = await websocket.recv()
                        print("Cheshire Cat:", cat_response)

            except websockets.exceptions.InvalidURI:
                print("Invalid URI provided. Please provide a valid URI.")

            except websockets.exceptions.InvalidStatusCode:
                print("Invalid status code received. Please check your connection.")

            except websockets.exceptions.WebSocketProtocolError:
                print("Websocket protocol error occurred. Please check your connection.")

            except websockets.exceptions.ConnectionClosedOK:
                print("Connection successfully closed.")

            except Exception as e:
                print("An error occurred:", e)

        # Running the function until completion
        asyncio.get_event_loop().run_until_complete(cat_chat())
        ```
    === "Node"
        ```javascript
        const WebSocket = require('ws');

        async function cat_chat() {

          try {
            const socket = new WebSocket('ws://localhost:1865/ws/');

            //Listen for connection event and log a message
            socket.on('open', () => {
              console.log('Connected to the Ceshire Cat');
            });

            //Listen for message event and log the received data message
            socket.on('message', (data) => {
              console.log(`Cheshire Cat: ${data}`);
            });

            //Iterate indefinitely while waiting for user input
            while (true) {
              //Call getUserInput function and wait for user input
              const user_input = await getUserInput('Human: ');

              socket.send(user_input);
            }

          } catch (error) {
            console.error(error);
          }
        }

        //Define a function named getUserInput that returns a Promise
        function getUserInput(prompt) {
          return new Promise((resolve) => {
            const stdin = process.openStdin();
            process.stdout.write(prompt);

            //Listen for data input events and resolve the Promise with the input
            stdin.addListener('data', (data) => {
              resolve(data.toString().trim());
              stdin.removeAllListeners('data');
            });
          });
        }

        //Call the cat_chat function
        cat_chat();
        ```

## :rabbit: Interacting with Rabbithole

Example of how to send a text file (`.md`,`.pdf.`,`.txt`) to the Cat using the Rabbit Hole at `localhost:1865/rabbithole/`.

Currently the following MIME types are supported:
* `text/plain`
* `text/markdown`
* `application/pdf`

!!! example

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
    === "cURL"
        ```
        # Upload an ASCII text file
        curl -v -X POST -H "accept: application/json" -F "file=@file.txt;type=text/plain" http://127.0.0.1:1865/rabbithole/

        # Upload a Markdown file
        curl -v -X POST -H "accept: application/json" -F "file=@file.md;type=text/markdown" http://127.0.0.1:1865/rabbithole/

        # Upload a PDF file
        curl -v -X POST -H "accept: application/json" -F "file=@myfile.pdf;type=application/pdf" http://127.0.0.1:1865/rabbithole/
        ```
