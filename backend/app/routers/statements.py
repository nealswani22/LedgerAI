from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)

from sqlalchemy.orm import Session


from app.database.connection import get_db


from app.models.transaction import Transaction


from app.services.statement_parser import (
    parse_csv_statement
)


from app.services.transaction_normalizer import (
    normalize_description
)


from app.services.ai_classifier import (
    classify_merchants_with_ai
)


from app.services.transaction_service import (

    find_duplicate_transaction,

    find_merchant_by_normalized_description,

    get_transaction_from_database

)


router = APIRouter(

    prefix="/statements",

    tags=["Statements"]

)


@router.post("/upload")
async def upload_statement(

    file: UploadFile = File(...),

    db: Session = Depends(get_db)

):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="File must have a filename"
        )


    if not file.filename.lower().endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Currently only CSV files are supported"
        )


    try:

        contents = await file.read()


        parsed_transactions = parse_csv_statement(
            contents
        )


        duplicate_transactions = []

        new_transactions = []

        transactions_for_ai = []

        cached_transactions = []


        ai_transaction_id = 1




        for transaction in parsed_transactions:



            normalized_description = (
                normalize_description(
                    transaction["description"]
                )
            )


            transaction[
                "normalized_description"
            ] = normalized_description


    

            duplicate = (
                find_duplicate_transaction(

                    db=db,

                    transaction_date=
                    transaction["transaction_date"],

                    description=
                    transaction["description"],

                    amount=
                    transaction["amount"],

                    transaction_type=
                    transaction["transaction_type"]

                )
            )


            if duplicate:

                duplicate_transactions.append(

                    get_transaction_from_database(
                        duplicate
                    )

                )

                continue



            merchant_cache = (
                find_merchant_by_normalized_description(

                    db=db,

                    normalized_description=
                    normalized_description

                )
            )


            if merchant_cache:


                transaction[
                    "merchant_name"
                ] = (
                    merchant_cache.merchant_name
                )


                transaction[
                    "category"
                ] = (
                    merchant_cache.category
                )


                transaction[
                    "category_confidence"
                ] = (
                    merchant_cache.category_confidence
                )


                transaction[
                    "classification_source"
                ] = "merchant_cache"


                cached_transactions.append(
                    transaction
                )


                new_transactions.append(
                    transaction
                )


                continue




            transaction["id"] = ai_transaction_id

            ai_transaction_id += 1


            transaction[
                "classification_source"
            ] = "ai"


            transactions_for_ai.append(
                transaction
            )


            new_transactions.append(
                transaction
            )




        ai_results = (
            classify_merchants_with_ai(

                transactions_for_ai

            )
        )




        classification_map = {}


        for result in ai_results:


            transaction_id = result.get("id")


            if transaction_id is not None:

                classification_map[
                    transaction_id
                ] = result




        for transaction in transactions_for_ai:


            classification = (
                classification_map.get(

                    transaction["id"],

                    {}

                )
            )


            transaction[
                "merchant_name"
            ] = classification.get(

                "merchant_name",

                "Unknown"

            )


            transaction[
                "category"
            ] = classification.get(

                "category",

                "Other"

            )


            transaction[
                "category_confidence"
            ] = classification.get(

                "category_confidence",

                0.0

            )



        saved_transactions = []


        for transaction in new_transactions:


            new_transaction = Transaction(

                transaction_date=
                transaction["transaction_date"],


                description=
                transaction["description"],


                normalized_description=
                transaction[
                    "normalized_description"
                ],


                amount=
                transaction["amount"],


                transaction_type=
                transaction["transaction_type"],


                merchant_name=
                transaction.get(
                    "merchant_name",
                    "Unknown"
                ),


                category=
                transaction.get(
                    "category",
                    "Other"
                ),


                category_confidence=
                transaction.get(
                    "category_confidence",
                    0.0
                )

            )


            db.add(
                new_transaction
            )


            db.flush()


            saved_transactions.append({

                "id":
                new_transaction.id,


                "transaction_date":
                new_transaction.transaction_date,


                "description":
                new_transaction.description,


                "normalized_description":
                new_transaction.normalized_description,


                "amount":
                new_transaction.amount,


                "transaction_type":
                new_transaction.transaction_type,


                "merchant_name":
                new_transaction.merchant_name,


                "category":
                new_transaction.category,


                "category_confidence":
                new_transaction.category_confidence,


                "source":
                transaction.get(
                    "classification_source",
                    "unknown"
                )

            })



        db.commit()


        return {

            "message":
            "Statement processed successfully",


            "filename":
            file.filename,


            "transactions_found":
            len(parsed_transactions),


            "new_transactions":
            len(new_transactions),


            "duplicates_found":
            len(duplicate_transactions),


            "merchant_cache_hits":
            len(cached_transactions),


            "transactions_sent_to_ai":
            len(transactions_for_ai),


            "ai_classifications_received":
            len(ai_results),


            "preview":

            (

                saved_transactions

                +

                duplicate_transactions

            )[:10]

        }


    except HTTPException:

        raise


    except Exception as error:


        db.rollback()


        raise HTTPException(

            status_code=400,

            detail=(
                f"Could not process statement: "
                f"{str(error)}"
            )

        )