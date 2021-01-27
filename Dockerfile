FROM python:3.6-slim-buster

WORKDIR /usr/src/app

# Add requirements.txt before rest of repo for caching
COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

# This prevents loading backend before database service
COPY wait-for-it.sh /usr/src/app/wait-for-it.sh
RUN chmod +x wait-for-it.sh
RUN chmod +x /usr/src/app/wait-for-it.sh

# For running alembic db migrations + gunicorn
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# EXPOSE 7970 # exposed in docker-compose file

# Only use --wokers 1 if you're using socket.io
# CMD gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:7970 application:app # in docker-compose file