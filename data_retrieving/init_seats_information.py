import logging

from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup as bs


class seat_available_info:
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
        if seat_id in self.council_seat_id:
            return "Council"
        elif seat_id in self.commission_seat_id:
            return "Commission"
        else:
            return "Parliamentarian"


def retrieve_page_source(url):
    fireDriver = webdriver.Firefox()
    fireDriver.get(url)
    sleep(10)
    hemi_node = fireDriver.page_source
    fireDriver.close()

    return hemi_node

def parse_seat(html_str):
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
    parl_abrvs = ["str", "bru"]
    for val in parl_abrvs:
        yield val


if __name__ == '__main__':
    str_all_data = ""
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
            str_all_data += ",".join(cur_data) + "\n"
            
    with open("tmp/seat_info.csv", "w") as seat_file:
        seat_file.write(str_all_data)

    logging.warning("Retrieving Done")
    # url_seat_info_str = "https://www.europarl.europa.eu/erpl-public/hemicycle/index.htm?lang=en&loc=str#"
    # url_seat_info_bru = "https://www.europarl.europa.eu/erpl-public/hemicycle/index.htm?lang=en&loc=bru#"
    
    # str_seat_info_bru = retrieve_page_source(url_seat_info_bru)
    # canvas_size, seat_info = parse_seat(str_seat_info_bru)

    # parl_info = seat_available_info("str")

    # all_data = []

    # for seat_id in seat_info.keys():
    #     valx, valy = seat_info[seat_id]
    #     seat_use = parl_info.seat_use(seat_id=seat_id)
    #     all_data.append(
    #         [
    #         str(seat_id), valx, valy, 
    #         canvas_size[0], canvas_size[1],
    #         seat_use, parl_info.parliament_id
    #         ]
    #     )
    # print(all_data)
    



