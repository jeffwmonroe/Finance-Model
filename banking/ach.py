from datetime import datetime
from config import config
import pandas as pd

from banking.natcha import Natcha



def make_ach_payment():
    print("Make ACH Payment")

    payment_file = f"{config['ach_dir']}/ACH_Payment.xlsx"
    natcha_file = f"{config['processed_dir']}/natcha_file.txt"

    natcha = Natcha()
    natcha.add_payments(payment_file)

    with open(natcha_file, "w") as f:
        natcha.write_to_file(f)

    # pay = payment("123456789", "my account", 3.14, "my id", "Jeffrey Wayne Monroe")
    # print(pay.entry_detail(7))

    # print(trim_string("123456789", 7))