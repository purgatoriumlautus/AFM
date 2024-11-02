
# The Austrian Flood Monitoring (AFM)

The Austrian Flood Monitoring (AFM) system is a web-based platform that aims to support emergency response organisations in their work. The platform provides ways to monitor, organise and coordinate the response to flood-related incidents. AFM offers an interactive map of current, along with historical water level information. Additionally, AFM provides registered users with an interface for submitting detailed emergency reports that enhance the response actions of emergency services. 


## Run Locally

Clone the project

```bash
  git clone https://link-to-project
```

Go to the project directory

```bash
  cd my-project
```

Create virtual environment
```bash
  py -m venv venv
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  flask run
```

To set up the database

```bash
  flask shell
  from src.db import db
  db.create_all()
```
