import os
import json

from dotenv import load_dotenv

from google import genai
from google.genai import types


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")


if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in your .env file"
    )


client = genai.Client(
    api_key=api_key
)


def classify_merchants_with_ai(merchants):

    if not merchants:
        return []


    prompt = f"""
You are classifying merchants found in Indian bank statements.

For each merchant identify:

1. merchant_name
2. category
3. category_confidence

Allowed categories:

Food
Groceries
Entertainment
Transport
Shopping
Utilities
Subscriptions
Investments
Transfers
Income
Healthcare
Education
Travel
Other

Rules:

- Keep the ID unchanged.
- Use the merchant text as the main classification signal.
- Identify the real merchant when possible.
- Do not invent a merchant.
- If the merchant is unclear, use "Unknown".
- Stock brokers and investment platforms are Investments.
- Banks or payment recipients are not automatically merchants.
- Person-to-person transfers should be Transfers.
- Return confidence between 0 and 1.
- Every input item MUST have exactly one output.
- Return only valid JSON.
- Do not include markdown.
- Do not include explanations.

Required format:

[
  {{
    "id": 1,
    "merchant_name": "Blinkit",
    "category": "Groceries",
    "category_confidence": 0.98
  }}
]

Merchants:

{json.dumps(merchants, default=str)}
"""


    try:

        print(
            f"Sending {len(merchants)} merchants to Gemini..."
        )


        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=prompt,

            config=types.GenerateContentConfig(

                response_mime_type="application/json"

            )

        )


        output = response.text.strip()


        print("\nGEMINI RAW RESPONSE:")

        print(output)


        if not output:

            print(
                "Gemini returned an empty response"
            )

            return []


        results = json.loads(
            output
        )


        if not isinstance(results, list):

            print(
                "Gemini response is not a JSON list"
            )

            return []


        print(
            f"\nGemini successfully classified "
            f"{len(results)} merchants"
        )


        return results


    except Exception as error:

        print("\n")

        print("=" * 60)

        print(
            "GEMINI CLASSIFICATION ERROR"
        )

        print("=" * 60)

        print(type(error).__name__)

        print(str(error))

        print("=" * 60)

        print("\n")


        return []