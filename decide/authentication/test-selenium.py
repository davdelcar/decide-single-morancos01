from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WelcomeLoginTests(StaticLiveServerTestCase):
    def setUp(self):
        # Configuración de Selenium
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        super().setUp()

    def tearDown(self):
        self.driver.quit()
        super().tearDown()

    def test_welcome_page_loads(self):

        self.driver.get(f"{self.live_server_url}")

        self.assertIn("Decide", self.driver.title)
        self.assertIn("Welcome to Decide", self.driver.page_source)

        ir_a_censos_button = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Go to Census')]"))
        )
        self.assertTrue(ir_a_censos_button.is_displayed())



