import sqlalchemy as db


class SQLService:
    __instance = None
    engine = None
    metadata = None

    """ Used by various script to make sure that the DB has been initialised"""

    @staticmethod
    def init_db(app):
        raise NotImplemented("init_db has not been implemented")

    """ """

    @staticmethod
    def get_instance() -> "SQLService":
        if not SQLService.__instance:
            raise Exception(
                "Tried to get SQL Instance before it was initialised, please call init_db first"
            )
        return SQLService.__instance

    """ Gets a URI that can then be used to connect to a MYSQL Instance"""

    @staticmethod
    def get_sqlalchemy_uri():
        raise NotImplemented("get_sql_alchemy_uri has not been implemented")

    def __init__(self, sql_alchemy_uri):
        engine = db.create_engine(sql_alchemy_uri)
        metadata = db.MetaData(engine)
        self.engine = engine
        self.metadata = metadata

    def execute_query(self, query):
        raise NotImplemented("execute_query has not been implemented")
