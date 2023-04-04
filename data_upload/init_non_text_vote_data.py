#!/usr/bin/python

import psycopg2
from config import config
import re
import json

def insert_parliament():
    """Create strings to insert parliament data

    Returns:
        str: String to insert parliament data
    """
    parliament_data=[(0, 'Brussels', 'BRU'),
                     (1, 'Strasbourg', 'STR')]

    insert_parliament_string = ""
    
    for thisData in parliament_data:
        insert_parliament_string += "INSERT INTO project.parliament\n\tVALUES ({0}, \'{1}\', \'{2}\');\n".format(*thisData)
    
    return insert_parliament_string


def insert_seat(filename="tmp/clean_brussels_siege.csv"):
    """Create string to insert seats data
    
    Args:
        filename (str, optional): filename to parliamentarian data. Defaults to "tmp/clean_brussels_siege.csv".

    Returns:
        str: String to insert seats in the database
    """
    insert_seat_string = ""
    seats_info = None
    with open(filename, "r") as content:
        list_lines = content.readlines()
        del list_lines[0]
        seats_info = [re.sub("\n", "", x).split(",") for x in list_lines]

    for seat in seats_info:
        seat[5] = "\'{}\'".format(seat[5])
        insert_seat_string += "INSERT INTO project.seat\n\tVALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6});\n".format(*seat)

    return insert_seat_string
        
def insert_parliamentarian(filename="tmp/Parlementarian_011723.json"):
    """Create strings to insert political group, national political group and parliamentarian in the databse.

    Args:
        filename (str, optional): _description_. Defaults to "tmp/Parlementarian_011723.json".

    Returns:
        (str, str, str): (politcalGroup, nationalPotilicalGroup, parliamentatian)
    """
    sql_npg_str = ""
    sql_pg_str = ""
    sql_parl_str = ""

    parl_json = {}

    with open(filename, "r") as file_content:
        parl_json = json.load(file_content)
    
    uni_pg = []
    uni_npg = []
    
    for id_parl in parl_json.keys():
        cur_pg = -1
        cur_npg = -1

        if parl_json[id_parl]["politicalGroup"] in uni_pg:
            cur_pg = uni_pg.index(parl_json[id_parl]["politicalGroup"])
        else:
            cur_pg = len(uni_pg)
            uni_pg.append(parl_json[id_parl]["politicalGroup"])
        
        if parl_json[id_parl]["nationalPoliticalGroup"] in uni_npg:
            cur_npg = uni_npg.index(parl_json[id_parl]["nationalPoliticalGroup"])
        else:
            cur_npg = len(uni_npg)
            uni_npg.append(parl_json[id_parl]["nationalPoliticalGroup"])

        values = [id_parl, 
                  "\'" + re.sub("\'", "\'\'", parl_json[id_parl]["fullName"]) + "\'", 
                  "\'" + re.sub("\'", "\'\'", parl_json[id_parl]["country"]) + "\'", 
                  str(cur_npg), str(cur_pg)]
        sql_parl_str += "INSERT INTO project.parliamentarian\n\tVALUES(" + ",".join(values) + ");\n"
    
    for pg in uni_pg:
        sql_pg_str += "INSERT INTO project.political_group\n\tVALUES ({0}, \'{1}\');\n"\
        .format(uni_pg.index(pg), re.sub("\'", "\'\'", pg))

    for npg in uni_npg:
        sql_npg_str += "INSERT INTO project.national_political_group\n\tVALUES ({0}, \'{1}\');\n"\
        .format(uni_npg.index(npg), re.sub("\'", "\'\'", npg))

    return (sql_pg_str, sql_npg_str, sql_parl_str)

def insert_vote_values():
    """Create string to insert vote value data 

    Returns:
        str: string to insert data
    """
    vote_data = [
        (0, "\'for\'", 1),
        (1, "\'against\'", -1),
        (2, "\'abstention\'", 0)
    ]

    result = ""

    for vote_vect in vote_data:
        result += "INSERT INTO project.vote_value\n\tVALUES ({0}, {1}, {2});\n".format(*vote_vect)

    return result

def connect():
    """
    Connect to the PostgreSQL database server.
    Insert parliament and parliament seats.
    Insert political group and national political group and parliamentarian.
    """
    conn = None
    try:
        # read connection parameters
        params = config(filename="../EP_project/data_storage/database.ini")

        # connect to the postgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # Insert parliament data and return number of lines
        print("Inserting parliament data...")
        cur.execute(insert_parliament())
        
        cur.execute("SELECT count(*) FROM project.parliament;")
        db_result = cur.fetchone()
        print(db_result)

        # Insert parliament seats data and return number of lines
        print("Inserting parliament seats data...")
        cur.execute(insert_seat())
        
        cur.execute("SELECT count(*) FROM project.seat;")
        db_result = cur.fetchone()
        print(db_result)

        # Gather parliamentarian data
        pg, npg, parl = insert_parliamentarian()

        # Insert political group data and return number of lines
        print("Inserting political group...")
        cur.execute(pg)
        
        cur.execute("SELECT count(*) FROM project.political_group;")
        db_result = cur.fetchone()
        print(db_result)

        # Insert national political group and return number of lines
        print("Inserting national political group...")
        cur.execute(npg)
        
        cur.execute("SELECT count(*) FROM project.national_political_group;")
        db_result = cur.fetchone()
        print(db_result)

        # Insert parliamentarian and return number of lines
        print("Inserting parliamentarian...")
        cur.execute(parl)
        
        cur.execute("SELECT count(*) FROM project.parliamentarian;")
        db_result = cur.fetchone()
        print(db_result)

        # Insert vote value and return number of lines
        print("Inserting vote value...")
        vote_value = insert_vote_values()
        cur.execute(vote_value)
        
        cur.execute("SELECT count(*) FROM project.vote_value;")
        db_result = cur.fetchone()
        print(db_result)

        # commit values 
        cur.execute("COMMIT;")


        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def query_db(query_str):
    db_result = None
    conn = None
    try:
        # read connection parameters
        params = config(filename="../EP_project/data_storage/database.ini")

        print("Connecting to db...")
        # connect to the postgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        print("Executing the following query:\n" + query_str)
        cur.execute(query_str)
        db_result = cur.fetchall()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
        return db_result


def update_parliamentarian(filename="tmp/Parlementarian_011723.json"):
    sql_npg_str = ""
    sql_pg_str = ""
    sql_parl_str = ""

    old_npg = query_db("SELECT npg_id, npg_name FROM project.national_political_group;")
    uni_npg = [v[1] for v in old_npg]
    
    old_pg  = query_db("SELECT pg_id, pg_name FROM project.political_group;")
    uni_pg = [v[1] for v in old_pg]

    old_par = query_db("SELECT parliamentarian_id FROM project.parliamentarian;")
    old_par = [v[0] for v in old_par]

    new_npg = []
    new_pg = []

    parl_json = {}

    with open(filename, "r") as file_content:
        parl_json = json.load(file_content)

    
    for id_parl in parl_json.keys():
        cur_pg = -1
        cur_npg = -1

        if parl_json[id_parl]["politicalGroup"] in uni_pg:
            cur_pg = uni_pg.index(parl_json[id_parl]["politicalGroup"])
        else:
            cur_pg = len(uni_pg)
            uni_pg.append(parl_json[id_parl]["politicalGroup"])
            new_pg.append(parl_json[id_parl]["politicalGroup"])
        
        if parl_json[id_parl]["nationalPoliticalGroup"] in uni_npg:
            cur_npg = uni_npg.index(parl_json[id_parl]["nationalPoliticalGroup"])
        else:
            cur_npg = len(uni_npg)
            uni_npg.append(parl_json[id_parl]["nationalPoliticalGroup"])
            new_npg.append(parl_json[id_parl]["nationalPoliticalGroup"])

        if id_parl not in old_par:
            values = [id_parl, 
                    "\'" + re.sub("\'", "\'\'", parl_json[id_parl]["fullName"]) + "\'", 
                    "\'" + re.sub("\'", "\'\'", parl_json[id_parl]["country"]) + "\'", 
                    str(cur_npg), str(cur_pg)]
            sql_parl_str += "INSERT INTO project.parliamentarian\n\tVALUES(" + ",".join(values) + ");\n"
    
    for pg in new_pg:
        sql_pg_str += "INSERT INTO project.political_group\n\tVALUES ({0}, \'{1}\');\n"\
        .format(uni_pg.index(pg), re.sub("\'", "\'\'", pg))

    for npg in new_npg:
        sql_npg_str += "INSERT INTO project.national_political_group\n\tVALUES ({0}, \'{1}\');\n"\
        .format(uni_npg.index(npg), re.sub("\'", "\'\'", npg))

    return (sql_pg_str, sql_npg_str, sql_parl_str)

def update_db():
    """
    Connect to the PostgreSQL database server.
    Insert parliament and parliament seats.
    Insert political group and national political group and parliamentarian.
    """
    conn = None
    try:
        # read connection parameters
        params = config(filename="../EP_project/data_storage/database.ini")

        # connect to the postgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # Gather parliamentarian data
        pg, npg, parl = update_parliamentarian("tmp/Parlementarian_230302.json")

        # Insert political group data and return number of lines
        if len(pg) > 0:
            print("Inserting political group...")
            cur.execute(pg)
            
            cur.execute("SELECT count(*) FROM project.political_group;")
            db_result = cur.fetchone()
            print(db_result)

        # Insert national political group and return number of lines
        if len(npg) > 0:
            print("Inserting national political group...")
            cur.execute(npg)
            
            cur.execute("SELECT count(*) FROM project.national_political_group;")
            db_result = cur.fetchone()
            print(db_result)

        # Insert parliamentarian and return number of lines
        if len(parl) > 0:
            print("Inserting parliamentarian...")
            cur.execute(parl)
            
            cur.execute("SELECT count(*) FROM project.parliamentarian;")
            db_result = cur.fetchone()
            print(db_result)

        # commit values 
        cur.execute("COMMIT;")


        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    # connect()
    update_db()