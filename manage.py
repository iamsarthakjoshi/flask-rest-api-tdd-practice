from gevent import monkey

monkey.patch_all()

from flask_migrate import init, migrate, upgrade
from flask.cli import FlaskGroup
from rq import Connection, Worker
from app import create_app, db


app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("drop_db")
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@cli.command("migrate_db")
def migrate_db():
    try:
        init(directory="migrations", multidb=False)
    except:
        pass
    finally:
        migrate(directory="migrations")
        upgrade(directory="migrations")


@cli.command("downgrade_db")
def downgrade_db():
    downgrade(directory="migrations", revision="-1", sql=False, tag=None)


@cli.command("run_worker")
def run_worker():
    worker = Worker(app.config["QUEUES"], connection=app.redis)
    worker.work()


# Run more workers or, run more docker worker images
# @cli.command('run_worker_two')
# def run_worker():
#     worker = Worker(app.config['QUEUES'], connection=app.redis)
#     worker.work()

if __name__ == "__main__":
    cli()
