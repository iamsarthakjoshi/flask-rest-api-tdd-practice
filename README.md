# Flask Rest API Boilerplate

Example of Flask REST-API.

## Some extensions and their usage

- `Flask-SQLAlchemy`: Helper extension to operate SQLAlchemy features. Mainly for database operation.
- `Flask-Socketio`: An implmentation of WebSockets to push/send events (data) with open connection.
- `Flask-Mail`: Mail extension to send emails.
- `redis`: Redis client is used mainly for `rq` extension that handles asynchronous tasks.
- `rq`: RQ (Redis Queue) is a simple Python library for queueing jobs and processing them in the background with workers. It is backed by Redis and it is designed to have a low barrier to entry. - [rq](https://python-rq.org/)
- `pytest`: An extension to implement function and unit tests.
- `stripe`: For Third-Party payment integration.

## Installation and Configuration Installation and Configuration

- Python Specific
  - Create a new Python 3.6 (3.6.5) virtual environment called `venv` in the backend root folder
    - `python3 -m venv venv`
  - Activate the virtual environment
    - `source venv/bin/activate`
  - Run `pip install -r requirements` to install the necessary requirements
- Database
  - Install MySQL on your machine
  - Modify the `.env` file/s to have the correct username, password and database names that you have setup and want to use for this project and ALSO, update the DB connection strings (this is mandatory)
  - To create a DB migration (Run ONLY for Non-docker setup, docker setup auto does this from entrypoint files)
    - Run this command in the root directory to:
      - set migration commit message `alembic revision -m "Message about your commit"`
      - migrate `alembic upgrade head`

## Installation and Configuration Running the app

- Startup your MySQL/Postgres Database
- Run `application.py` (For Non-docker scenario)
- For Docker setup, just run `docker-compose up -f '<docker-file-name>.yml' up --build -d`
- Test that its working by opening the following url in your browser and confirming that the message is `pong`: http://localhost:7970/api/ping

## Running Tests

- Running command `pytest` will run both integration test and unit tests
- Note: Every Tests are not included. (in-progress)
- `TODO`: Adding other tests, test coverage and more.

## REDIS - RQ-WORKER (For Local-Development)

- To make Redis and Rq-Worker work in local setup, you must run redis and rq-workers in your local machine. This is because worker is an instance of the entire application and running worker locally with redis running in docker container creates a complexcity\* where you want to avoid it.
  - Complexcity: You need to create a communication between docker and localhost because docker continer does not have direct access to host machine. To make this work, follow one of these instructions:
    - https://stackoverflow.com/questions/24319662/from-inside-of-a-docker-container-how-do-i-connect-to-the-localhost-of-the-mach##:~:text=Use%20%2D%2Dnetwork%3D%22host%22,for%20Linux%2C%20per%20the%20documentation.
    - https://github.com/qoomon/docker-host

## General Practices / Information

- Every new endpoint should call the `access_verifier`, see example of the heartbeat endpoint for more information
- Database migrations should be defined by using Flask_Migrate
- Add to the `.gitignore` any files you may have which are specific to your machine OR contain secret information (such as API keys etc)
- Add application level configuration settings to config.py
- Add system level, secret or api keys, credentials, configuration settings to .env files
- Remember to not include any production specific information in `config.py` settinfgs, these should be configured later when deployments are implemented

## PDF Generator

- There are two implementation for generating PDF files.
  - One with ReportLab library which does not need any extra setup.
  - Second is with PDFKIT library. It is installed along with other requirement.
    - It has a dependency package called 'wkhtmltox'. You have to install "wkhtmltox" package on the host/server machine. Only then pdfkit is able to generate PDF file from HTML template files.
    - Some time on the host/server we might get an issue wkhtmltopdf: cannot connect to X server.
      - This is because of the standard installation of wkhtmltopdf, requires a xserver. To resolve the issue please follow the link: `https://micropyramid.com/blog/how-to-create-pdf-files-in-python-using-pdfkit/`
