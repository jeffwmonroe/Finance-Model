from config import config
import pandas as pd
from datetime import datetime
from banking.payment_detail import PaymentDetail

HAZTRAIN_TAX_ID = "521309633"
PNC_ROUTING_NUMBER = "054000030"
PNC_TR_NUMBER = "071921891"
COMPANY_NAME = "HazTrain Inc"
COMPANY_ID = 1521309633

class Natcha:

    def __init__(self, effective_date: datetime):
        self.effective_date = effective_date
        self.receiver_df = pd.read_excel(config['ack_receivers'], dtype={'Routing Number': str,
                                                                         'Account Number': str,
                                                                         'Customer ID': str,
                                                                         })
        self.receiver_df["Customer ID"] = self.receiver_df["Customer ID"].fillna("")
        # print("Natcha")
        # print(self.receiver_df)
        # print(self.receiver_df.dtypes)
        self.creation_date = datetime.now()
        self.payments = []

    def add_payments(self, payment_file):
        # print("Add_payments")
        payment_df = pd.read_excel(payment_file, dtype={
            'Description': str,
            'Amount': float,
            # 'Invoice Date': datetime,
        })
        payment_df['Description'] = payment_df['Description'].fillna('')
        # print(payment_df)
        # print(payment_df.dtypes)

        joined_df = payment_df.merge(self.receiver_df, left_on="Vendor ID", right_on="Vendor ID", how="left")
        print("joined DF:")
        print(joined_df)
        # print(joined_df.dtypes)
        # print("Vendors:")
        # if joined_df.loc[:, "Vendor Name"].isnull().sum() > 0:
        #     print("Vendor not found")
        assert joined_df.loc[:, "Vendor Name"].isnull().sum() == 0, "A vendor not found in receivers"
        assert joined_df.loc[:, "Vendor Type"].isnull().sum() == 0, "A vendor does not have a vendor type"
        assert joined_df.loc[:, "Account Type"].isnull().sum() == 0, "A vendor does not have an account type"
        assert joined_df.loc[:, "Routing Number"].isnull().sum() == 0, "A vendor does not have a routing number"
        assert joined_df.loc[:, "Account Number"].isnull().sum() == 0, "A vendor does not have an account number"

        for i in range(len(joined_df.index)):
            # print(f'i={i} {joined_df.loc[i, "Vendor Name"]}')
            detail = PaymentDetail(joined_df.loc[i, :], i + 1)
            # print(detail.entry_detail_record())
            # print(detail.addenda_record())
            self.payments.append(detail)

    def header(self):
        assert len(HAZTRAIN_TAX_ID) == 9, "Tax ID must be 9 characters in length"
        return_value = (
            "1"
            "01"
            f"{PNC_ROUTING_NUMBER:>10}"
            f"1{HAZTRAIN_TAX_ID:}"
            f"{self.creation_date.year - 2000}{self.creation_date.month:02d}{self.creation_date.day:02d}"
            f"{self.creation_date.hour:02d}{self.creation_date.minute:02d}"
            "1"  # File_ID
            "094"  # Record Size
            "10"  # Blocking Factor
            "1"  # Format Code
            f"{'PNC Bank':<23}"
            f"{'HazTrain Inc.':<23}"
            f"{' ':8}"
        )
        assert len(return_value) == 94, "Bad record length for header"
        return return_value

    def company_batch_header(self, batch_number=1):
        return_value = (
            "5"
            "220"                           # Service Class code 220 == ACH Credits Only
            f"{COMPANY_NAME:<16}"
            f"{'ACH Payments':>20}"         # Discretionary data ToDo Look to change this
            f"1{HAZTRAIN_TAX_ID:}"
            "CCD"                           # Standard entry class code
            f"{'Payments':10}"              # Company entry description  ToDo Look to change this
            f"{self.effective_date.year - 2000:02d}{self.effective_date.month:02d}{self.effective_date.day:02d}"
            f"{self.effective_date.year - 2000:02d}{self.effective_date.month:02d}{self.effective_date.day:02d}"
            f"{' ':3}"  # Settlement Date
            "1"  # Originator Status Code
            f"{PNC_ROUTING_NUMBER[0:8]}"
            f"{batch_number:07d}"
        )
        assert len(return_value) == 94, "Bad record length for header"
        return return_value

    def batch_control_record(self):
        total_amount = sum([pay.amount for pay in self.payments])
        dfi_hash = sum([int(pay.receiving_dfi()) for pay in self.payments]) % 10000000000

        return_value = (
            "8"
            "220"               # Service class code
            f"{len(self.payments):06d}"
            f"{dfi_hash:010d}"
            f"{0:012d}"
            f"{int(total_amount*100):012d}"
            f"1{HAZTRAIN_TAX_ID:}"
            f"{' ':19}"         # Message Authentication Code
            f"{' ':6}"          # Reserved
            f"{PNC_ROUTING_NUMBER[0:8]}"
            f"{1:07d}"        # Batch Number
        )
        assert len(return_value) == 94, "Bad record length for header"

        return return_value

    def file_control_record(self):
        total_amount = sum([pay.amount for pay in self.payments])
        dfi_hash = sum([int(pay.receiving_dfi()) for pay in self.payments]) % 10000000000
        return_value = (
            "9"
            f"{1:06d}"                              # Batch Count
            f"{2+2+2*len(self.payments):06d}"       # Block Count
            f"{2*len(self.payments):08d}"           # Entry Count
            f"{dfi_hash:010d}"                      # Entry Hash
            f"{0:012d}"                            # Debit amount
            f"{int(total_amount*100):012d}"                 # Credit amount
            f"{' ':39}"
        )
        # print(f'file control length = {len(return_value)}')
        assert len(return_value) == 94, "Bad record length for file control record"

        return return_value

    def write_to_file(self, file):
        file.write(self.header() + "\n")
        file.write(self.company_batch_header() + "\n")
        for payment in self.payments:
            file.write(payment.entry_detail_record() + "\n")
            file.write(payment.addenda_record() + "\n")
        file.write(self.batch_control_record() + "\n")
        file.write(self.file_control_record() + "\n")

    def total_amount(self):
        amount = sum([payment.amount for payment in self.payments])
        return amount
