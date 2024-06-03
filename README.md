# Django chat app

A simple chat app in Django using channels.

## Installation / build

```
docker-compose up -d --build
```

## After first build you can just do

```
docker-compose up
```

## Running tests

```
docker-compose run --rm test
```

## And to remove the containers

```
docker-compose down -v
```

## Usage
Open an incognito window and go to `http://localhost:8000` and create a new user.

Then, open another incognito window and go to `http://localhost:8000` and create another user.

Now, you can chat between these two (or more) users.

## Logs
For the logs, we have to use the `docker-compose logs -f` command, and we can see the logs of the `web` and `worker` services.
And we can see the logs of the `redis` and `postgres` services as well.
They will be stored locally in the root directory as well.