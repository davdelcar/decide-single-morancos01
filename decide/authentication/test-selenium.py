from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from django.test import LiveServerTestCase


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

class LoginTest(LiveServerTestCase):

    def setUp(self):
        # Configura el navegador web (asegúrate de que tengas ChromeDriver u otro driver instalado)
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)  # Espera implícita

    def test_login_process(self):
        # Abre la aplicación web en la URL deseada
        self.driver.get(f"{self.live_server_url}/authentication/signin/")

        # Realiza acciones en la página de inicio de sesión (puedes personalizar según la estructura de tu página)
        username_input = self.driver.find_element(By.NAME, "identifier")  # Reemplaza con el nombre real del campo de usuario
        username_input.send_keys("testuser")  # Utiliza el nombre de usuario creado a través de la API

        password_input = self.driver.find_element(By.NAME, "password")  # Reemplaza con el nombre real del campo de contraseña
        password_input.send_keys("testpassword")  # Utiliza la contraseña del usuario creado a través de la API

        remember_me_checkbox = self.driver.find_element(By.NAME, "remember_me")  # Reemplaza con el nombre real del checkbox
        remember_me_checkbox.click()

        # Envía el formulario (por ejemplo, si hay un botón de enviar)
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")  # Reemplaza con el selector real del botón de envío
        submit_button.click()

        # Espera a que se cargue la página después de iniciar sesión (puedes ajustar el tiempo según la velocidad de carga de tu aplicación)
        time.sleep(3)

        # Realiza aserciones para verificar que estás en la página después de iniciar sesión
        error_message = self.driver.find_element(By.XPATH, "//div[@class='alert alert-danger']")  # Reemplaza con el selector real del mensaje de error
        self.assertIsNotNone(error_message)

    def tearDown(self):
        # Cierra el navegador al finalizar las pruebas
        self.driver.quit()

if __name__ == "__main__":
    LiveServerTestCase.main()

