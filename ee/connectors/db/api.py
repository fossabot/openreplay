from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker, session
from contextlib import contextmanager
import logging
from decouple import config as _config
from pathlib import Path

DATABASE = _config('CLOUD_SERVICE')
if DATABASE == 'redshift':
    import pandas_redshift as pr

base_path = Path(__file__).parent.parent

from db.models import Base

logger = logging.getLogger(__file__)


def get_class_by_tablename(tablename):
    """Return class reference mapped to table.
    Raise an exception if class not found

    :param tablename: String with name of table.
    :return: Class reference.
    """
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c
    raise AttributeError(f'No model with tablename "{tablename}"')


class DBConnection:
    """
    Initializes connection to a database
    To update models file use:
    sqlacodegen --outfile models_universal.py mysql+pymysql://{USER}:{pwd}@{HOST}
    """
    _sessions = sessionmaker()

    def __init__(self, config) -> None:
        self.metadata = MetaData()
        self.config = config

        if config == 'redshift':
            self.pdredshift = pr
            ci = _config('cluster_info', default='')
            cluster_info = dict()
            if ci == '':
                cluster_info['USER'] = _config('USER')
                cluster_info['HOST'] = _config('HOST')
                cluster_info['PORT'] = _config('PORT')
                cluster_info['PASSWORD'] = _config('PASSWORD')
                cluster_info['DBNAME'] = _config('DBNAME')
            else:
                ci = ci.split(' ')
                cluster_info = dict()
                for _d in ci:
                    k,v = _d.split('=')
                    cluster_info[k]=v
            self.pdredshift.connect_to_redshift(dbname=cluster_info['DBNAME'],
                                                host=cluster_info['HOST'],
                                                port=cluster_info['PORT'],
                                                user=cluster_info['USER'],
                                                password=cluster_info['PASSWORD'])

            self.pdredshift.connect_to_s3(aws_access_key_id=_config('AWS_ACCESS_KEY_ID'),
                                          aws_secret_access_key=_config('AWS_SECRET_ACCESS_KEY'),
                                          bucket=_config('BUCKET'),
                                          subdirectory=_config('SUBDIRECTORY', default=None))

            self.CONNECTION_STRING = _config('CONNECTION_STRING').format(
                USER=cluster_info['USER'],
                PASSWORD=cluster_info['PASSWORD'],
                HOST=cluster_info['HOST'],
                PORT=cluster_info['PORT'],
                DBNAME=cluster_info['DBNAME']
            )
            self.engine = create_engine(self.CONNECTION_STRING)

        elif config == 'clickhouse':
            self.CONNECTION_STRING = _config('CONNECTION_STRING').format(
                HOST=_config('HOST'),
                DATABASE=_config('DATABASE')
            )
            self.engine = create_engine(self.CONNECTION_STRING)
        elif config == 'pg':
            self.CONNECTION_STRING = _config('CONNECTION_STRING').format(
                USER=_config('USER'),
                PASSWORD=_config('PASSWORD'),
                HOST=_config('HOST'),
                PORT=_config('PORT'),
                DATABASE=_config('DATABASE')
            )
            self.engine = create_engine(self.CONNECTION_STRING)
        elif config == 'bigquery':
            pass
        elif config == 'snowflake':
            self.CONNECTION_STRING = _config('CONNECTION_STRING').format(
                USER=_config('USER'),
                PASSWORD=_config('PASSWORD'),
                ACCOUNT=_config('ACCOUNT'),
                DATABASE=_config('DATABASE'),
                DBNAME = _config('DBNAME'),
                WAREHOUSE = _config('WAREHOUSE')
            )
            self.engine = create_engine(self.CONNECTION_STRING)
        else:
            raise ValueError("This db configuration doesn't exist. Add into keys file.")

    @contextmanager
    def get_test_session(self, **kwargs) -> session:
        """
        Test session context, even commits won't be persisted into db.
        :Keyword Arguments:
            * autoflush (``bool``) -- default: True
            * autocommit (``bool``) -- default: False
            * expire_on_commit (``bool``) -- default: True
        """
        connection = self.engine.connect()
        transaction = connection.begin()
        my_session = type(self)._sessions(bind=connection, **kwargs)
        yield my_session

        # Do cleanup, rollback and closing, whatever happens
        my_session.close()
        transaction.rollback()
        connection.close()

    @contextmanager
    def get_live_session(self) -> session:
        """
        This is a session that can be committed.
        Changes will be reflected in the database.
        """
        # Automatic transaction and connection handling in session
        connection = self.engine.connect()
        my_session = type(self)._sessions(bind=connection)

        yield my_session

        my_session.close()
        connection.close()

    def restart(self):
        self.close()
        self.__init__(config=self.config)

    def close(self):
        if self.config == 'redshift':
            self.pdredshift.close_up_shop()
