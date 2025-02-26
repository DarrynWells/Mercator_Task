import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager


@pytest.fixture(scope="class", autouse=True)
def test_startup(request):
    print("\nRunning Test Setup...")
    gecko_driver_path = GeckoDriverManager().install()
    driver = webdriver.Firefox(service=Service(gecko_driver_path), options=None)
    driver.maximize_window()
    request.cls.driver = driver

@pytest.mark.usefixtures("test_startup")
class TestItemPurchase:

    @pytest.mark.dependency()
    def test_open_page(self):
        self.driver.get("https://www.saucedemo.com/")

    @pytest.mark.dependency(depends=["TestItemPurchase::test_open_page"])
    def test_login(self):
        wait = WebDriverWait(self.driver, 10)

        username = wait.until(EC.visibility_of_element_located((By.ID, "user-name")))
        username.send_keys("standard_user")
        password = self.driver.find_element(By.ID, "password")
        password.send_keys("secret_sauce")
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-button")))
        login_button.click()

    @pytest.mark.dependency(depends=["TestItemPurchase::test_login"])
    def test_purchase_item(self):
        # Variables to keep track of the highest price and associated button
        highest_price = -1
        highest_price_button = None

        # Find all inventory items
        wait = WebDriverWait(self.driver, 10)
        inventory_items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.inventory_item")))

        for item in inventory_items:
            # Extract price for the current item
            price_text = item.find_element(By.CSS_SELECTOR, ".inventory_item_price").text
            price = float(price_text.replace('$', '').strip())

            # Find the "Add to cart" button associated with this item
            add_to_cart_button = item.find_element(By.CSS_SELECTOR, "button[id^='add-to-cart-'")

            # Update the highest price if this item has a higher price
            if price > highest_price:
                highest_price = price
                highest_price_button = add_to_cart_button

        # If a button with the highest price is found, click it
        if highest_price_button:
            highest_price_button.click()
