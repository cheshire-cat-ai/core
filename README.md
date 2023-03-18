# 🐱 Cheshire-Cat (Stregatto)

<p align="center">

<img src=cheshire-cat.jpeg width=240px alt="Wikipedia picture of the Cheshire Cat">

</p>



## About The Project

The Cheshire Cat AI (Stregatto) can leverage many different language models, according to your taste. It's an open source layer on top of the most used language models. It features a long term memory and a plugin system so you can extend it.


## Getting started

### Requirements

- Docker installed
- .env file containing secrets


### Installation

In order to use Cheshire Cat AI you need to clone the repository from github and run it using docker-compose. Use git clone to get the repo:

```bash
git clone --branch vLATEST https://github.com/pieroit/cheshire-cat.git
cd cheshire-cat
# Before to run docker-compose up command you have to create a .env file containing secrets, more details on Secrets file section
docker-compose up
```

### Secrets file

To execute Cheshire Cat AI you should provide a **.env** file containing the required secrets variables, that are:

```bash
OPENAI_KEY="YOUR_OPEN_AI_KEY"
```

## Usage

Once you created the .env file and executed `docker-compose up`  you will find the UI available at `http://localhost`.


## Roadmap

- [ ] Add models support



## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 


## Contributors

[![](https://github.com/pieroit.png?size=50)](https://github.com/pieroit)
[![](https://github.com/antonioru.png?size=50)](https://github.com/antonioru)
[![](https://github.com/peppicus.png?size=50)](https://github.com/peppicus)
[![](https://github.com/umbertogriffo.png?size=50)](https://github.com/umbertogriffo)
[![](https://github.com/samirsalman.png?size=50)](https://github.com/samirsalman)


