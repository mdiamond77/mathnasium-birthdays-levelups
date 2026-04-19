import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

from config import INPUT_DIR, RADIUS_LOGIN_URL, CENTERS

CENTER_IDS = [c["radius_id"] for c in CENTERS.values()]


def _login(page):
    """Log into Radius."""
    page.goto(RADIUS_LOGIN_URL)
    page.fill("#UserName", os.environ.get("RADIUS_USERNAME"))
    page.fill("#Password", os.environ.get("RADIUS_PASSWORD"))
    page.click("#login")
    page.wait_for_load_state("networkidle")


def _select_all_centers(page):
    """Select both Englewood and Teaneck in the center MultiSelect."""
    page.evaluate(
        """(ids) => {
            const ms = $('#AllCenterListMultiSelect').data('kendoMultiSelect');
            ms.value(ids);
            ms.trigger('change');
        }""",
        json.dumps(CENTER_IDS),
    )


def download_enrollment_report(page, month_label: str) -> Path:
    """Navigate to the Enrollment Report, select enrolled + both centers, export to Excel."""
    out_path = INPUT_DIR / f"Enrollment_{month_label}.xlsx"

    page.goto("https://radius.mathnasium.com/Enrollment/EnrollmentReport")
    page.wait_for_load_state("networkidle")

    # Set status to Enrolled (value "3")
    page.evaluate("""
        const dd = $('#EnrollmentStatusDropDown').data('kendoDropDownList');
        dd.value('3');
        dd.trigger('change');
    """)

    _select_all_centers(page)

    page.click("#btnsearch")
    page.wait_for_load_state("networkidle")

    with page.expect_download() as dl:
        page.click("#btnExport")
    dl.value.save_as(out_path)

    return out_path


def download_birthday_report(page, month_label: str, month_num: int) -> Path:
    """Navigate to the Birthday Report, filter to enrolled + current month + both centers, export."""
    out_path = INPUT_DIR / f"Birthdays_{month_label}.xlsx"

    page.goto("https://radius.mathnasium.com/BirthdayReport")
    page.wait_for_load_state("networkidle")

    # Set month filter
    page.evaluate(
        """(m) => {
            const dd = $('#birthdayMonthsDropDownList').data('kendoDropDownList');
            dd.value(m);
            dd.trigger('change');
        }""",
        str(month_num),
    )

    # Set enrollment filter to Enrolled (value "3")
    page.evaluate("""
        const dd = $('#enrollmentFiltersDropDownList').data('kendoDropDownList');
        dd.value('3');
        dd.trigger('change');
    """)

    _select_all_centers(page)

    page.click("#btnsearch")
    page.wait_for_load_state("networkidle")

    with page.expect_download() as dl:
        page.click("#btnExport")
    dl.value.save_as(out_path)

    return out_path


def download_reports(month_label: str, month_num: int) -> dict:
    """Download both reports. Returns dict with paths to each file."""
    INPUT_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        with browser:
            context = browser.new_context(accept_downloads=True)
            with context:
                page = context.new_page()
                _login(page)
                enrollment_path = download_enrollment_report(page, month_label)
                birthday_path = download_birthday_report(page, month_label, month_num)

    return {
        "enrollment": enrollment_path,
        "birthdays": birthday_path,
    }
