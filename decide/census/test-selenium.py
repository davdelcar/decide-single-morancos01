from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from django.test import LiveServerTestCase

class CensusTestCase(LiveServerTestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        super().setUp()

    def tearDown(self):
        self.driver.quit()
        super().tearDown()

    def test_census_page_loads_and_elements(self):
        self.driver.get(f"{self.live_server_url}")

        self.assertIn("Decide", self.driver.title)
        self.assertIn("Welcome to Decide", self.driver.page_source)

        ir_a_censos_button = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Go to Census')]"))
        )
        ir_a_censos_button.click()

        census_table = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "table-striped"))
        )

        voting_id_column = census_table.find_element(By.XPATH, "//th[contains(text(), 'Voting ID')]")
        voter_id_column = census_table.find_element(By.XPATH, "//th[contains(text(), 'Voter ID')]")

        self.assertIsNotNone(voting_id_column)
        self.assertIsNotNone(voter_id_column)

    def test_import_census_page_loads_and_elements(self):
        self.driver.get(f"{self.live_server_url}/census")

        self.assertIn("Decide", self.driver.title)
        self.assertIn("Census", self.driver.page_source)

        ir_a_import_censos_button = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Import Census')]"))
        )
        ir_a_import_censos_button.click()

        self.assertIn("Importar Censo", self.driver.page_source)

        volver_button = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Return')]"))
        )
        volver_button.click()

        self.assertIn("In this section you can see all the censuses created.", self.driver.page_source)

