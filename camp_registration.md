# Summer Camp Registration Automation

This repo includes a Playwright script that can auto-fill a summer camp
registration form. Customize the selectors in `camp_registration_config.json`
so they match the real registration page.

## 1) Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install playwright
playwright install
```

## 2) Update selectors

Open `camp_registration_config.json` and replace the URL and CSS selectors with
values from the registration form.

## 3) Provide data via environment variables

```bash
export CAMP_CHILD_FIRST="FirstName"
export CAMP_CHILD_LAST="LastName"
export CAMP_PARENT_NAME="Parent Name"
export CAMP_CARD_NUMBER="4111111111111111"
export CAMP_CARD_EXP="12/34"
export CAMP_CARD_CVV="123"
export CAMP_BILLING_ZIP="12345"
```

## 4) Run the automation

```bash
python camp_registration.py --sessions 1 2 3 5 7 --headless=false
```

The script uses the session list to format the selector template
`session_checkbox_template`. For example, `#session-{session}` becomes
`#session-1`, `#session-2`, etc.

> Tip: Run in headed mode (the default) so you can verify the filled form before
> submission. Remove or edit the `submit_button` selector if you want to prevent
> auto-submission.
