# Django chat app

![image](https://github.com/vitorrcunhaa/django-chat/assets/21017817/a084482d-da7d-4e7d-aec1-662cea0c8ba9)


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

## Other screenshots with 2 users using at the same time:
![image](https://github.com/vitorrcunhaa/django-chat/assets/21017817/756394e8-6e81-493a-8fe6-fc8e687f60c4)

## User leaves the room:
![image](https://github.com/vitorrcunhaa/django-chat/assets/21017817/c232c52e-97cf-4c0d-81ab-db4419acbff4)

