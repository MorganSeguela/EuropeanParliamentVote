
# DB driver package
import db_tools as db

# Log packges
import logging

# Json file management
import json

# File management
import os

# Date time package for filename
from datetime import datetime

def get_db_parl_id():
    """Retrieve Parliamentarian ID are in the database

    Returns:
        List[Int]: List of parliamentarian ID
    """
    query_result = db.query_db("SELECT parliamentarian_id from project.parliamentarian;")
    return [v[0] for v in query_result]


def get_db_seat_parl_id():
    """Retrieve parliamentarian ID for each seat place date

    Returns:
        Dict: {Date: List[Int]}
            List[Int]: List of parliamentarian ID
    """
    query_result = db.query_db("SELECT parliamentarian_id, date_sit FROM project.sits_on;")
    res_dict = {}
    for tuple in query_result:
        if tuple[1] not in res_dict.keys():
            res_dict[tuple[1]] = []
        res_dict[tuple[1]].append(tuple[0])
    return res_dict


def gen_vote_files():
    """Generator of vote result filepath

    Yields:
        str: filepath of vote result data
    """
    start_dir = "tmp/stage_2/"
    for files in [this_file for this_file in os.listdir(start_dir) if "Vote_data" in this_file]:
        yield start_dir + files


def verify_seat(seat_data, parl_id):
    """Verify which seats date this parliamentarian has

    Args:
        seat_data (dict): {date: List[int]} - List of parliamentarian ID 
        parl_id (Int): Parliamentarian to verify

    Returns:
        List[Date]: List of date where parliamentarian has seat
    """
    data_res = []
    for ds in seat_data.keys():
        if parl_id in seat_data[ds]:
            data_res.append(ds)
    return data_res


def ext_int_vote(intention_data):
    """Extract intention vote

    Args:
        intention_data (dict): Values of "intention"

    Returns:
        dict: {parliamentarian ID: intenton value}
    """
    intention_res = {}
    for int_vv in intention_data.keys():
        for parl_id in intention_data[int_vv].keys():
            intention_res[parl_id] = int_vv
    return intention_res

def ext_verify_vote(vote_data, verification):
    """Extract vote for each content id and verify if this content id can be added.
    A Content is considered successfull if all its parliamentarian that voted are in DB and has seat

    Args:
        vote_data (dict): values of each content id 
        verification (List, Dict): List of parliamentarian in DB and dictionary of sit date and parl ID

    Returns:
        (List[List], List[List], Boolean): List of success tuple, List of fail tuple, and boolean if content is success
    """
    parl_db, seat_db = verification
    IsSuccess = True
    res = []

    prs_date = list(seat_db.keys())

    tmp_fail = {"notInDb":[],
                "noSeat" :[]}

    int_vote = ext_int_vote(vote_data["intention"])

    for id_vv in vote_data["vote"].keys():
        voters_dict = vote_data["vote"][id_vv]

        for parl_id in voters_dict.keys():
            isInDB = int(parl_id) in parl_db
            whichDate = verify_seat(seat_db, int(parl_id))

            prs_date = [good_date for good_date in whichDate if good_date in prs_date]

            parl_int = "NULL"
            if parl_id in int_vote.keys():
                parl_int = int_vote[parl_id]
            
            if isInDB and prs_date:
                res.append([parl_id, id_vv, parl_int])
            else:
                IsSuccess = False
                if not isInDB:
                    tmp_fail["notInDb"].append([parl_id, id_vv, parl_int, voters_dict[parl_id], "Not in database"])
                if not prs_date:
                    tmp_fail["noSeat"].append([parl_id, id_vv, parl_int, voters_dict[parl_id], "Has no seat in DB"])

    return (res, tmp_fail, IsSuccess)


def parse_vote_data(verification):
    """Retrieve vote result and verify if the vote can be added in DB or not.

    Args:
        verification (List, Dict): List of parliamentarian in DB and dictionary of sit date and parl ID

    Returns:
        (List[List], List[List]): List of successfull data, List of failure data
    """
    res_suc = []
    res_fail = []
    for vote_file in gen_vote_files():
        cur_file = {}
        with open(vote_file, "r") as vote_fc:
            cur_file = json.load(vote_fc)
        for content_id in cur_file.keys():

            tmp_res, tmp_fail, isSuccess = ext_verify_vote(cur_file[content_id], verification)
            if isSuccess:
                for tuple in tmp_res:
                    tuple.insert(1, content_id)
                    res_suc.append(tuple)
            else:
                notInDBData = tmp_fail["notInDb"]
                for tuple in notInDBData:
                    tuple.insert(1,content_id)
                    res_fail.append(tuple)

                noSeatDB = tmp_fail["noSeat"]
                for tuple in noSeatDB:
                    tuple.insert(1,content_id)
                    res_fail.append(tuple)
    return (res_suc, res_fail)
                    

def insert_db(data, isApply=False):
    """Insert data in DB

    Args:
        data (List[List]): List of tuple to insert
        isApply (bool, optional): insert data in DB. Defaults to False.
    """
    logging.info("Inserting vote result data...")
    insert_vr_string = ""
    for tuple in data:
        insert_vr_string += "INSERT INTO project.votes\n\tVALUES ({0}, {1}, {2}, {3});\n".format(*tuple)

    insert_vr_string += "COMMIT;"

    if isApply:
        db.query_db(insert_vr_string)
    else:
        print(insert_vr_string)

    logging.info("Vote result data successfully inserted")


def write_file(data, isApply=False):
    """Write data in a file

    Args:
        data (List[List]): List of data to write
        isApply (bool, optional): Write data. Defaults to False.
    """
    logging.info("Writing failure file...")
    file_content_str = ""

    for tuple in data:
        file_content_str += ",".join(tuple) + "\n"
    
    file_name = "tmp/stage_2/Fail_vote_{}.csv".format(datetime.now().strftime("%Y%m%d"))

    if isApply:
        with open(file_name, "w") as wf:
            wf.write(file_content_str)
    else:
        print(file_content_str)


if __name__ == "__main__":
    parl_in_db = get_db_parl_id()
    db_seat_parl = get_db_seat_parl_id()
    success, fail = parse_vote_data((parl_in_db, db_seat_parl))
    isApply = True
    insert_db(success)
    write_file(fail, isApply)
