#!/usr/bin/env python
 
"""
Interface to SQLite3-based tick database

Adapted from code by Jabba Laci
https://pythonadventures.wordpress.com/2014/05/12/an-sqlite-example/
"""
 
import os
import atexit
import datetime

# SQLAlchemy ORM stuff
import sys
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
import logging

import pdb

Base = declarative_base()

# pdb.set_trace()
 
# Set the path to the database
PATH = os.path.dirname(os.path.abspath(__file__))
db_path = 'sqlite:///' + PATH + '/prices.db'
 
DBSessionFactory = None     # Session factory, created later
session = None       # Current session, created on demand

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

class Price(Base):
    __tablename__ = 'prices'
    id = Column(Integer, primary_key=True)
    epic = Column(String(20), nullable=False)
    updateDate = Column(String(20), nullable=False)
    updateTime = Column(String(20), nullable=False)
    bid  = Column(Float,nullable=False)
    offer = Column(Float,nullable=False)

# SCHEMA = """
# CREATE TABLE ticks
#        (epic           CHAR(20)    NOT NULL,
#        updateDate     CHAR(20),
#        updateTime        CHAR(20),
#        bid         FLOAT,
#        offer       FLOAT);
# """

def add_tick(tick):
    # Add a single IG_tick object to the DB as a single row
    # Deprecated: use add_ticks instead
    try:
        # pdb.set_trace()
        logger.debug("Writing to DB")
        session = DBSessionFactory()
        new_price = Price(epic=tick.epic, updateDate=tick.updateDate, updateTime=tick.updateTime, bid=tick.bid, offer=tick.offer)
        session.add(new_price)
        session.commit()
        logger.debug("Success")
        session.close()
        session = None
    except:
        session.rollback()
        session.close()
        session = None
        logger.error("Error")

def add_ticks(ticks):
    # Add multiple IG_tick objects to the DB each as a row
    try:
        # pdb.set_trace()
        logger.debug("Writing to DB")
        session = DBSessionFactory()
        for tick in ticks:
            new_price = Price(epic=tick.epic, updateDate=tick.updateDate, updateTime=tick.updateTime, bid=tick.bid, offer=tick.offer)
            session.add(new_price)
        session.commit()
        session.close()
        session = None
        logger.debug("Success")
    except:
        session.rollback()
        session.close()
        session = None
        logger.error("Error")
    
 
def get_all_ticks():
    # Get all data from the ticks table
    session = DBSessionFactory()
    result = session.query(Price).all()
    return result
 
def init(commit=True):
    # Initialize the DB.
    atexit.register(commit_and_close)
 
    # pdb.set_trace()

    if not os.path.exists(db_path):
        # DB does not exist, create a new one
        engine = create_engine(db_path)
        Base.metadata.create_all(engine)
    else:
        # All good - just create the engine
        engine = create_engine(db_path)

    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSessionFactory instance
    Base.metadata.bind = engine

    global DBSessionFactory

    if not DBSessionFactory:   
        # Create the session factory
        DBSessionFactory = sessionmaker(bind=engine)

        # Instantiate later, as required:
        # session = DBSessionFactory() 

 
def commit_and_close():
    # Commit and close DB connection.
    if session:
        try:
            session.commit()
            session.close()
        except:
            try:
                session.rollback()
                session.close()
            except:
                try:
                    session.close()
                except:
                    session = None
####

if __name__ == "__main__":
    init()