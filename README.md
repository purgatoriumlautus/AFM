
# The Austrian Flood Monitoring (AFM)

The Austrian Flood Monitoring (AFM) system is a web-based platform that aims to support emergency response organisations in their work. The platform provides ways to monitor, organise and coordinate the response to flood-related incidents. AFM offers an interactive map of current, along with historical water level information. Additionally, AFM provides registered users with an interface for submitting detailed emergency reports that enhance the response actions of emergency services. 

## TO RUN THE SERVER YOU NEED TO HAVE DOCKER INSTALLED ON YOUR LOCAL MACHINE
## Run Locally

Clone the project

```bash
  git clone https://link-to-project
```

Go to the project directory

```bash
  cd my-project
```

Create docker image and container
```bash
  docker compose build
```

Initialize the compose
```bash
-d tag unlinks the output of the containers consoles, if you want to see them remove the -d tag 
```
```bash
  docker compose up -d
```

After this the container for the server, db and db adminer has already started.
But the DB is not populated. To populate the db run the src/imitialize_db.py script

## Steps:
Get into application container bash
```bash
  docker compose run app bash
```

Run the script
```bash
python src/initiate_db.py
```

Exit the container
```bash
exit
```

Now the server and db is set up.

## http://localhost:5000 - server
## http://localhost:8080 - db adminer

To log in into db adminer use
```bash
server:db
username: user
password: secret
db: postgres
```

To stop the server
```bash
docker compose down
```


