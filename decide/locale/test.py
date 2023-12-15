from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import activate, deactivate_all, get_language, gettext
from django.contrib.auth.models import User
from django.utils.translation import activate, get_language, gettext
from django.utils import translation
from django.utils.translation import gettext_lazy as _

class ChangeLanguageFormTest(TestCase):

    def testChangeLanguageFormEnglish(self):

        response_post = self.client.post(reverse('set_language'), {'language': 'en'})
        self.assertEqual(response_post.status_code, 302)

        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'English')
        self.assertContains(response, '<form action="/i18n/setlang/" method="post" style="display: inline;">')
        self.assertContains(response, '<select name="language" onchange="javascript:form.submit()">')
        self.assertContains(response, '<option value="es" >Spanish</option>')
        self.assertContains(response, '<option value="en" selected="selected">English</option>')
                
        html_content = response.content.decode('utf-8')
        self.assertIn('Welcome to Decide!', html_content)
        

    def testChangeLanguageFormSpanish(self):
        
        response_post = self.client.post(reverse('set_language'), {'language': 'es'})
        self.assertEqual(response_post.status_code, 302)

        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Español')
        self.assertContains(response, '<form action="/i18n/setlang/" method="post" style="display: inline;">')
        self.assertContains(response, '<select name="language" onchange="javascript:form.submit()">')
        self.assertContains(response, '<option value="en" >Inglés</option>')
        self.assertContains(response, '<option value="es" selected="selected">Español</option>')
        
        html_content = response.content.decode('utf-8')
        self.assertIn('Bienvenido a Decide!', html_content)

    def testErrorChangeLanguageFormEnglish(self):

        response_post = self.client.post(reverse('set_language'), {'language': 'en'})
        self.assertEqual(response_post.status_code, 302)

        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Inglés')
               
        html_content = response.content.decode('utf-8')
        self.assertNotIn('Bienvenido a Decide!', html_content)

    def testErrorChangeLanguageFormSpanish(self):

        response_post = self.client.post(reverse('set_language'), {'language': 'es'})
        self.assertEqual(response_post.status_code, 302)

        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Spanish')

        html_content = response.content.decode('utf-8')
        self.assertNotIn('Welcome to Decide!', html_content)

    def testSpanishTranslation(self):
        #Vemos si se traducen las palabras correctamente al español desde el .po
        self.assertEqual(_("Congratulations. Your vote has been sent"), "Felicidades. Tu voto ha sido enviado.")
        deactivate_all()

    def testEnglishTranslation(self):
        #Vemos si se traducen las palabras correctamente al inglés desde el .po
        self.assertEqual(_("Gracias por unirte a nuestra plataforma de votación electrónica"), "Thank you for joining our electronic voting platform")
