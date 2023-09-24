# accuknox

## Docker setup -

[Docker install instructions](https://docs.docker.com/engine/install/)

Start the project by running - 

```
docker compose up
```

This will create the following services 
* db - Postgres DB to store data
* backend - Django server, this server is connected to Postgres database

Application can be accessed on port 8000 after setup - 
(Please wait for all the services to be up before trying to hit the API and please note that no other existing services should be running on port 8000)

Note - Migrate command will be run by default whenever the project is setup (Included in the startup command)
```
python3 manage.py migrate
```

To run any other command inside a container, Ex -
```
docker ps
docker exec -it container_name sh
pipenv shell
python3 manage.py createsuperuser
```

API signature is shared in a Postman collection - **Social Network.postman_collection.json** 
When using the Postman collection - BASE_URL needs to be configured - for ex - http://127.0.0.1:8000/
