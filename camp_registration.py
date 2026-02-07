#!/usr/bin/env python3
"""Automate summer camp registration form filling using Playwright.

This script reads selectors from a JSON config file and values from
command-line arguments or environment variables.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Iterable

from playwright.sync_api import sync_playwright


@dataclass(frozen=True)
class RegistrationData:
    child_first_name: str
    child_last_name: str
    sessions: list[str]
    card_number: str
    card_expiration: str
    card_cvv: str
    billing_zip: str | None
    parent_name: str | None


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as config_file:
        return json.load(config_file)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Auto-fill summer camp registration via Playwright."
    )
    parser.add_argument(
        "--config",
        default="camp_registration_config.json",
        help="Path to JSON config with selectors and URL.",
    )
    parser.add_argument(
        "--sessions",
        nargs="+",
        default=["1", "2", "3", "5", "7"],
        help="Session numbers to select.",
    )
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Run browser in headless mode (default: False).",
    )
    return parser.parse_args()


def env_or_empty(key: str) -> str:
    return os.environ.get(key, "").strip()


def env_or_none(key: str) -> str | None:
    value = os.environ.get(key, "").strip()
    return value if value else None


def build_registration_data(sessions: Iterable[str]) -> RegistrationData:
    return RegistrationData(
        child_first_name=env_or_empty("CAMP_CHILD_FIRST"),
        child_last_name=env_or_empty("CAMP_CHILD_LAST"),
        sessions=[str(session).strip() for session in sessions],
        card_number=env_or_empty("CAMP_CARD_NUMBER"),
        card_expiration=env_or_empty("CAMP_CARD_EXP"),
        card_cvv=env_or_empty("CAMP_CARD_CVV"),
        billing_zip=env_or_none("CAMP_BILLING_ZIP"),
        parent_name=env_or_none("CAMP_PARENT_NAME"),
    )


def validate_required(data: RegistrationData) -> None:
    missing = []
    if not data.child_first_name:
        missing.append("CAMP_CHILD_FIRST")
    if not data.child_last_name:
        missing.append("CAMP_CHILD_LAST")
    if not data.card_number:
        missing.append("CAMP_CARD_NUMBER")
    if not data.card_expiration:
        missing.append("CAMP_CARD_EXP")
    if not data.card_cvv:
        missing.append("CAMP_CARD_CVV")

    if missing:
        missing_vars = ", ".join(missing)
        raise SystemExit(
            f"Missing required environment variables: {missing_vars}."
        )


def maybe_fill(page, selector: str | None, value: str | None) -> None:
    if not selector or not value:
        return
    locator = page.locator(selector)
    if locator.count() > 0:
        locator.first.fill(value)


def maybe_check(page, selector: str | None) -> None:
    if not selector:
        return
    locator = page.locator(selector)
    if locator.count() > 0:
        locator.first.check()


def run_registration(config: dict, data: RegistrationData, headless: bool) -> None:
    selectors = config["selectors"]
    session_template = selectors.get("session_checkbox_template")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(config["url"], wait_until="domcontentloaded")

        maybe_fill(page, selectors.get("child_first_name"), data.child_first_name)
        maybe_fill(page, selectors.get("child_last_name"), data.child_last_name)
        maybe_fill(page, selectors.get("parent_name"), data.parent_name)

        if session_template:
            for session in data.sessions:
                maybe_check(page, session_template.format(session=session))

        maybe_fill(page, selectors.get("card_number"), data.card_number)
        maybe_fill(page, selectors.get("card_expiration"), data.card_expiration)
        maybe_fill(page, selectors.get("card_cvv"), data.card_cvv)
        maybe_fill(page, selectors.get("billing_zip"), data.billing_zip)

        submit_selector = selectors.get("submit_button")
        if submit_selector:
            page.locator(submit_selector).click()

        page.wait_for_timeout(2000)
        browser.close()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    data = build_registration_data(args.sessions)
    validate_required(data)
    run_registration(config, data, headless=args.headless)


if __name__ == "__main__":
    main()
