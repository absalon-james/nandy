"""Module with classes for interfacing with a database."""

from contextlib import contextmanager
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, DateTime, ForeignKey, \
    Integer, Numeric, String

Base = declarative_base()


class Tenant(Base):
    """Tenant table. Just an id and an uuid."""

    __tablename__ = 'tenant'
    id = Column(Integer, primary_key=True)
    uuid = Column(String(32), unique=True)

    @classmethod
    def get_or_create(cls, session, uuid):
        """Get or create a tenant.

        Creates a tenant if one with uuid does not exist.
        Returns the existing or new tenant.

        :param session: Sqlalchemy session
        :param uuid: String uuid of tenant.
        :returns: Tenant

        """
        tenant = session.query(Tenant).filter_by(uuid=uuid).first()
        if not tenant:
            tenant = Tenant(uuid=uuid)
            session.add(tenant)
        return tenant


class ActiveVCPUS(Base):
    """Active vcpus table.

    Holds time series data for vcpu metering.
    """

    __tablename__ = 'meter_active_vcpus'
    value = Column(Integer)
    time = Column(DateTime(), primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenant.id'), primary_key=True)


class ActiveMemoryMB(Base):
    """Active Memory MB table.

    Holds time series data for ram metering.
    """

    __tablename__ = 'meter_active_memory_mb'
    value = Column(Numeric(20, 2))
    time = Column(DateTime(), primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenant.id'), primary_key=True)


class ActiveLocalStorageGB(Base):
    """Active Local Storage Table.

    Holds time series data for storage metering.
    """

    __tablename__ = 'meter_active_local_storage_gb'
    value = Column(Numeric(20, 2))
    time = Column(DateTime(), primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenant.id'), primary_key=True)


class DB(object):
    """Database instance manager."""

    def __init__(self):
        """Init the manager."""
        self.engine = None
        self.sessionmaker = None

    def get_engine(self, conf):
        """Return an instance of sqlalchemy engine.

        Should be one per process. Reuse if one exists.

        :param conf: Dictionary configuration
        :returns: sqlalchemy engine
        """
        # Return engine if already created.
        if self.engine:
            return self.engine

        # Build the db connection string from config.
        kwargs = {
            'username': conf.get('username'),
            'password': conf.get('password'),
            'host': conf.get('host', 'localhost'),
            'port': conf.get('port', 3306),
            'dbname': conf.get('dbname', 'nandy')
        }
        connection_string = (
            'mysql://{username}:{password}'
            '@{host}:{port}/{dbname}').format(**kwargs)

        # Get instance of engine
        self.engine = create_engine(
            connection_string,
            echo=False,
            pool_recycle=conf.get('pool_recycle', 1800)
        )

        # Create tables.
        Base.metadata.create_all(self.engine)

        # Return
        return self.engine

    def get_session(self):
        """Get a sqlalchemy session.

        :returns: Sqlalchemy session
        """
        # Check for engine
        if not self.engine:
            raise Exception('Engine not created yet.')

        # Check for session maker
        if not self.sessionmaker:
            self.sessionmaker = sessionmaker(bind=self.engine)

        # Call session maker for session
        return self.sessionmaker(bind=self.engine)

    @contextmanager
    def session_scope(self):
        """Return a session context to wrap around db operations.

        example:
        with db.session_scope() as session:
            # do some inserts

        :returns: Session context
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

# Create module db instance.
# Import this and use db.get_engine() to get started.
db = DB()
