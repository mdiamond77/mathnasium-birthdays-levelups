import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import CENTERS, CC_RECIPIENT


def _table_rows(rows: list[dict], cols: list[str]) -> str:
    if not rows:
        return "<tr><td colspan='{}' style='color:#888;font-style:italic;'>None this month.</td></tr>".format(len(cols))
    return "".join(
        "<tr>" + "".join(
            "<td style='padding:6px 12px;border:1px solid #ddd;'>{}</td>".format(row.get(c, ""))
            for c in cols
        ) + "</tr>"
        for row in rows
    )


def _table(headers: list[str], rows: list[dict], cols: list[str]) -> str:
    header_html = "".join(
        "<th style='padding:6px 12px;border:1px solid #ddd;background:#f5f5f5;text-align:left;'>{}</th>".format(h)
        for h in headers
    )
    return (
        "<table style='border-collapse:collapse;font-family:Arial,sans-serif;"
        "font-size:14px;margin-bottom:8px;'>"
        "<tr>{}</tr>"
        "{}"
        "</table>"
    ).format(header_html, _table_rows(rows, cols))


def build_html(
    center_name: str,
    month_label: str,
    birthdays: list[dict],
    current_levelups: list[dict],
    last_levelups: list[dict],
) -> str:
    """Build the full HTML email body."""
    bday_rows = [
        {"Name": r["name"], "Birthday": r["birthday"], "Age": r["age"]}
        for r in birthdays
    ]
    bday_table = _table(["Name", "Birthday", "Age"], bday_rows, ["Name", "Birthday", "Age"])

    def levelup_table(rows):
        display = [
            {
                "Name": r["name"],
                "Old Level": "Level {}".format(r["old_level"]),
                "New Level": "Level {}".format(r["new_level"]),
            }
            for r in rows
        ]
        return _table(
            ["Name", "Old Level", "New Level"],
            display,
            ["Name", "Old Level", "New Level"],
        )

    divider = "<hr style='border:none;border-top:2px solid #ccc;margin:24px 0;'>"

    return """
<html><body style="font-family:Arial,sans-serif;font-size:14px;max-width:700px;margin:0 auto;padding:20px;">

<p>Hi {center} Center Directors,</p>

<p>Please find this month's Birthdays &amp; Level Ups below. As a reminder:</p>
<ul>
  <li>Please have an instructor <strong>update the student binders</strong> for any level ups.</li>
  <li>Please <strong>add this month's birthdays to the whiteboard</strong> so we can celebrate with our students!</li>
</ul>

{divider}

<h2 style="color:#333;">&#127874; Birthdays &mdash; {month}</h2>
{bday_table}

{divider}

<h2 style="color:#333;">&#11088; Level Ups This Month</h2>
{current_table}

{divider}

<h2 style="color:#333;">&#9989; Last Month's Level Ups &mdash; Please Confirm Binders Were Updated</h2>
<p style="color:#555;">The following students leveled up last month. Please confirm their binders have been updated.</p>
{last_table}

{divider}

<p style="color:#999;font-size:12px;"><em>This email was generated automatically. Questions? Contact matt.diamond@mathnasium.com.</em></p>

</body></html>
""".format(
        center=center_name,
        month=month_label,
        divider=divider,
        bday_table=bday_table,
        current_table=levelup_table(current_levelups),
        last_table=levelup_table(last_levelups),
    )


def send_email(center_name: str, month_label: str, html: str) -> None:
    """Send the HTML email for one center via Gmail SMTP."""
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    recipient = CENTERS[center_name]["recipient"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Mathnasium {} \u2014 Birthdays & Level Ups: {}".format(
        center_name, month_label
    )
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg["Cc"] = CC_RECIPIENT

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [recipient, CC_RECIPIENT], msg.as_string())


def deliver(center_data: dict, month_label: str) -> None:
    """Send one email per center.

    Args:
        center_data: output of process.process() —
            {center_name: {current_levelups, last_levelups, birthdays}}
        month_label: human-readable label e.g. "April 2026"
    """
    for center_name, data in center_data.items():
        html = build_html(
            center_name=center_name,
            month_label=month_label,
            birthdays=data["birthdays"],
            current_levelups=data["current_levelups"],
            last_levelups=data["last_levelups"],
        )
        send_email(center_name, month_label, html)
        print("Sent email for {}".format(center_name))
