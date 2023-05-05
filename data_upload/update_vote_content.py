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


def get_pv_db():
    query_str = "SELECT minute_url FROM project.minute;"
    pv_res = db.query_db(query_str)
    return [tuple[0] for tuple in pv_res]



def gen_pv_files():
    start_dir = "tmp/stage_2/"
    for pv_file in [this_pv for this_pv in os.listdir(start_dir) if "PV_url" in this_pv]:
        yield start_dir + pv_file


def insert_pv_data(isApply=False):
    logging.info("Inserting minute data in DB...")
    unique_pv = get_pv_db()
    pv_data = []
    for pv_file in gen_pv_files():
        cur_data = []
        with open(pv_file, "r") as pv_content:
            cur_data = [this_line.rstrip().split(",")[1] for this_line in  pv_content.readlines()]
        for one_url in cur_data:
            if (one_url not in unique_pv) and (one_url not in pv_data) :
                pv_data.append([len(unique_pv) + len(pv_data), one_url])
    
    pv_db = get_pv_db()

    insert_pv_string = ""
    for this_data in pv_data:
        if this_data[0] not in pv_db:
            insert_pv_string += "INSERT INTO project.minute\n\tVALUES ({0}, {1});\n".format(this_data[0], db.handle_str_sql(this_data[1]))
    insert_pv_string += "COMMIT;"

    if isApply:
        db.query_db(insert_pv_string)
    else:
        print(insert_pv_string)

    logging.info("Minute data successfully inserted")



def get_text_id_db():

    query_str = "SELECT reference FROM project.text;"

    res_text = db.query_db(query_str)

    return [tuple[0] for tuple in res_text]


def insert_text_data(isApply=False):
    logging.info("Inserting text data in DB...")
    start_dir = "tmp/stage_1/"
    text_data = []
    with open(start_dir+"text_info.csv", "r") as text_file:
        text_data = [txt_line.rstrip().split(";") for txt_line in text_file.readlines()]
    
    db_ref = get_text_id_db()

    insert_text_string = ""
    for one_text in text_data:
        if one_text[0] not in db_ref:
            insert_text_string += "INSERT INTO project.text\n\tVALUES ({0}, {1}, {2});\n".format(*[db.handle_str_sql(this_data) for this_data in one_text])
    insert_text_string += "COMMIT;"

    if isApply:
        db.query_db(insert_text_string)
    else:
        print(insert_text_string)

    logging.info("Text data successfully inserted")

def gen_content_file():
    start_dir = "tmp/stage_2/"
    for content_file in [this_file for this_file in os.listdir(start_dir) if "Vote_content" in this_file]:
        yield start_dir + content_file


def get_content_db():
    query_str = "SELECT content_id FROM project.vote_content;"
    res_db = db.query_db(query_str)
    return [tuple[0] for tuple in res_db]

def insert_content_data(isApply=False):
    logging.info("Inserting vote content data in DB...")
    
    content_data = []
    for content_file in gen_content_file():
        cur_data = {}
        with open(content_file, "r") as content_content:
            cur_data = json.load(content_content)
        for content_id in cur_data.keys():
            this_data = cur_data[content_id]
            content_data.append((
                content_id, 
                db.handle_str_sql(this_data["description"]),
                db.handle_str_sql(this_data["date"]),
                db.handle_str_sql(this_data["reference"]),
                this_data["PV"]
            ))
    
    content_db = get_content_db()
    insert_content_string = ""
    for this_tuple in content_data:
        if int(this_tuple[0]) not in content_db:
            insert_content_string += "INSERT INTO project.vote_content\n\tVALUES ({0}, {1}, {2}, {3}, {4});\n".format(*this_tuple)
    insert_content_string += "COMMIT;"

    if isApply:
        db.query_db(insert_content_string)
    else:
        print(insert_content_string)
        
    logging.info("Vote content data successfully inserted")
    

if __name__ == "__main__":
    isApply = True
    insert_text_data(isApply)
    insert_pv_data(isApply)
    insert_content_data(isApply)




