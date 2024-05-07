from datetime import datetime

TAX_ID = "1521309633"
ROUTING_NUMBER = "054000030"
TR_NUMBER = "071921891"

def ach_header():
    creation_date = datetime.now()
    # print(f"date {creation_date}")
    cdate = f"{creation_date.year - 2000}{creation_date.month:02d}{creation_date.day:02d}"
    ctime = f"{creation_date.hour:02d}{creation_date.minute:02d}"
    # print(f"cdate = {cdate}")
    # print(f"ctime = {ctime}")
    file_id = "1"
    bank = "PNC BANK"
    company = "HazTrain Inc."
    ref = " "
    # creation_time
    ret = f"101 {ROUTING_NUMBER}{TAX_ID}{cdate}{ctime}{file_id}094101{bank:>23}{company:>23}{ref:>8}"
    assert (len(ret) == 94)
    # print(f"Len = {len(x)}")
    return ret


def company_batch_header():
    company = "HazTrain Inc."
    notes = "Payment"
    description = "Payment"

    creation_date = datetime.now()
    cdate = f"{creation_date.year - 2000}{creation_date.month:02d}{creation_date.day:02d}"
    batch = 1
    ret = f"5220{company:>16}{notes:>20}{TAX_ID}PPD{description:>10}{cdate}{cdate}{" ":>3}1{ROUTING_NUMBER[:-1]}{batch:07d}"
    assert (len(ret) == 94)
    # print(f"len = {len(ret)}")
    return ret


def trim_string(str, max_len):
    if len(str) > max_len:
        return str[:max_len]
    return str


class payment:
    def __init__(self, route, account, amount, id, name):
        self.ROUTING_NUMBER = route
        self.account_number = account
        self.amount = amount

        self.id_number = trim_string(id, 15)

        self.name = trim_string(name, 22)

    def entry_detail(self, transaction_number):
        trace = ROUTING_NUMBER[:-1] + f"{transaction_number:07d}"
        ret = f"622{self.ROUTING_NUMBER:>9}{self.account_number:<17}{self.amount:010.2f}{self.id_number:>15}{self.name:>22}  0{trace}"
        # print(f"entry len = {len(ret)}")
        assert (len(ret) == 94)
        return ret


def make_ach_payment():
    print("Make ACH Payment")
    print(ach_header())
    print(company_batch_header())

    pay = payment("123456789", "my account", 3.14, "my id", "Jeffrey Wayne Monroe")
    print(pay.entry_detail(7))

    print(trim_string("123456789", 7))