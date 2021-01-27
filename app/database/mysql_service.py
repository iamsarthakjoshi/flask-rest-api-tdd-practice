import os
from app.database import SQLService
from app.config import ConfigUtil

""" This class implements SQL service """


class MySQLService(SQLService):
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
        if not MySQLService.__instance:
            MySQLService.__instance = MySQLService()
        return MySQLService.__instance

    """ Gets a URI that can then be used to connect to a MYSQL Instance"""

    @staticmethod
    def get_sqlalchemy_uri():
        # config = ConfigUtil.read_file('sql.ini')
        host = os.getenv("MYSQL_DB_HOST", "127.0.0.1")
        user = os.getenv("MYSQL_USER", "local_username")
        passwd = os.getenv("MYSQL_PASSWORD", "local_password")
        database = os.getenv("MYSQL_DATABASE", "flask_rest_example_app_mysql_db")
        port = os.getenv("MYSQL_PORT", "3310")
        db_type = "mysql"
        db_connector = "pymysql"
        # Setup SQLAlchemy based on the db settings
        SQLALCHEMY_DATABASE_URI = (
            f"{db_type}+{db_connector}://{user}:{passwd}@{host}:{port}/{database}"
        )
        return SQLALCHEMY_DATABASE_URI

    def __init__(self):
        SQLService.__init__(self, MySQLService.get_sqlalchemy_uri())

    def execute_query(self, query):
        return self.engine.connect().execute(query)
