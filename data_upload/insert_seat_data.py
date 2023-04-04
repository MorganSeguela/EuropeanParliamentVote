#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# The main objective of this program is to insert SEAT information in DB

# DB driver package
import db_tools as db

# Log packges
import logging


def retrieve_parliament_data():
    """Parliament data (id, name, abbreviation)

    Yields:
        tuple: (id, name, abbreviation)
    """
    parliament_data = [(0, 'Brussels', 'BRU'), (1, 'Strasbourg', 'STR')]
    for one_parl in parliament_data:
        yield one_parl


def insert_parliament_data():
    """Insert parliament data in DB
    """
    logging.info("Inserting parliament data in DB...")
    insert_parliament_string = ""

    for one_parl in retrieve_parliament_data():
        insert_parliament_string += "INSERT INTO project.parliament\n\tVALUES ({0}, \'{1}\', \'{2}\');\n".format(*one_parl)
    insert_parliament_string += "COMMIT:"

    print(insert_parliament_string)

    # db.query_db(insert_parliament_string)

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


def insert_seat_data():
    logging.info("Inserting seat data in DB...")
    insert_seat_string = ""
    for one_seat in retrieve_seat_data():
        one_seat[6] = "\'{}\'".format(one_seat[5])
        insert_seat_string += "INSERT INTO project.seat\n\tVALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7});\n".format(*one_seat)
    
    insert_seat_string += "COMMIT;"
    print(insert_seat_string)
    # db.query_db(insert_seat_string)
    logging.info("Seat data successfully inserted")


if __name__ == "__main__":
    insert_parliament_data()
    insert_seat_data()

