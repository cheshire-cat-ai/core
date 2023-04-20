# Changelog

## 0.0.1 ( 2023-04-20 )

### Enhancements

* Markdown support in admin
* Bump python version to 3.10 (remember to `docker-compose build --no-cache` after pull)
* Add host and port configuration via `.env`, please see `.env.example` as it is now necessary to declare default hosts and ports
* Update license to GPLv3
* Plugins list available in the admin
* endpoint `rabbithole/web` to ingest an URL, scrape it and store to memory
* Chat notification when finished uploading a file (sorta)
* Take back Qdrant as vector DB instead of FAISS, as FAISS does not allow metadata aware search
* Refactor CheshireCat class in smaller classes
