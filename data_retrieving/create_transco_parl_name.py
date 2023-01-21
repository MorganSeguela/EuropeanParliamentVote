import get_parlementarian as gp

def get_transco_info_siege():

    parl_place = gp.get_all_parl_place()
    brux = parl_place["BRU"].copy()
    strasb = parl_place["STR"].copy()
    
    parl_info = gp.get_parl_info()
    
    bru_ids_sieges = {}
    bru_not_found = {}

    str_ids_sieges = {}
    str_not_found = {}

    return_info = {}
    return_info["BRU"] = {}
    return_info["STR"] = {}

    for parl_id in parl_info.keys():
        parl_info_name = parl_info[parl_id]["fullName"]

        name_surname = " ".join(parl_info_name.split(" ")[1:]) + " " + parl_info_name.split(" ")[0].upper()

        ### BRUXELLE ###
        bru_all_siege = []
        for bru_siege_id in brux.keys():
            if name_surname[0:len(brux[bru_siege_id])] == brux[bru_siege_id]:
                bru_all_siege.append(bru_siege_id)

        if len(bru_all_siege) > 1 or len(bru_all_siege) == 0:
            bru_not_found[parl_id] = name_surname
        else:
            bru_ids_sieges[parl_id] = [bru_all_siege[0], name_surname, brux[bru_all_siege[0]]]

        ### STRASBOURG ###
        str_all_siege = []
        for str_siege_id in strasb.keys():
            if name_surname[0:len(strasb[str_siege_id])] == strasb[str_siege_id]:
                str_all_siege.append(str_siege_id)

        if len(str_all_siege) > 1 or len(str_all_siege) == 0:
            str_not_found[parl_id] = name_surname
        else:
            str_ids_sieges[parl_id] = [str_all_siege[0], name_surname, strasb[str_all_siege[0]]]

    return_info["BRU"] = [bru_ids_sieges, bru_not_found]
    return_info["STR"] = [str_ids_sieges, str_not_found]

    return return_info


if __name__ == "__main__":

    pathfile = "/home/morgan/Documents/EP_project/transco/"

    all_transco = get_transco_info_siege()

    bru_ids_sieges, bru_not_found = all_transco["BRU"]
    str_ids_sieges, str_not_found = all_transco["STR"]

    with open(pathfile + "transco_parl_bru.csv", "w") as bru_csv:
        bru_csv.write("parl_id,siege_id,name_surname,name_pdf\n")
        for parl_id in bru_ids_sieges.keys():
            bru_info = bru_ids_sieges[parl_id]
            bru_csv.write(str(parl_id) + "," + ",".join(bru_info) + "\n")

    with open(pathfile + "fail_transco_parl_bru.csv", "w") as bru_csv:
        bru_csv.write("parl_id,name_surname\n")
        for parl_id in bru_not_found.keys():
            bru_name = bru_not_found[parl_id]
            bru_csv.write(str(parl_id) + "," + bru_name + "\n")

    with open(pathfile + "transco_parl_str.csv", "w") as str_csv:
        str_csv.write("parl_id,siege_id,name_surname,name_pdf\n")
        for parl_id in str_ids_sieges.keys():
            str_info = str_ids_sieges[parl_id]
            str_csv.write(str(parl_id) + "," + ",".join(str_info) + "\n")

    with open(pathfile + "fail_transco_parl_str.csv", "w") as str_csv:
        str_csv.write("parl_id,name_surname\n")
        for parl_id in str_not_found.keys():
            str_name = str_not_found[parl_id]
            str_csv.write(str(parl_id) + "," + str_name + "\n")



