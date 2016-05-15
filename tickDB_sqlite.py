#!/usr/bin/env python
 
"""
Interface to SQLite3-based tick database

Adapted from code by Jabba Laci
https://pythonadventures.wordpress.com/2014/05/12/an-sqlite-example/
"""
 
import os
import sqlite3
import atexit
import datetime

import logging

import pdb
 
# Set the path to the database, and create the table schema
PATH = os.path.dirname(os.path.abspath(__file__))
SCHEMA = """
CREATE TABLE ticks
       (epic           CHAR(20)    NOT NULL,
       updateDate     CHAR(20),
       updateTime        CHAR(20),
       bid         FLOAT,
       offer       FLOAT);
"""
SQLITE_DB = PATH + '/prices.db'
 
conn = []     # This will be initialised later with the DB connection

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

def add_tick(tick):
    # Add a single IG_tick object to the DB as a single row
    try:
        logger.debug("Writing to tick DB")
        query = "INSERT INTO ticks (epic, updateDate, updateTime, bid, offer) VALUES (?, ?, ?, ?, ?)"
        conn.execute(query, (tick.epic, tick.updateDate, tick.updateTime, tick.bid, tick.offer))
        logger.debug("Success")
    except sqlite3.IntegrityError:
        logger.error("Error")
 
def get_all_ticks():
    # Get all data from the ticks table
    query = "SELECT * FROM ticks"
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result
 
def create_db():
    # Create a new database using the schema
    conn = sqlite3.connect(SQLITE_DB)
    conn.executescript(SCHEMA)
 
def init(commit=True):
    # Initialize the DB.
    global conn
    if commit:
        atexit.register(commit_and_close)
    else:
        atexit.register(close)
 
    if not os.path.exists(SQLITE_DB):
        create_db()
    if not conn:
        conn = sqlite3.connect(SQLITE_DB, check_same_thread=False)
 
def commit():
    # Commit.
    
    if conn:
        conn.commit()
 
def close():
    # Close.
    
    if conn:
        conn.close()
 
def commit_and_close():
    """
    Commit and close DB connection.
 
    As I noticed, commit() must be called, otherwise changes
    are not committed automatically when the program terminates.
    """
    if conn:
        conn.commit()
        conn.close()
 
####################
 
if __name__ == "__main__":
    init()