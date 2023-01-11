import get_parlementarian as gp

parl_place = gp.get_all_parl_place()
brux = parl_place["BRU"].copy()
strasb = parl_place["STR"].copy()

parl_info = gp.get_parl_info()

print("ok")


bru_ids_sieges = {}
str_ids_sieges = {}
for parl_id in parl_info.keys():
    parl_info_name = parl_info[parl_id]["fullName"]

    name_surname = " ".join(parl_info_name.split(" ")[1:]) + " " + parl_info_name.split(" ")[0].upper()

    ### BRUXELLE ###
    bru_all_siege = []
    for bru_siege_id in brux.keys():
        print(bru_siege_id + " - " + brux[bru_siege_id] + "::" + name_surname)
        if name_surname[0:len(brux[bru_siege_id])] == brux[bru_siege_id]:
            bru_all_siege.append(bru_siege_id)

    if len(bru_all_siege) > 1 or len(bru_all_siege) == 0:
        print("WARNING")
    else:
        bru_ids_sieges[parl_id] = [bru_all_siege[0], name_surname, brux[bru_all_siege[0]]]

    ### STRASBOURG ###
    str_all_siege = []
    for str_siege_id in strasb.keys():
        print(str_siege_id + " - " + strasb[str_siege_id] + "::" + name_surname)
        if name_surname[0:len(strasb[str_siege_id])] == strasb[str_siege_id]:
            str_all_siege.append(str_siege_id)

    if len(str_all_siege) > 1 or len(str_all_siege) == 0:
        print("WARNING")
    else:
        str_ids_sieges[parl_id] = [str_all_siege[0], name_surname, strasb[str_all_siege[0]]]
    
print(bru_ids_sieges)
print(str_ids_sieges)

with open("transco_parl_bru.csv", "w") as bru_csv:
    bru_csv.write("parl_id,siege_id,name_surname,name_pdf\n")
    for parl_id in bru_ids_sieges.keys():
        bru_info = bru_ids_sieges[parl_id]
        bru_csv.write(str(parl_id) + "," + ",".join(bru_info) + "\n")

with open("transco_parl_str.csv", "w") as str_csv:
    str_csv.write("parl_id,siege_id,name_surname,name_pdf\n")
    for parl_id in str_ids_sieges.keys():
        str_info = str_ids_sieges[parl_id]
        str_csv.write(str(parl_id) + "," + ",".join(str_info) + "\n")




