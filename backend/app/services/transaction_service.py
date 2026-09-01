from app.models.transaction import Transaction


def find_duplicate_transaction(
    db,
    transaction_date,
    description,
    amount,
    transaction_type
):

    return (

        db.query(Transaction)

        .filter(

            Transaction.transaction_date
            == transaction_date,

            Transaction.description
            == description,

            Transaction.amount
            == amount,

            Transaction.transaction_type
            == transaction_type

        )

        .first()

    )


def find_merchant_by_normalized_description(
    db,
    normalized_description
):
    """
    Finds a previously classified transaction
    with the same normalized merchant fingerprint.
    """

    if not normalized_description:

        return None


    return (

        db.query(Transaction)

        .filter(

            Transaction.normalized_description
            == normalized_description,

            Transaction.merchant_name
            .isnot(None),

            Transaction.category
            .isnot(None)

        )

        .order_by(
            Transaction.id.desc()
        )

        .first()

    )


def get_transaction_from_database(
    transaction
):

    return {

        "id":
        transaction.id,

        "transaction_date":
        transaction.transaction_date,

        "description":
        transaction.description,

        "normalized_description":
        transaction.normalized_description,

        "amount":
        transaction.amount,

        "transaction_type":
        transaction.transaction_type,

        "merchant_name":
        transaction.merchant_name,

        "category":
        transaction.category,

        "category_confidence":
        transaction.category_confidence,

        "source":
        "database"

    }