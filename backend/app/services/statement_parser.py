import csv
import io

from datetime import datetime


DATE_COLUMNS = [
    "date",
    "transaction date",
    "tran date",
    "txn date",
    "value date",
    "transaction date/time"
]


DESCRIPTION_COLUMNS = [
    "description",
    "particulars",
    "narration",
    "transaction details",
    "remarks",
    "details",
    "transaction particulars"
]


DEBIT_COLUMNS = [
    "debit",
    "dr",
    "withdrawal",
    "withdrawals",
    "debit amount",
    "withdrawal amount"
]


CREDIT_COLUMNS = [
    "credit",
    "cr",
    "deposit",
    "deposits",
    "credit amount",
    "deposit amount"
]


AMOUNT_COLUMNS = [
    "amount",
    "transaction amount",
    "txn amount"
]


def clean_column_name(column):

    if not column:
        return ""

    return " ".join(
        str(column).strip().lower().split()
    )


def find_column(header, possible_names):

    for index, column in enumerate(header):

        cleaned_column = clean_column_name(column)

        if cleaned_column in possible_names:
            return index

    return None


def parse_date(value):

    if not value:
        return None

    value = str(value).strip()

    date_formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%b-%Y",
        "%d %b %Y",
        "%d-%B-%Y",
        "%d %B %Y"
    ]

    for date_format in date_formats:

        try:

            return datetime.strptime(
                value,
                date_format
            )

        except ValueError:

            pass

    return None


def clean_amount(value):

    if not value:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = value.replace(",", "")
    value = value.replace("₹", "")
    value = value.replace("INR", "")
    value = value.strip()

    try:

        return float(value)

    except ValueError:

        return None


def parse_csv_statement(contents):

    text_content = contents.decode(
        "utf-8",
        errors="replace"
    )

    csv_file = io.StringIO(
        text_content
    )

    reader = csv.reader(csv_file)

    rows = list(reader)

    if not rows:

        raise ValueError(
            "CSV file is empty"
        )


    header_index = None
    header = None



    for index, row in enumerate(rows):

        cleaned_row = [
            clean_column_name(column)
            for column in row
        ]

        date_column = find_column(
            cleaned_row,
            DATE_COLUMNS
        )

        description_column = find_column(
            cleaned_row,
            DESCRIPTION_COLUMNS
        )

        debit_column = find_column(
            cleaned_row,
            DEBIT_COLUMNS
        )

        credit_column = find_column(
            cleaned_row,
            CREDIT_COLUMNS
        )

        amount_column = find_column(
            cleaned_row,
            AMOUNT_COLUMNS
        )

        has_money_column = (

            debit_column is not None

            or credit_column is not None

            or amount_column is not None

        )


        if (

            date_column is not None

            and description_column is not None

            and has_money_column

        ):

            header_index = index
            header = cleaned_row

            break


    if header_index is None:

        raise ValueError(
            "Could not detect transaction table"
        )


    date_column = find_column(
        header,
        DATE_COLUMNS
    )

    description_column = find_column(
        header,
        DESCRIPTION_COLUMNS
    )

    debit_column = find_column(
        header,
        DEBIT_COLUMNS
    )

    credit_column = find_column(
        header,
        CREDIT_COLUMNS
    )

    amount_column = find_column(
        header,
        AMOUNT_COLUMNS
    )


    transactions = []


    for row in rows[header_index + 1:]:


        if date_column >= len(row):

            continue


        transaction_date = parse_date(
            row[date_column]
        )


        if transaction_date is None:

            continue


        if description_column >= len(row):

            continue


        description = row[
            description_column
        ].strip()


        if not description:

            continue


        debit = None
        credit = None
        amount = None
        transaction_type = None


        if (

            debit_column is not None

            and debit_column < len(row)

        ):

            debit = clean_amount(
                row[debit_column]
            )



        if (

            credit_column is not None

            and credit_column < len(row)

        ):

            credit = clean_amount(
                row[credit_column]
            )



        if debit is not None and debit > 0:

            amount = debit
            transaction_type = "debit"


        elif credit is not None and credit > 0:

            amount = credit
            transaction_type = "credit"


        elif (

            amount_column is not None

            and amount_column < len(row)

        ):

            amount = clean_amount(
                row[amount_column]
            )

            if amount is not None:

                transaction_type = "unknown"


        if amount is None:

            continue


        transactions.append({

            "transaction_date":
            transaction_date,

            "description":
            description,

            "amount":
            amount,

            "transaction_type":
            transaction_type

        })


    return transactions