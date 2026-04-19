import argparse
import traceback
from datetime import date

from download import download_reports
from process import process
from deliver import deliver
from run_log import write_log


def get_month_label(month_str: str) -> str:
    """Convert 'YYYY-MM' to 'Month YYYY' e.g. '2026-04' -> 'April 2026'."""
    year, month = month_str.split("-")
    month_name = date(int(year), int(month), 1).strftime("%B")
    return "{} {}".format(month_name, year)


def main():
    parser = argparse.ArgumentParser(description="Run Birthdays & Level Ups automation.")
    parser.add_argument(
        "--month",
        default=date.today().strftime("%Y-%m"),
        help="Month to process in YYYY-MM format (default: current month)",
    )
    args = parser.parse_args()
    month_str = args.month
    month_num = int(month_str.split("-")[1])
    month_label = get_month_label(month_str)

    print("Running Birthdays & Level Ups for {}".format(month_label))

    try:
        print("Downloading reports...")
        paths = download_reports(month_label, month_num)

        print("Processing data...")
        center_data = process(paths["enrollment"], paths["birthdays"], month=month_num)

        print("Sending emails...")
        deliver(center_data, month_label)

        write_log(month_str, success=True)
        print("Done.")

    except Exception as e:
        error_msg = traceback.format_exc()
        print("ERROR: {}".format(e))
        print(error_msg)
        write_log(month_str, success=False, error=error_msg)
        raise


if __name__ == "__main__":
    main()
