from datetime import datetime
from config import config
import pandas as pd

from banking.natcha import Natcha



def make_ach_payment(effective_date: str):
    if effective_date is None:
        effective_date = datetime.now()
    else:
        effective_date = datetime.strptime(effective_date, '%m/%d/%Y')
    print(f"Make ACH Payment: {effective_date}")

    payment_file = f"{config['ach_dir']}/ACH_Payment.xlsx"
    natcha_file = f"{config['processed_dir']}/natcha_file.txt"

    natcha = Natcha(effective_date)
    natcha.add_payments(payment_file)

    with open(natcha_file, "w") as f:
        natcha.write_to_file(f)

    print(f'Total amount of ACH Payment: ${natcha.total_amount():,.2f}')
    # pay = payment("123456789", "my account", 3.14, "my id", "Jeffrey Wayne Monroe")
    # print(pay.entry_detail(7))

    # print(trim_string("123456789", 7))