# import pandas as pd
import re
import time
import os
from datetime import datetime, timedelta
import schedule
import sys

## NEXT STEP IS TO SEE IF YOU CAN GET THIS WORKING ON OLD COMPUTER WITH
# conda env create -f playtime.yaml
# re: https://youtu.be/rJvArFX5Gy4?t=266
# then put it on github.

from playwright.sync_api import Playwright, sync_playwright, expect, TimeoutError

# from timestamps import Timestamps

# Timestamps = Timestamps()

SITE_URL = 'https://www.playtimescheduler.com/login.php'
PLAYTIME_PASSWORD = os.getenv('PLAYTIME_PASSWORD')
# date_to_sign_up_for = "11/27/2024" #MUST BE IN MM/DD/YYYY FORMAT e.g. "01/22/2025"
SESSION_TEXT_TO_FIND = "Bedford - John Glenn Middle School – 4.0"
# SESSION_TEXT_TO_FIND = "Watertown"


def run(playwright: Playwright):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False, slow_mo=100)
    context = browser.new_context()
    page = context.new_page()
    page.goto(SITE_URL)
    return page


def login(page):
    try:
        page.get_by_placeholder("name@example.com").click()
        page.get_by_placeholder("name@example.com").fill(PLAYTIME_EMAIL)
        page.get_by_role("button", name="Login").click()
        page.locator("#password").fill(PLAYTIME_PASSWORD)
        page.get_by_role("button", name="Login").click()
        try:
            if page.locator("#rulesModal").is_visible():
                page.locator("#rulesModal").click()
        except Exception as e:
            print(f"An error occurred when locating the code of conduct modal window: {e}")

        page.get_by_role("button", name="Got It!").click()

    except Exception as e:
        print(f"An error occurred when logging in: {e}")

def select_date(page, date_to_sign_up_for):
        # click on the calendar dropdown to select a date
        page.locator('xpath=//*[@id="calendar"]/div[2]/h1/a[1]').click()

        # click on a date within the calendar dropdown
        signup_date_element = page.locator(f"td[data-day='{date_to_sign_up_for}']")

        # iterate through months until the signup date is found
        max_iterations = 12  # maximum number of months to check
        iterations = 0

        while signup_date_element.count() == 0 and iterations < max_iterations:
            print("No, I didn't find it... let's move to the next month and try again...")
            page.get_by_title("Next Month").click()
            signup_date_element = page.locator(f"td[data-day='{date_to_sign_up_for}']")
            iterations += 1

        if iterations == max_iterations:
            print("Date not found within the next 12 months.")
            return

        signup_date_element.click()

def select_session(page):
        xpath = f'//*[@id="calendar"]/div[5]/div[1]/div[2]/button/div[2][contains(text(), "{SESSION_TEXT_TO_FIND}")]'
        identified_playdate_elements = page.locator(f'xpath={xpath}')

        #POTENTIAL IMPROVEMENT - CONSIDER USING THE BELOW CODE TO IDENTIFY THE ELEMENTS
        # elements = page.locator("text=9:00A : Watertown - Cannalonga Park – 3.75-4.0")
        # for element in elements.all():
        #     print(element.text_content())
        # time.sleep(5)

            # print the text of all elements identified by the SESSION_TEXT_TO_FIND and if there is anything, click on it!
        if identified_playdate_elements.count() == 0:
            print(f"no elements found including '{SESSION_TEXT_TO_FIND}'")
            page.get_by_role("link", name=" Log Out").click()
        else:
            # print all the elements that were found
            for elements in identified_playdate_elements.all():
                print(elements.text_content())
            # select the first of the found elements
            identified_playdate_elements.first.click()
            print("Accessed session at ", time.strftime("%H:%M:%S", time.localtime()), "...")

def sign_up(page, date_to_sign_up_for):
        # Verifying the workflow for refreshing the page.
        MAX_REFRESH_ATTEMPTS = 10
        refresh_attempt_count = 0 # counter for the number of times to refresh the page
        while refresh_attempt_count < MAX_REFRESH_ATTEMPTS:
            try:
                time.sleep(1)
                page.get_by_role("button", name="+ Add My Name").click(timeout=500)
                print(f"Reservation on {date_to_sign_up_for} was successful!")
                def remove_self():
                    print("just signed up... executing option to remove myself")
                    time.sleep(2)
                    page.get_by_role("row", name="Sean Morris (4.0)").get_by_role("img").nth(2).click()

                    print("just removed myself, waiting 2 seconds before confirming removal")
                    time.sleep(2)
                    page.get_by_role("button", name="Remove").click()
                    print("removal successful")
                    page.get_by_role("button", name="Close").click()
                    page.locator("text=Log Out").click()
                # remove_self()
                page.get_by_role("button", name="Close").click()
                break
            except TimeoutError:
                print("Session not available... yet... retrying in 1 second")
                # time.sleep(1)
                page.locator("#reloadSessionBtn").click()
                refresh_attempt_count += 1

        if refresh_attempt_count == 10:
            print("shucks we've reached our specified max number of refresh attempts, no reservation was made")
            return


if __name__ == '__main__':
    scheduled_or_immediate = "scheduled"
    page = run(Playwright)

    if scheduled_or_immediate == "immediate":
        login(page)
        select_date(page)
        select_session(page)
        sign_up(page, date_to_sign_up_for="11/27/2024")

    elif scheduled_or_immediate == "scheduled":
        time_for_sign_up = "00:01:00"

        # function to get the time 1 minute before the time_for_login
        def get_login_time(time_for_sign_up: str) -> str:
            return (datetime.strptime(time_for_sign_up, "%H:%M:%S") - timedelta(minutes=1)).strftime("%H:%M:%S")

        time_for_logging_in = get_login_time(time_for_sign_up)
        print("will log in at...", time_for_logging_in)

        def scheduled_login(date_to_sign_up_for):
            login(page)
            select_date(page, date_to_sign_up_for)

        def scheduled_sign_up(date_to_sign_up_for):
            select_session(page)
            sign_up(page, date_to_sign_up_for)

        def get_date_in_7_days():
            global date_in_7_days
            date_in_7_days = (datetime.now() + timedelta(days=7)).strftime("%m/%d/%Y")
            print("this function was run on ", time.strftime("%H:%M:%S", time.localtime()), "and returns ", date_in_7_days)
            return date_in_7_days
        date_in_7_days = get_date_in_7_days()
        print("will sign up for...", date_in_7_days)

        # the following three lines of code were for analysis and debugging purposes
        # schedule.every().day.at("00:00:01").do(get_date_in_7_days)
        # schedule.every().day.at(time_for_logging_in).do(scheduled_login, date_in_7_days)
        # schedule.every().day.at(time_for_sign_up).do(scheduled_sign_up, date_in_7_days)

        # schedule the following two sets of sessions:
        # 1/2 Saturday sessions at 3pm
        schedule.every().saturday.at("14:59:00").do(scheduled_login, date_in_7_days)
        schedule.every().saturday.at("15:00:01").do(scheduled_sign_up, date_in_7_days)

        # 2/2 - Sunday, Tuesday, and Thursday sessions at 6pm
        for day in ["sunday", "tuesday", "thursday"]:
            schedule.every().__getattribute__(day).at("17:59:00").do(scheduled_login, date_in_7_days)
            schedule.every().__getattribute__(day).at("18:00:01").do(scheduled_sign_up, date_in_7_days)

        while True:
            schedule.run_pending()
            time.sleep(1)
