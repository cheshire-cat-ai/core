# :card_file_box: Folders & API

The Cheshire Cat is composed of two main parts: the core functionality resides in the `/core` folder, and the frontend interface is located in the `/admin` folder. This document will provide an overview of The Cheshire Cat, including its basic functions and how to access them.

## :anatomical_heart: The Cat Core

The core functionalities of The Cheshire Cat resides in the `/core` folder. The core exposes all of its APIs via the address `localhost:1865/`.
The program has several endpoints that can be accessed via this address. All of these endpoints are thoroughly documented and can be easily tested using Swagger (available at `localhost:1865/docs`) or ReDoc (available at `localhost:1865/redoc`).

Some of these endpoints include:

- `/` - This endpoint will return the message `"We're all mad here, dear!"` if the cat is functioning properly.
- `/ws/` - Use this endpoint to start a chat with the cat using a websocket.
- `/rabbithole/` - This endpoint allows you to send a file (text, markdown or pdf) to the cat, which will then be saved into its memory. This allows you to share information directly with the cat and for it to access it whenever needed.

## :yarn: The Admin Interface

The frontend interface of The Cheshire Cat is located in the `admin` folder and can be accessed via `localhost:3000`. This interface provides users with an easy-to-use chat that act as playground and can be used to interact with your application.   
   
All the cat's settings are available under this GUI's `Settings` menu.