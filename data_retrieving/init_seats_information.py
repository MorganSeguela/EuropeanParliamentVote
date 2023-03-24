#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# Log package
import logging

# Access and Parse packages 
from selenium import webdriver
from bs4 import BeautifulSoup as bs

from time import sleep


class seat_available_info:
    """Class of seat information not gathered

    Raises:
        Exception: The init input does not correspond to expected ones
    """
    parl_council_seat_id = {
        "bru": [
            1, 2,
            23, 24, 25, 26,
            51, 52, 53, 54, 55,
            88, 89, 90, 91, 92,
            123, 124, 125, 126, 127,
            171, 172, 173, 174,
            216, 217
        ],
        "str": [
            1, 2,
            23, 24,
            45, 46, 47,
            76, 77, 78, 79, 
            119, 120, 121, 122,
            167, 168, 169, 170, 171,
            224, 225, 226, 227, 228, 229,
            293, 294, 295, 296, 297, 298
        ]
    }

    parl_commission_seat_id = {
        "bru": [
            21, 22,
            46, 47, 48, 49,
            81, 82, 83, 84, 85,
            129, 130, 131, 132, 133,
            166, 167, 168, 169, 170,
            212, 213, 214, 215,
            265, 266
        ],
        "str": [
            21, 22,
            43, 44,
            73, 74, 75, 
            115, 116, 117, 118,
            163, 164, 165, 166,
            219, 220, 221, 222, 223,
            287, 288, 289, 290, 291, 292,
            363, 364, 365, 366, 367, 368
        ]
    }

    def __init__(self, parl_abrv):
        """Initialize which parliament is taken into account.

        Args:
            parl_abrv (str): "str" (Strasbourg) or "bru" (Brussels)

        Raises:
            Exception: The init input does not correspond to expected ones
        """
        self.council_seat_id = self.parl_council_seat_id[parl_abrv]
        self.commission_seat_id = self.parl_commission_seat_id[parl_abrv]

        self.parliament_name = None
        self.parliament_id = -1

        if parl_abrv == "str":
            self.parliament_name = "Strasbourg"
            self.parliament_id = 1
        elif parl_abrv == "bru":
            self.parliament_name = "Brussels"
            self.parliament_id = 0

        if self.parliament_name == None:
            raise Exception("Parliament abreviation should be \"str\" for Strasbourg or \"bru\" for Brussels, you wrote: " + parl_abrv)
    
    def seat_use(self, seat_id):
        """Given a seat id, retrieve the use of the seat

        Args:
            seat_id (int): seat id

        Returns:
            str: Usage of the seat between "Council", "Commission", "Parliamentarian"
        """
        if seat_id in self.council_seat_id:
            return "Council"
        elif seat_id in self.commission_seat_id:
            return "Commission"
        else:
            return "Parliamentarian"


def retrieve_page_source(url):
    """Access to the given url and retrieve its html.
    It is worth noting that we use Firefox without headless, to run the javascript to be able to parse the seats map

    Args:
        url (str): url to the website (here interactive plan)

    Returns:
        str: html of the given url website
    """
    fireDriver = webdriver.Firefox()
    fireDriver.get(url)
    sleep(10)
    hemi_node = fireDriver.page_source
    fireDriver.close()

    return hemi_node


def parse_seat(html_str):
    """Parse and retrieve seats information

    Args:
        html_str (str): String of the html parsed before

    Returns:
        (vect, dict): 
            - vect: canvas size (size_x, size_y)
            - dict: seat_id: [posx, posy]
    """
    seat_bs = bs(html_str, "html.parser")
    seat_map_canvas = seat_bs.find("div", {"class": "erpl_hemicycle-map-canvas"})
    seat_map_canvas_svg = seat_map_canvas.svg

    canvas_size = (seat_map_canvas_svg["width"][:-2], seat_map_canvas_svg["height"][:-2])

    dict_seat_info = {}

    for circle in seat_map_canvas_svg.children:
        if circle.name == "circle":    
            seat_id = int(circle["id"])
            seat_cx = circle["cx"]
            seat_cy = circle["cy"]
            dict_seat_info[seat_id] = [seat_cx, seat_cy]
    
    return (canvas_size, dict_seat_info)


def gen_all_parl():
    """Generator of each parliament abbreviation

    Yields:
        str: Parliament abbreviation
    """
    parl_abrvs = ["str", "bru"]
    for val in parl_abrvs:
        yield val


def regroup_all_seats_data():
    """Retrieve seats information from the parliament interactive plan.
    Parse seats html to retrieve seat (x,y) positions and the canvas size (width, height).
    Each seat is a vector (id, posx, posy, width, height, seat_use, parliament_id),
    stored in a list of seats.

    Returns:
        List[Vect()]: List of Seats informations: [(id, posx, posy, width, height, seat_use, parliament_id)]
    """
    all_data = []
    for parl_abrv in gen_all_parl():
            cur_url = "https://www.europarl.europa.eu/erpl-public/hemicycle/index.htm?lang=en&loc={}#".format(parl_abrv)

            logging.warning("Retrieving data from:\n{}\nDo not touch anything".format(cur_url))

            str_seat_info = retrieve_page_source(cur_url)
            canvas_size, seat_info = parse_seat(str_seat_info)

            parl_info = seat_available_info(parl_abrv)

            for seat_id in seat_info.keys():
                valx, valy = seat_info[seat_id]
                seat_use = parl_info.seat_use(seat_id=seat_id)
                cur_data=[
                    str(seat_id), valx, valy, 
                    canvas_size[0], canvas_size[1],
                    seat_use, str(parl_info.parliament_id)
                ]
                all_data.append(cur_data)
    return all_data


def write_data_in_file(all_data, filepath):
    """Write seat data in a file.

    Args:
        all_data (List[Vect()]): List of Seats information
        filepath (str): Filepath where to write data
    """
    str_all_data = ""

    for seat_data in all_data:
        str_all_data += ",".join(seat_data) + "\n"
    
    with open(filepath, "w") as seat_file:
        seat_file.write(str_all_data)
    


if __name__ == '__main__':
    """
    Running this file permits to retrieve parliament seats data from the website, and write them in ../tmp/seat_info.csv

    We chose to use selenium with Firefox (without headless option), as it is the easiest way to access data with graphic parameters to execute the javascript in order to be able to retrieve seats map.
    """
    
    seats_data = regroup_all_seats_data()
    write_data_in_file(seats_data, "tmp/stage_1/seat_info.csv")
    logging.warning("Retrieving Done")
