#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# The aim of this program is to provide tools to interact with the db

import psycopg2

import re

from config import config

import time

db_ini_filename = "../EP_project/data_storage/database.ini"

def handle_str_sql(str_value):
    """Replace simple quote with doubled simple quote for postgres insert

    Args:
        str_value (str): string to transform

    Returns:
        str: string with only doubled simple quotes
    """
    if str_value != None:
        return "\'" + re.sub("\'", "\'\'",str_value) + "\'"
    return "NULL"

def query_db(query_str):
    """execute db query

    Args:
        query_str (str): query to execute on the db

    Returns:
        List[Vect()]: Result of the query
    """
    db_result = None
    conn = None
    try:
        # read connection parameters
        params = config(filename=db_ini_filename)

        print("Connecting to db...")
        # connect to the postgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # Execute query
        print("Executing the following query:\n" + query_str)
        cur.execute(query_str)
        db_result = cur.fetchall()

        # Close connection
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
        return db_result



