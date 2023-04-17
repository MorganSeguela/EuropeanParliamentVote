#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# The main objective of this program is to insert SEAT information in DB

# DB driver package
import db_tools as db

# Log packges
import logging

import os

from datetime import datetime

def retrieve_parliament_data():
    """Parliament data (id, name, abbreviation)

    Yields:
        tuple: (id, name, abbreviation)
    """
    parliament_data = [(0, 'Brussels', 'BRU'), (1, 'Strasbourg', 'STR')]
    for one_parl in parliament_data:
        yield one_parl


def insert_parliament_data(isApply=False):
    """Insert parliament data in DB

    Args:
        isApply (bool, optional): Apply insert in DB. Defaults to False.
    """
    logging.info("Inserting parliament data in DB...")
    insert_parliament_string = ""

    for one_parl in retrieve_parliament_data():
        insert_parliament_string += "INSERT INTO project.parliament\n\tVALUES ({0}, \'{1}\', \'{2}\');\n".format(*one_parl)
    insert_parliament_string += "COMMIT;"

    if isApply:
        db.query_db(insert_parliament_string)
    else:
        print(insert_parliament_string)

    logging.info("Parliament data successfully inserted")


def retrieve_seat_data():
    """Retrieve seat data from tmp/stage_1/seat_info.csv

    Yields:
        Tuple(): (seat_id, seat_number, x_pos, y_pos, x_size, y_size, use, parliament_id)
    """
    filepath = "tmp/stage_1/seat_info.csv"

    parsed_type = (int, float, float, int, int, str, int)

    seats_data = []
    with open(filepath, "r") as seat_file:
        seats_data = [one_seat.rstrip().split(",") for one_seat in seat_file.readlines()]
    
    for one_seat in seats_data:
        one_seat = [parsed_type[i](one_seat[i]) for i in range(len(one_seat))]
        one_seat.insert(0, 1000 * one_seat[6] + one_seat[0])
        yield one_seat


def insert_seat_data(isApply=False):
    """Insert seat data in DB

    Args:
        isApply (bool, optional): Apply insert in DB. Defaults to False.
    """
    logging.info("Inserting seat data in DB...")
    insert_seat_string = ""
    for one_seat in retrieve_seat_data():
        one_seat[6] = "\'{}\'".format(one_seat[6])
        insert_seat_string += "INSERT INTO project.seat\n\tVALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7});\n".format(*one_seat)
    
    insert_seat_string += "COMMIT;"

    if isApply:
        db.query_db(insert_seat_string)
    else:
        print(insert_seat_string)
        
    logging.info("Seat data successfully inserted")


def gen_sits_transco_file():
    """Generator of transcodification files

    Yields:
        str: data filepath
    """
    start_dir = "tmp/stage_2/"
    transco_files_list = [this_file for this_file in os.listdir(start_dir) if "transco_" in this_file]

    for one_file in transco_files_list:
        yield start_dir + one_file


def insert_sits_on_data(isApply=False):
    """Insert sits on data in DB

    Args:
        isApply (bool, optional): Apply insert in DB. Defaults to False.
    """
    logging.info("Inserting Sits on data in DB...")

    sits_on_data = []
    for transo_file in gen_sits_transco_file():
        parsed_data = datetime.strftime(datetime.strptime(transo_file.split(".")[0].split("_")[-1], "%y%m%d"), "%Y-%m-%d")
        parliaments = ["BRU", "STR"]
        parliament_id = parliaments.index(transo_file.split("/")[-1].split(".")[0].split("_")[1])*1000
        cur_data = []
        with open(transo_file, "r") as transco_content:
            cur_data = [[int(this_line.rstrip().split(",")[0]), str(parliament_id + int(this_line.rstrip().split(",")[3])), db.handle_str_sql(parsed_data)] for this_line in transco_content.readlines()]
        sits_on_data.extend(cur_data)
    
    insert_sits_on_string = ""
    for one_pair in sits_on_data:
        insert_sits_on_string += "INSERT INTO project.sits_on\n\tVALUES ({0}, {1}, {2});\n".format(*one_pair)
    insert_sits_on_string += "COMMIT;"

    if isApply:
        db.query_db(insert_sits_on_string)
    else:
        print(insert_sits_on_string)
        
    logging.info("Sits on data successfully inserted")

if __name__ == "__main__":
    isApply= False
    insert_parliament_data(isApply)
    insert_seat_data(isApply)
    insert_sits_on_data(True)

