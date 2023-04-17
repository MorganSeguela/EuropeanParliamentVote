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

def get_parl_db_data(parls_id):
    """Retrieve parliamentarian data from database

    Args:
        parls_id (list): List of parliamentarian id

    Returns:
        dict: dictionary of parliamentarian data
    """
    # SQL query to retrieve only parliamentarian according to input list
    query_str = "SELECT parliamentarian_id, p_fullname, country_id, pg_id, npg_id\nFROM project.parliamentarian WHERE parliamentarian_id IN ({});".format(",".join(parls_id))

    res_parl = db.query_db(query_str)

    # Arrange data according to file ones
    parls_db = {}
    for tuple in res_parl:
        cur_data = {
            "fullName":tuple[1],
            "country": tuple[2],
            "politicalGroup": tuple[3],
            "nationalPoliticalGroup": tuple[4]
        }
        parls_db[str(tuple[0])] = cur_data

    return parls_db



def parliamentarian_files():
    """Generator of parliamentarians data file paths

    Yields:
        str: filepath of parliamentarians
    """
    start_dir = "tmp/stage_2/"
    for parl_file in [this_file for this_file in os.listdir(start_dir) if "parliamentarian_info" in this_file]:
        yield start_dir + parl_file


def diff_file_db(parls_data):
    """Compare parliamentarian info between db and file

    Args:
        parls_data (dict): Parliamentarian information in files

    Returns:
        (List, dict): List of tuple of parliamentarian to add, dictionary of parliamentarian to update
    """
    # Retrieve data from db
    parls_db = get_parl_db_data(list(parls_data.keys()))

    # Accoding types between file and db
    dtype = [str, int, int, int]

    toUpdate = {}
    toAdd = []

    for parl_id in parls_data.keys():
        fdata = parls_data[parl_id]
        # Verify if parliamentarian in DB
        if parl_id in parls_db.keys():
            curUpdate = {}
            dbdata = parls_db[parl_id]
            type_id = 0
            # Compare data between file and db
            for col in dbdata.keys():
                if dtype[type_id](fdata[col]) != dtype[type_id](dbdata[col]):
                    curUpdate[col] = fdata[col]
                type_id += 1
            if len(curUpdate.keys()):
                toUpdate[parl_id] = curUpdate
        else:
            # Otherwise create new tuple
            cur_data = [parl_id, 
                    db.handle_str_sql(fdata["fullName"]), 
                    fdata["country"], 
                    fdata["nationalPoliticalGroup"],
                    fdata["politicalGroup"]
                    ]
            cur_data = [str(this_data) for this_data in cur_data]
            toAdd.append(cur_data)
    return (toAdd, toUpdate)


def insert_new_data(data_to_add, isApply=False):
    """insert new parliamentarian information in DB

    Args:
        data_to_add (List[List]): List of tuples
        isApply (bool, optional): Apply insert in DB. Defaults to False.
    """
    logging.info("Inserting new parliamentarian in DB...")
    insert_new_parl_str = ""
    for tuple in data_to_add:
        insert_new_parl_str += "INSERT INTO project.parliamentarian\n\tVALUES(" + ",".join(tuple) + ");\n"

    insert_new_parl_str += "COMMIT;"

    if isApply:
        db.query_db(insert_new_parl_str)
    else:
        print(insert_new_parl_str)
    logging.info("New parliamentarian inserted successfully")
        

def update_parl_data(data_to_update, isApply=False):
    """Update parliamentarian information in DB

    Args:
        data_to_update (dict): {parl_id: {column: new_value}}
        isApply (bool, optional): Apply update in db. Defaults to False.
    """
    logging.info("Updating parliamentarians data in DB...")
    transco_col = {
        "fullname":"p_fullname",
        "country":"country_id",
        "nationalPoliticalGroup":"npg_id",
        "politicalGroup":"pg_id"
    }
    update_parl_str = ""
    for parl_id in data_to_update.keys():
        update_parl_str += "UPDATE project.parliamentarian\nSET "
        update_col = data_to_update[parl_id]
        first = True
        for col in update_col.keys():
            if not first:
                update_parl_str += ","
            update_parl_str += "{}={}".format(transco_col[col], update_col[col])
        update_parl_str += "\nWHERE parliamentarian_id={};\n".format(parl_id)

    update_parl_str += "COMMIT;"

    if isApply:
        db.query_db(update_parl_str)
    else:
        print(update_parl_str)
    logging.info("Parliamentarian data updated")


# UPDATE project.parliamentarian
# SET column1 = val1, column2=val2
# WHERE parliamentarian_id = 1312;


def update_parl_table(isApply=False):
    """Orchestrate insert and update data from files compared to DB

    Args:
        isApply (bool, optional): apply modification in db. Defaults to False.
    """
    parl_data = {}

    for parl_file in parliamentarian_files():
        cur_data = {}
        with open(parl_file, "r") as file_content:
            cur_data = json.load(file_content)
        for parl_id in cur_data.keys():
            parl_data[parl_id] = cur_data[parl_id]
    
    addData, updateData = diff_file_db(parl_data)

    if addData:
        insert_new_data(addData, isApply)
    if updateData.keys():
        update_parl_data(updateData, isApply)


if __name__ == "__main__":
    update_parl_table(True)