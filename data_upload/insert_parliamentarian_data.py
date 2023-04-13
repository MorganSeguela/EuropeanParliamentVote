#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# The main objective of this program is to insert Parliamentarian information in DB

# DB driver package
import db_tools as db

# Log packges
import logging

# Json file management
import json

# File management
import os


def insert_country_data(isApply=False):
    """Insert country data in db

    Args:
        isApply (bool, optional): Apply insert in DB. Defaults to False.
    """
    logging.info("Inserting country data in DB...")
    start_dir = "tmp/stage_2/"

    ctr_lines = []
    with open(start_dir + "country_info.csv", "r") as country_file:
        ctr_lines = country_file.readlines()
    
    insert_country_string = ""
    for one_line in ctr_lines:
        ctr_id, ctr_name = one_line.split(",")
        insert_country_string += "INSERT INTO project.country\n\tVALUES ({0}, {1});\n".format(ctr_id, db.handle_str_sql(ctr_name.rstrip()))
    insert_country_string += "COMMIT;"

    if isApply:
        db.query_db(insert_country_string)
    else:
        print(insert_country_string)

    logging.info("Country data successfully inserted")


def insert_pg_data(isApply=False):
    """Insert Political Group in db

    Args:
        isApply (bool, optional): Apply insert in db. Defaults to False.
    """
    logging.info("Inserting political group data in DB...")
    start_dir = "tmp/stage_2/"

    pg_data = []
    with open(start_dir + "political_group_info.csv" , "r") as pg_file:
        pg_data = pg_file.readlines()
    
    insert_pg_string = ""
    for one_line in pg_data:
        all_data = one_line.rstrip().split(",")
        all_data[1] = db.handle_str_sql(all_data[1])
        all_data[2] = db.handle_str_sql(all_data[2])
        insert_pg_string += "INSERT INTO project.political_group\n\tVALUES ({0}, {1},{2});\n".format(*all_data)

    insert_pg_string += "COMMIT;"

    if isApply:
        db.query_db(insert_pg_string)
    else:
        print(insert_pg_string)

    logging.info("Political group data successfully inserted")


def insert_npg_data(isApply=False):
    """Insert National Political Group in db

    Args:
        isApply (bool, optional): Apply insert in DB. Defaults to False.
    """
    logging.info("Inserting national political group data in DB...")
    start_dir = "tmp/stage_2/"

    npg_data = []
    with open(start_dir + "national_political_group_info.csv" , "r") as npg_file:
        npg_data = npg_file.readlines()
    
    insert_npg_string = ""
    for one_line in npg_data:
        all_data = one_line.rstrip().split(",")
        insert_npg_string += "INSERT INTO project.national_political_group\n\tVALUES ({0}, {1});\n".format(all_data[0], db.handle_str_sql(all_data[1]))


    insert_npg_string += "COMMIT;"

    if isApply:
        db.query_db(insert_npg_string)
    else:
        print(insert_npg_string)

    logging.info("Political group data successfully inserted")


def parliamentarian_files():
    """Generator of parliamentarians data file paths

    Yields:
        str: filepath of parliamentarians
    """
    start_dir = "tmp/stage_2/"
    for parl_file in [this_file for this_file in os.listdir(start_dir) if "parliamentarian_info" in this_file]:
        yield start_dir + parl_file


def insert_parl_data(isApply=False):
    """Insert parliamentarian data in db

    Args:
        isApply (bool, optional): Apply insert in DB. Defaults to False.
    """
    logging.info("Inserting parliamentarians data in DB...")

    parl_data = {}

    for parl_file in parliamentarian_files():
        cur_data = {}
        with open(parl_file, "r") as file_content:
            cur_data = json.load(file_content)
        for parl_id in cur_data.keys():
            parl_data[parl_id] = cur_data[parl_id]
        
    insert_parl_string = ""
    for parl_id in parl_data.keys():
        cur_data = [parl_id, 
                    db.handle_str_sql(parl_data[parl_id]["fullName"]), 
                    parl_data[parl_id]["country"], 
                    parl_data[parl_id]["nationalPoliticalGroup"],
                    parl_data[parl_id]["politicalGroup"]
                    ]
        cur_data = [str(this_data) for this_data in cur_data]
        insert_parl_string += "INSERT INTO project.parliamentarian\n\tVALUES(" + ",".join(cur_data) + ");\n"

    insert_parl_string += "COMMIT;"

    if isApply:
        db.query_db(insert_parl_string)
    else:
        print(insert_parl_string)
        
    logging.info("Parliamentarians data successfully inserted")

if __name__ == "__main__":
    isApply = True
    insert_country_data(isApply)
    insert_pg_data(isApply)
    insert_npg_data(isApply)
    insert_parl_data(isApply)