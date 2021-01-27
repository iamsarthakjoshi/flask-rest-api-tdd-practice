import os
from app.database import SQLService
from app.config import ConfigUtil

""" This class implements SQL service """


class PgSQLService(SQLService):
    __instance = None
    engine = None
    metadata = None

    @staticmethod
    def init_db(app):
        """
        Doesn't do anything as we don't need any app specific initilizations for using this service
        :param app:
        :return:
        """
        pass

    @staticmethod
    def get_instance() -> "SQLService":
        if not PgSQLService.__instance:
            PgSQLService.__instance = PgSQLService()
        return PgSQLService.__instance

    """ Gets a URI that can then be used to connect to a PGSQL Instance"""

    @staticmethod
    def get_sqlalchemy_uri():
        # config = ConfigUtil.read_file('sql.ini')
        host = os.getenv("PGSQL_DB_HOST", "127.0.0.1")
        user = os.getenv("PGSQL_USER", "local_username")
        passwd = os.getenv("PGSQL_PASSWORD", "local_password")
        database = os.getenv("PGSQL_DATABASE", "flask_rest_example_app_PGSQL_db")
        port = os.getenv("PGSQL_PORT", "3310")
        db_type = "postgresql"
        # Setup SQLAlchemy based on the db settings
        SQLALCHEMY_DATABASE_URI = (
            f"{db_type}://{user}:{passwd}@{host}:{port}/{database}"
        )
        return SQLALCHEMY_DATABASE_URI

    def __init__(self):
        SQLService.__init__(self, PgSQLService.get_sqlalchemy_uri())

    def execute_query(self, query):
        return self.engine.connect().execute(query)
