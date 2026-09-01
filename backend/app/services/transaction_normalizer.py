import re


STOP_WORDS = {
    "UPI",
    "P2M",
    "P2A",
    "IMPS",
    "NEFT",
    "RTGS",
    "POS",
    "ECOM",
    "PUR",
    "PURCHASE",
    "PAYMENT",
    "TRANSFER",
    "BANK",
    "LIMITED",
    "LTD",
    "LTD.",
    "PAYMENTS",
    "REMITTER",
    "VERIFIED",
    "EXECUTION",
    "REMARK",
    "REMAR",
    "SENT",
    "USING",
    "P2V",
    "UPIINT",
    "YBS",
    "YESPAY",
    "YESPAY",
    "DOMIMPS",
    "SELFFT",
}



NOISE_PHRASES = {
    "HDFC",
    "HDFC BANK",
    "HDFC BANK LIMITED",

    "AXIS",
    "AXIS BANK",
    "AXIS BANK LIMITED",

    "ICICI",
    "ICICI BANK",
    "ICICI BANK LIMITED",

    "YES",
    "YES BANK",
    "YES BANK LIMITED",
    "YESPAY",
    "YES BANK YESPAY",

    "SBI",
    "SBIN",
    "STATE BANK",
    "STATE BANK OF INDIA",

    "BANK OF INDIA",

    "AIRTEL PAYMENTS",
    "AIRTEL PAYMENTS BANK",

    "PAY FO",
    "PARTNER SELL",
    "REMITTER",
    "NO REMAR",
    "NO REMARK",
}


def clean_text(text: str) -> str:


    if not text:
        return ""

    text = text.upper().strip()


    text = re.sub(
        r"[^A-Z0-9 ]",
        " ",
        text
    )


    text = re.sub(
        r"\b\d{5,}\b",
        " ",
        text
    )


    words = []

    for word in text.split():

        if word.isdigit():
            continue

        words.append(word)

    return " ".join(words).strip()


def is_noise(text: str) -> bool:

    if not text:
        return True

    text = text.upper().strip()

    if len(text) < 3:
        return True

    if text.isdigit():
        return True

    if re.fullmatch(
        r"[A-Z]{1,8}\d{5,}[A-Z0-9]*",
        text
    ):
        return True


    if text in NOISE_PHRASES:
        return True

    words = text.split()


    if words and all(
        word in STOP_WORDS
        for word in words
    ):
        return True


    bank_words = {
        "HDFC",
        "AXIS",
        "ICICI",
        "YES",
        "SBI",
        "SBIN",
    }

    if any(
        word in bank_words
        for word in words
    ):
        return True

    return False

def clean_merchant_candidate(text: str) -> str:


    if not text:
        return ""

    text = clean_text(text)

    if not text:
        return ""

    words = []

    for word in text.split():


        if word in STOP_WORDS:
            continue

        words.append(word)

    text = " ".join(words).strip()


    text = re.sub(
        r"\b(LIMITED|LTD|PRIVATE|PVT)\b",
        "",
        text
    )


    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def looks_like_reference(text: str) -> bool:

    if not text:
        return True

    text = text.upper().strip()

    # Mostly numbers.
    digits = sum(
        character.isdigit()
        for character in text
    )

    if len(text) > 0:

        digit_ratio = digits / len(text)

        if digit_ratio > 0.45:
            return True


    if re.fullmatch(
        r"[A-Z]{1,10}\d{5,}[A-Z0-9]*",
        text
    ):
        return True

    return False


def normalize_description(description: str) -> str:
  

    if not description:
        return ""

    original = description.upper().strip()


    if original.startswith("UPI/"):

        parts = [
            part.strip()
            for part in original.split("/")
        ]


        for part in parts[3:]:

            candidate = clean_merchant_candidate(
                part
            )

            if not candidate:
                continue

            if is_noise(candidate):
                continue

            if looks_like_reference(candidate):
                continue

            return candidate

        return ""

    

    if original.startswith("POS/"):

        parts = [
            part.strip()
            for part in original.split("/")
        ]

        if len(parts) > 1:

            candidate = clean_merchant_candidate(
                parts[1]
            )

            if (
                candidate
                and not is_noise(candidate)
                and not looks_like_reference(candidate)
            ):
                return candidate

        return ""


    if (
        original.startswith("ECOM")
        or original.startswith("ECOM PUR")
    ):

        parts = [
            part.strip()
            for part in original.split("/")
        ]

        for part in parts[1:]:

            candidate = clean_merchant_candidate(
                part
            )

            if not candidate:
                continue

            if is_noise(candidate):
                continue

            if looks_like_reference(candidate):
                continue

            # Skip obvious locations.
            if candidate in {
                "MUMBAI",
                "GURGAON",
                "DELHI",
                "BANGALORE",
                "BENGALURU",
            }:
                continue

            return candidate

        return ""


    if (
        original.startswith("NEFT/")
        or original.startswith("IMPS/")
        or original.startswith("RTGS/")
    ):

        parts = [
            part.strip()
            for part in original.split("/")
        ]

        for part in parts[1:]:

            candidate = clean_merchant_candidate(
                part
            )

            if not candidate:
                continue

            if is_noise(candidate):
                continue

            if looks_like_reference(candidate):
                continue

            # Avoid tiny fragments.
            if len(candidate) < 4:
                continue

            return candidate

        return ""


    parts = re.split(
        r"[/\-:*]",
        original
    )

    for part in parts:

        candidate = clean_merchant_candidate(
            part
        )

        if not candidate:
            continue

        if is_noise(candidate):
            continue

        if looks_like_reference(candidate):
            continue

        if len(candidate) < 3:
            continue

        return candidate

    return ""