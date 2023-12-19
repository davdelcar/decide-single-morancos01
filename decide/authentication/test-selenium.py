import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from django.test import LiveServerTestCase
import requests

class LoginTest(LiveServerTestCase):
    
    def setUp(self):
        # Configura el navegador web (asegúrate de que tengas ChromeDriver u otro driver instalado)
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)  # Espera implícita

    def test_login_bad_process(self):
        # Abre la aplicación web en la URL deseada
        self.driver.get(f"{self.live_server_url}/authentication/signin/")

        # Realiza acciones en la página de inicio de sesión (puedes personalizar según la estructura de tu página)
        username_input = self.driver.find_element(By.NAME, "identifier")  # Reemplaza con el nombre real del campo de usuario
        username_input.send_keys("testuser")  # Reemplaza con un nombre de usuario válido

        password_input = self.driver.find_element(By.NAME, "password")  # Reemplaza con el nombre real del campo de contraseña
        password_input.send_keys("testwrongpass")  # Reemplaza con una contraseña válida

        remember_me_checkbox = self.driver.find_element(By.NAME, "remember_me")  # Reemplaza con el nombre real del checkbox
        remember_me_checkbox.click()

        # Envía el formulario (por ejemplo, si hay un botón de enviar)
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")  # Reemplaza con el selector real del botón de envío
        submit_button.click()

        # Espera a que se cargue la página después de iniciar sesión (puedes ajustar el tiempo según la velocidad de carga de tu aplicación)
        time.sleep(3)

        # Realiza aserciones para verificar que estás en la página después de iniciar sesión
        go_to_profile_button = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Ir a tu Perfil')]")
        self.assertIsNotNone(go_to_profile_button)

    def tearDown(self):
        # Cierra el navegador al finalizar las pruebas
        self.driver.quit()

if __name__ == "__main__":
    LiveServerTestCase.main()