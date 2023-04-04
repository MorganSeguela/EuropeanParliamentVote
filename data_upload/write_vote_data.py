#!/#!/usr/bin/python

import psycopg2
import os
import re
import json
from config import config

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


def extract_id_voter_pg(verification, pg_vote):
    """Retrieve parliamentarian id in the political group vote.
    In fact, for each vote value, parliamentarian are grouped in political group

    Args:
        verification (parl_id_seat, exist_parl_id): vector of data to verify if parliamentarian already taken into account
        pg_vote (dict): dictionnary of each vote value with pg name as key

    Returns:
        vect(success_result, fail_result): parliamentarian id and name for vote
    """
    seat_data, db_data = verification

    result = []
    fail_result = {"notInDb": [],
                   "noSeat": []}
    
    for  cur_pg in pg_vote:
        parl_id = cur_pg["PersId"]
        parl_name = cur_pg["Name"]

        # Verify result
        hasSeat = parl_id in seat_data.keys()
        isInDB = int(parl_id) in db_data

        if isInDB and hasSeat:
            result.append(parl_id)
        else:
            if not isInDB:
                fail_result["notInDb"].append([parl_id, parl_name])
            if not hasSeat:
                fail_result["noSeat"].append([parl_id, parl_name])
    return (result, fail_result)


def is_successfull(failed_data):
    """Verify if all parliamentarian is found

    Args:
        failed_data (dict): dictionary of failed_result

    Returns:
        boolean: only successful result
    """
    is_success = True
    for reason in failed_data.keys():
        if is_success:
            is_success = len(failed_data[reason]) == 0
    return is_success


def extract_id_voter(verifiation, vote):
    """Extract parliamentarian id for each vote value

    Args:
        verifiation (parl_id_seat, exist_parl_id): vector of data to verify if parliamentarian already taken into account
        vote (dict): dictionary of vote value

    Returns:
        vect(dict, dict): successful and fail result of parliamentarian id 
    """
    tmp_success = []
    tmp_fail = {"notInDb":[],
                "noSeat" :[]}
    for pg_name in vote.keys():
        for_pg_data = vote[pg_name]
        success_result, fail_result = extract_id_voter_pg(verifiation, for_pg_data)
        tmp_success.extend(success_result)
        tmp_fail["notInDb"].extend(fail_result["notInDb"])
        tmp_fail["noSeat"].extend(fail_result["noSeat"])

    return (tmp_success, tmp_fail)


def extract_success_fail_vote(cur_vote, parl_id_seat, exist_parl_id):
    """Extract parliamentarian id of each vote value

    Args:
        cur_vote (dict): raw vote for each vote id
        parl_id_seat (dict): keys(parliamentarian id) and value seat id
        exist_parl_id (list): list of parliamentarian id in the db

    Returns:
        (dict, dict, boolean): vote_success, vote_fail, isSuccess
    """
    list_vote_value = ["forDetails", "againstDetails", "abstentionDetails"]

    vote_success = {}
    vote_fail = {}

    isSuccess = True
    for vote_value in list_of_votes:      
        if vote_value in cur_vote.keys():
            tmp_success, tmp_fail = extract_id_voter((parl_id_seat, exist_parl_id), cur_vote[vote_value])
            vote_success[list_vote_value.index(vote_value)] = tmp_success
            vote_fail[list_vote_value.index(vote_value)] = tmp_fail
            if isSuccess:
                isSuccess = is_successfull(tmp_fail)

    return (vote_success, vote_fail, isSuccess)


def extract_intention_vote(cur_vote):
    """Extract intention vote from vote result

    Args:
        cur_vote (dict): dictionary of result for each text_id

    Returns:
        dict: {"parliamentarian id": intention vote value}
    """
    
    intentions_dict = {}
    if "intentions" in cur_vote.keys():
        intention_data = cur_vote["intentions"]

        for cur_choice in intention_data.keys():
            if cur_choice == "For":
                for_data = intention_data[cur_choice]
                for parl_for in for_data:
                    intentions_dict[parl_for["PersId"]] = 0
            if cur_choice == "Against":
                for_data = intention_data[cur_choice]
                for parl_for in for_data:
                    intentions_dict[parl_for["PersId"]] = 1
            if cur_choice == "Abstention":
                for_data = intention_data[cur_choice]
                for parl_for in for_data:
                    intentions_dict[parl_for["PersId"]] = 2

    return intentions_dict

def insert_text_str(text_id, old_text, text_info):
    """Write text information to insert in DB

    Args:
        text_id (int): text identifier
        old_text (list): list of text id already in DB
        text_info (vect): vector of text information

    Returns:
        str: string to insert text information in DB
    """
    text = "-- text\n"
    if text_id not in old_text:
        text += "INSERT INTO project.text VALUES (" + (",".join((str(val) for val in text_info))) + ");\n"
    return text

def insert_vote_str(cur_vote, vote_success, intentions_dict):
    """Write string to insert vote information in DB

    Args:
        cur_vote (dict): vote information
        vote_success (dict): vote value and parliamentarian id
        intentions_dict (dict): parliamentarian id and intention vote

    Returns:
        str: text to insert vote data
    """

    text = "-- votes\n"
    for vote_value in vote_success.keys():
        vote_result = vote_success[vote_value]
        for parl_id in vote_result:
            intention_vote = "NULL"
            if parl_id in intentions_dict.keys():
                intention_vote = intentions_dict[parl_id]
            value = (
                parl_id, cur_vote["id"], 
                handle_str_sql(cur_vote["date"]),
                vote_value,
                intention_vote
                )
            text += "INSERT INTO project.tmp_votes VALUES (" + (",".join((str(val) for val in value))) + ");\n"
    
    return text


def store_fail_date(cur_vote, vote_fail, intentions_dict, text_info):
    """Data to store when vote fail (if parliamentarian not in DB)

    Args:
        cur_vote (dict): Information of the current vote
        vote_fail (dict): reason of the failure and parliamentarian information
        intentions_dict (dict): parliamentarian id and vote intention
        text_info (vect): vector of text information

    Returns:
        list(vect): list of each failure with their information
    """
    fail_result = []
    for vote_value in vote_fail.keys():
        vote_result = vote_fail[vote_value]
        for fail_reason in vote_result.keys():
            fail_vote_result = vote_result[fail_reason]
            for parl_id, parl_name in fail_vote_result:
                intention_vote = "NULL"
                if parl_id in intentions_dict.keys():
                    intention_vote = intentions_dict[parl_id]
                fail_result.append(
                    (
                    handle_str_sql(fail_reason),
                    handle_str_sql(parl_name),
                    parl_id, cur_vote["id"],
                    cur_vote["date"], vote_value,
                    intention_vote, "NULL"
                    ) + text_info
                )
    return fail_result


def read_parl_data_file(root_data_dir):
    """Retrieve parliament data information

    Args:
        root_data_dir (str): directory path to these data

    Returns:
        dict: parliamentarian information
    """
    all_parl_files = [cur_parl_file for cur_parl_file in os.listdir(root_data_dir) if "Parlementarian" in cur_parl_file]

    parl_data = {}
    for cur_parl_file in all_parl_files:
        tmp_data = None
        with open("tmp/" + cur_parl_file, "r") as parl_file:
            tmp_data = json.load(parl_file)

        for parl_id in tmp_data.keys():
            if parl_id not in parl_data.keys():
                parl_data[parl_id] = tmp_data[parl_id]
            else:
                new_data = tmp_data[parl_id]
                old_data = parl_data[parl_id]
                if new_data["BRU_siege"] != old_data["BRU_siege"]:
                    parl_data[parl_id]["BRU_siege"] = new_data["BRU_siege"]
                if new_data["STR_siege"] != old_data["STR_siege"]:
                    parl_data[parl_id]["STR_siege"] = new_data["STR_siege"]
    return parl_data


def retrieve_bru_siege(root_data_dir):
    """Retrieve brussels siege from file from root_data_dir directory

    Args:
        root_data_dir (str): directory path to temporary data

    Returns:
        dict: parliamentarian: siege_id
    """
    parl_data = read_parl_data_file(root_data_dir)
    parl_id_seat = {}
    for cur_parl in parl_data.keys():
        parl_id_seat[cur_parl] = parl_data[cur_parl]["BRU_siege"]

    return parl_id_seat


if __name__ == '__main__':
    current_dir = "tmp/"
    all_files = [cur_file for cur_file in os.listdir("tmp/") if "Votes" in cur_file]

    parl_id_seat = retrieve_bru_siege(current_dir)


    query_result = query_db("SELECT parliamentarian_id from project.parliamentarian;")
    exist_parl_id = [v[0] for v in query_result]

    query_result = query_db("SELECT text_id from project.text;")
    old_text = [v[0] for v in query_result]

    # print(exist_parl_id)

    # success_result = []
    # fail_result = []


    for cur_file in all_files:
        vote_data = None
        success_result = []
        fail_result = []
        text_result = []
        final_text = ""

        with open(current_dir + cur_file, "r") as vote_json:
            vote_data = json.load(vote_json)
        
        if vote_data != None:
            list_of_votes = vote_data["data"]
            for cur_vote in list_of_votes:
                text_info = (
                    cur_vote["id"],
                    handle_str_sql(cur_vote["reference"]),
                    handle_str_sql(cur_vote["description"]),
                    handle_str_sql(cur_vote["url"])
                )

                intentions_dict = extract_intention_vote(cur_vote)

                vote_success, vote_fail, isSuccess = extract_success_fail_vote(cur_vote, parl_id_seat, exist_parl_id)
                
                if isSuccess:
                    text = insert_text_str(cur_vote["id"], old_text, text_info)
                    text += insert_vote_str(cur_vote, vote_success, intentions_dict)
                    text += "\nCOMMIT;\n"
                    query_db(text)
                    final_text += text
                            
                else:
                    fail_result.extend(store_fail_date(cur_vote, vote_fail, intentions_dict, text_info))
        
        no_ext_file = cur_file[0:len(cur_file) - 4]
        if len(fail_result) > 0:
            text = ""
            for info in fail_result:
                text += ",".join((str(val) for val in info)) + "\n"

            with open("vote_fail/" + no_ext_file + "csv", "w") as fail_file:
                fail_file.write(text)

        if len(final_text) > 0:
            with open("vote_success/" + no_ext_file + "sql", "w") as success_file:
                success_file.write(final_text)
            
    print("end input data")

