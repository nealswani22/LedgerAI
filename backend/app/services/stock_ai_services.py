import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()


api_key = os.getenv(
    "GEMINI_API_KEY"
)


if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in your .env file"
    )


client = genai.Client(
    api_key=api_key
)


def analyze_stock_with_ai(stock):

    prompt = f"""
You are analyzing a stock.

Analyze the provided stock analytics.

Return:

1. predicted_return_percent
2. confidence

Rules:

- Keep the stock symbol unchanged.
- predicted_return_percent should be a realistic estimated percentage return.
- confidence must be between 0 and 1.
- Use only the supplied analytics.
- Do not invent market data.
- Return ONLY valid JSON.
- Do not use markdown.

Required format:

{{
    "symbol": "RELIANCE.NS",
    "predicted_return_percent": 8.5,
    "confidence": 0.78
}}

Stock data:

{json.dumps(stock, default=str)}
"""


    try:

        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=prompt
        )


        output = response.text.strip()


        if not output:

            return None


        return json.loads(
            output
        )


    except Exception as error:

        print(
            f"AI analysis failed for "
            f"{stock.get('symbol')}: {error}"
        )

        return None