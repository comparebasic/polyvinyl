from playwright.sync_api import Page, Playwright, sync_playwright, expect
from . import fixtures
from urllib.request import urlopen
import re

def test_has_title(page: Page):
    page.goto("http://localhost:3000")

    expect(page).to_have_title("PolyVinyl Example  - Login or Sign Up")

def test_login(page: Page):
    user = fixtures.get_user("testone")
    fixtures.wipe_user(user)

    page.goto("http://localhost:3000/auth/login")
    page.get_by_role("textbox", name="Email").click()
    page.get_by_role("textbox", name="Email").fill(user["email"])
    page.get_by_text("Login or Create Account").click()
    page.get_by_text("Use password").click()
    page.get_by_role("textbox", name="Password 👁").click()
    page.get_by_role("textbox", name="Password 👁").fill(user["password"])
    page.get_by_text("Register new user").click()
    page.get_by_role("textbox", name="Fullname Sign up for our").click()
    page.get_by_role("textbox", name="Fullname Sign up for our").fill(user["fullname"])
    page.get_by_text("Sign up for our Newsletters").click()
    page.get_by_text("Products and features").nth(1).click()
    page.get_by_role("button", name="Submit").click()
    page.get_by_role("heading", name="Dashboard").click()
    page.get_by_text("Hi, {} ({})".format(user["fullname"], user["email"])).click()
    page.get_by_role("link", name="logout", exact=True).click()
    page.get_by_text("Login or Sign Up").click()

    # relogin
    page.get_by_text("Login or Create Account").click()
    page.get_by_role("textbox", name="Email").click()
    page.get_by_role("textbox", name="Email").fill(user["email"])
    page.get_by_text("Use password").click()
    page.get_by_role("textbox", name="Password 👁").click()
    page.get_by_role("textbox", name="Password 👁").fill(user["password"])
    page.get_by_role("button", name="Submit").click()
    page.get_by_role("heading", name="Dashboard").click()
    page.get_by_text("Hi, {} ({})".format(user["fullname"], user["email"])).click()
    page.get_by_role("link", name="logout", exact=True).click()
    page.get_by_text("Login or Sign Up").click()

    # login with code 
    page.get_by_role("textbox", name="Email").click()
    page.get_by_role("textbox", name="Email").fill(user["email"])
    page.get_by_text("Login or Create Account").click()
    page.get_by_text("Email a code/link").click()
    page.get_by_role("button", name="Submit").click()

    f = urlopen("http://localhost:3050/")
    email = f.read()
    regex = re.compile(b"to login to Authdinger:\n\n([0-9]{6})")
    match = regex.search(email)
    code = match.groups()[0].decode("utf-8")

    page.get_by_text("sent to {}".format(user["email"])).click()
    page.get_by_role("spinbutton", name="Enter Code:").click()
    page.get_by_role("spinbutton", name="Enter Code:").type(code)
    page.get_by_label("Login").click()
    page.get_by_text("Hi, {} ({})".format(user["fullname"], user["email"])).click()

    page.get_by_role("link", name="Subscriptions", exact=True).click()
    page.get_by_role("heading", name="Newsletter Subscriptions").click()
    expect(page.get_by_text("General newsletter")).to_be_checked()
    #expect(page.get_by_text("Products and features")).to_be_checked()
    page.get_by_role("link", name="Logout", exact=True).click()

    f = urlopen("http://localhost:3050/register")
    email = f.read()
    regex = re.compile(b"href=\"([^\"]+)\">manage")
    match = regex.search(email)
    url = match.groups()[0].decode("utf-8")
    print("Url {}".format(url))
    page.goto(url)
    page.get_by_role("heading", name="Newsletter Subscriptions").click()
    expect(page.get_by_text("General newsletter")).not_to_be_checked()
    expect(page.get_by_text("Products and features")).not_to_be_checked()
