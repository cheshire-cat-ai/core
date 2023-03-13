# 🐱 Cheshire-Cat (Stregatto)
Customizable AI architecture

![Wikipedia picture of the Cheshire Cat](cheshire-cat.jpeg)

```
"Would you tell me, please, which way I ought to go from here?"
"That depends a good deal on where you want to get to," said the Cat.
"I don't much care where--" said Alice.
"Then it doesn't matter which way you go," said the Cat.

(Alice's Adventures in Wonderland - Lewis Carroll)
```

## Quickstart

You just need `docker` and `docker-compose` installed on your system.

Clone the repo and cd into it. Create a `.env` file containing:

```OPENAI_KEY=<your-openai-key>```

After that you can run:

```docker-compose up```

The first time (only) it will take several minutes, as the images occupy a few GBs.

Interact with the Cheshire Cat on `localhost:3000`

When you finish, remember to CTRL+c in the terminal and `docker-compose down`.


## Development

This is a new and fast changing project.
If you want the latest version, we recommend to start each session by updating the code:

```git pull origin main```

If any `Dockerfile` or `docker-compose.yml` file has changed, rebuild the images from scratch (will take a while):

```docker-compose build --no-cache```

Then you can start hacking:

```docker-compose up```

From time to time remember to delete pending, unused images:

```docker rmi -f $(docker images -f "dangling=true" -q)```