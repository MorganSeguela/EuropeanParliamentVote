#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# The main objective of this program is to update Parliamentarian information in DB and insert new parliamentarian

# DB driver package
import db_tools as db

# Log packges
import logging

# Json file management
import json

# File management
import os

# Date time package
from datetime import datetime

import time

def get_date_sits():
    """Retrieve sits on date in database

    Returns:
        List: list of dates
    """
    query_str = "SELECT DISTINCT(date_sit)\nFROM project.sits_on;"
    res_date = db.query_db(query_str)
    if res_date:
        return [this_date[0] for this_date in res_date]
    return res_date


def get_seat_num(parliament_id):
    """Retrieve all seats for a parliament

    Args:
        parliament_id (int): Parliament id to retrieve right seats

    Returns:
        List: List of seats from the parliament
    """
    query_str = "SELECT seat_number\nFROM project.seat WHERE use LIKE 'Parliamentarian' AND parliament_id = {};".format(parliament_id)
    res_seat = db.query_db(query_str)
    return [cdata[0] for cdata in res_seat]


def verify_seat_nb(parliament_id, sits_data):
    """Verify seats that are left

    Args:
        parliament_id (int): parliament id for the query
        sits_data (List): List of used seats

    Returns:
        List: List of left seats
    """
    seat_in_parl = get_seat_num(parliament_id=parliament_id)
    for one_sit in sits_data:
        if one_sit in seat_in_parl:
            seat_in_parl.remove(one_sit)
    return seat_in_parl
    

def gen_sits_transco_file():
    """Generator of transcodification files

    Yields:
        str: data filepath
    """
    start_dir = "tmp/stage_2/"
    transco_files_list = [this_file for this_file in os.listdir(start_dir) if "transco_" in this_file]

    for one_file in transco_files_list:
        yield start_dir + one_file


def insert_new_seat(isApply=False):
    """Insert newly retrieved sits on data in DB

    Args:
        isApply (bool, optional): Apply inserting data in DB. Defaults to False.
    """
    parliaments = ["BRU", "STR"]
    db_dates = get_date_sits()
    new_sits = []
    for tfile in gen_sits_transco_file():
        parsed_date = datetime.strptime(tfile.split(".")[0].split("_")[-1], "%y%m%d")
        print(parsed_date)
        parliament_id = parliaments.index(tfile.split("/")[-1].split(".")[0].split("_")[1])*1000
        cur_data = []
        if parsed_date.date() not in db_dates:
            with open(tfile, "r") as tcontent:
                all_lines = tcontent.readlines()
                seat_cons = [int(this_line.split(",")[3]) for this_line in all_lines]
                seat_left = verify_seat_nb(parliament_id/1000, seat_cons)
                logging.warning(datetime.strftime(parsed_date, "%Y-%m-%d") + "\n" + str(seat_left))
                cur_data = [[str(this_line.rstrip().split(",")[0]), str(parliament_id + int(this_line.rstrip().split(",")[3])), db.handle_str_sql(datetime.strftime(parsed_date, "%Y-%m-%d"))] for this_line in all_lines]
        new_sits.extend(cur_data)

    insert_seat_str = ""
    for tuple in new_sits:
        insert_seat_str += "INSERT INTO project.sits_on\n\tVALUES ({0}, {1}, {2});\n".format(*tuple)
    insert_seat_str += "COMMIT;"

    if isApply:
        db.query_db(insert_seat_str)
    else:
        print(insert_seat_str)


if __name__ == "__main__":
    insert_new_seat(True)