import pandas as pd
# ToDo get this from data

def get_instructor_info():
    pto = 6.666 * 24 / 8

    instructor_list = ["Czysz", "Reising", "Wood", "Gorirossi", "McCrea", "Della-Volle", "Spheeris"]
    instructor_email = ["timczysz@haztrain.com", "markreising@haztrain.com", "stevenwood@haztrain.com",
                        "josephgorirossi@haztrain.com","joshmccrea@haztrain.com", "jdvsdv604@hotmail.com",
                        "paulaspheeris@haztrain.com"]
    instructor_pto = [0, pto, pto, pto, pto, 0, 0]
    instructor_pay = [0, 80000, 124800, 75504, 92400, 0, 0
                      ]
    inst_df = pd.DataFrame({"Virtual": [0 ] *len(instructor_list),
                            "In Person": [0 ] *len(instructor_list),
                            "Travel": [0 ] *len(instructor_list),
                            "Holiday": [9 ] *len(instructor_list),
                            "PTO": instructor_pto,
                            "Sick": [0 ] *len(instructor_list),
                            # "Pay": instructor_pay,
                            },
                           index=instructor_list)

    inst_dict = {email: name for name, email in zip(instructor_list, instructor_email)}
    # print(f'a = {a}')
    return inst_dict, inst_df
