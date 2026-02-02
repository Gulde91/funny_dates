#!/usr/bin/env python3
"""Send milestone email only when there is output to deliver."""
from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from subprocess import check_output


SENDER = os.environ["FUNNY_DATES_SENDER"]
RECIPIENT = os.environ.get("FUNNY_DATES_RECIPIENT", SENDER)
APP_PASSWORD = os.environ["FUNNY_DATES_APP_PASSWORD"]


def main() -> None:
    output = check_output(
        [
            "/usr/bin/python3",
            "/home/alex/funny_dates/funny_dates.py",
            "--birthdays",
            "/home/alex/funny_dates/birthdays.json",
        ],
        text=True,
    )

    if not output.strip():
        return

    msg = EmailMessage()
    msg["Subject"] = "Mærkedage"
    msg["From"] = SENDER
    msg["To"] = RECIPIENT
    msg.set_content(output)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER, APP_PASSWORD)
        smtp.send_message(msg)


if __name__ == "__main__":
    main()
