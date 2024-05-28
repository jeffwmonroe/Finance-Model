from math import isnan

ROUTING_NUMBER = "054000030"


def trim_string(str, max_len):
    if len(str) > max_len:
        return str[:max_len]
    return str


class PaymentDetail:
    def __init__(self, payment_info, transaction_number):
        # print(f'Payment Info:')
        # print(f'{payment_info}')
        # print(payment_info.dtypes)

        self.routing_number = payment_info["Routing Number"]
        self.account_number = payment_info["Account Number"]
        self.amount = payment_info["Amount"]
        self.vendor_name = payment_info["Vendor Name"]
        self.vendor_id = payment_info["Vendor ID"]
        self.invoice_number = payment_info["Invoice Number"]
        self.description = payment_info["Description"]
        self.transaction_number = transaction_number
        self.vendor_type = payment_info["Vendor Type"]
        self.customer_id = payment_info["Customer ID"]
        self.account_type = payment_info["Account Type"]
        assert len(self.routing_number) == 9
        assert len(self.account_number) <= 17
        assert len(self.description) <= 80

    def transaction_code(self):
        if self.account_type == "checking":
            return "22"
        else:
            return "32"

    def formatted_account_number(self):
        # If the account number is > len 17 we need to prune it
        assert len(self.account_number) < 17
        # Account number cannot contain spaces
        assert self.account_number.find(" ") == -1, "Error spaces in account number"
        return f"{self.account_number:<17}"

    def trace_number(self):
        return self.routing_number[:-1] + f"{self.transaction_number:07d}"

    def receiving_dfi(self):
        return self.routing_number[0:8]

    def entry_detail_record(self):
        return_value = (
            f"6"
            f"{self.transaction_code()}"
            f"{self.receiving_dfi()}"  # Receiving DFI
            f"{self.routing_number[-1]}"
            f"{self.formatted_account_number()}"
            f"{self.amount:010.2f}"
            f"{self.vendor_id:>15}"
            f"{self.vendor_name:>22}"
            f"  "
            "1"
            f"{self.trace_number()}"
        )
        # print(f"entry len = {len(ret)}")
        assert len(return_value) == 94, "Record is the wrong length"
        return return_value

    def formatted_invoice_number(self):
        if self.vendor_type == "employee":
            return_value = self.description
        else:
            return_value = f"Invoice Number: {self.invoice_number}"
            if len(self.customer_id) > 0:
                return_value += f", Customer ID: {self.customer_id}"
            if len(self.description) > 0:
                return_value += f", {self.description}"
        if len(return_value) > 80:
            return_value = return_value[:77] + "..."
        assert len(return_value) <= 80, "formatted invoice number is too long"
        return return_value

    def addenda_record(self):
        return_value = (
            "7"
            "05"
            f"{self.formatted_invoice_number():<80}"
            "0001"  # Addenda Sequence number
            f"{self.trace_number()[-7:]}"  # Entry detail sequence number
        )
        assert len(return_value) == 94, "Record is the wrong length"
        return return_value
