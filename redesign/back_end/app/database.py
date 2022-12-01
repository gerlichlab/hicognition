import logging
import sys
from typing import Any
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa


# this imports the module itself
this = sys.modules[__name__]

this.sql_connector = None
this.Base = None
this.engine = None
this.session = None
this.db = this.session
this.meta= None

def initialize(SQL_CONNECTOR: str):
    if (this.sql_connector is not None):
        logging.info(f"Database already initialized to {this.sql_connector}")
        return
    this.sql_connector = SQL_CONNECTOR
    this.Base = declarative_base(class_registry=dict())
    this.engine = sa.create_engine(this.sql_connector)
    this.session = orm.scoped_session(orm.sessionmaker(bind=this.engine, autocommit=False, autoflush=False))
    this.meta = this.Base.metadata
    
    #this.app.logger.info(f"Database connection to {this.sql_connector} ready.")

def shutdown(exception=None):
    #this.app.logger.info("Database connection closed.")
    this.session.remove()

