#!/usr/bin/env bash

############################### Legacy Database Init+Migration ##############################
# Run this only if you need to save certain migration or to run that migration
# if you do not wish to run this on next run, then remember to clean alembic version id from db 
# or just delete alembic table.
# alembic revision -m "baseline" 

# Create tables
# alembic upgrade head
###############################################################################################

# Database Init+Migration
python manage.py migrate_db

# For Dev, Local and Test
# python3 application.py

# For Production
# `--reload` will enable debug mode in Prod.
# `--log-file=-`` will create the log file
# `--error-logfile gunicorn.error.log` will specify error log file
# `--access-logfile gunicorn.log` will specify access/requests log file
# `--capture-output` will show the output in console
# *** IMPORTANT --preload causes conflict with eventlet, if you need --preload then use gevent instead of --preload ***
# gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 application:app --reload --log-file=- --error-logfile gunicorn.error.log --capture-output
gunicorn -k gevent -w 1 -b 0.0.0.0:7970 manage:app --log-file=- --error-logfile gunicorn.error.log --access-logfile gunicorn.log --capture-output