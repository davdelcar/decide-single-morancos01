from django.test import TestCase
from django.urls import reverse
from django.utils.translation import activate, deactivate_all
from django.utils.translation import gettext_lazy as _

class ChangeLanguageFormTest(TestCase):

    def test_change_languag_english(self):

        response_post = self.client.post(reverse('set_language'), {'language': 'en'})
        self.assertEqual(response_post.status_code, 302)

        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'English')
        self.assertContains(response, '<form action="/i18n/setlang/" method="post" style="display: inline;">')
        self.assertContains(response, '<select name="language" onchange="javascript:form.submit()">')
        self.assertContains(response, '<option value="es" >Spanish</option>')
        self.assertContains(response, '<option value="fr" >French</option>')
        self.assertContains(response, '<option value="en" selected="selected">English</option>')
                
        html_content = response.content.decode('utf-8')
        self.assertIn('Welcome to Decide!', html_content)
        
    def test_change_language_spanish(self):
        
        response_post = self.client.post(reverse('set_language'), {'language': 'es'})
        self.assertEqual(response_post.status_code, 302)

        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Español')
        self.assertContains(response, '<form action="/i18n/setlang/" method="post" style="display: inline;">')
        self.assertContains(response, '<select name="language" onchange="javascript:form.submit()">')
        self.assertContains(response, '<option value="en" >Inglés</option>')
        self.assertContains(response, '<option value="es" selected="selected">Español</option>')
        self.assertContains(response, '<option value="fr" >Francés</option>')
        
        html_content = response.content.decode('utf-8')
        self.assertIn('Bienvenido a Decide!', html_content)

    def test_change_language_french(self):

        response_post = self.client.post(reverse('set_language'), {'language': 'fr'})
        self.assertEqual(response_post.status_code, 302)

        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Français')
        self.assertContains(response, '<form action="/i18n/setlang/" method="post" style="display: inline;">')
        self.assertContains(response, '<select name="language" onchange="javascript:form.submit()">')
        self.assertContains(response, '<option value="en" >Anglais</option>')
        self.assertContains(response, '<option value="es" >Espagnol</option>')
        self.assertContains(response, '<option value="fr" selected="selected">Français</option>')

        html_content = response.content.decode('utf-8')
        self.assertIn('Bienvenue à Decide!', html_content)

    def test_error_change_language_english(self):

        response_post = self.client.post(reverse('set_language'), {'language': 'en'})
        self.assertEqual(response_post.status_code, 302)

        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Inglés')
               
        html_content = response.content.decode('utf-8')
        self.assertNotIn('Bienvenido a Decide!', html_content)

    def test_error_change_language_spanish(self):

        response_post = self.client.post(reverse('set_language'), {'language': 'es'})
        self.assertEqual(response_post.status_code, 302)

        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Spanish')

        html_content = response.content.decode('utf-8')
        self.assertNotIn('Welcome to Decide!', html_content)

    def test_error_change_language_french(self):

        response_post = self.client.post(reverse('set_language'), {'language': 'fr'})
        self.assertEqual(response_post.status_code, 302)

        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'French')

        html_content = response.content.decode('utf-8')
        self.assertNotIn('Welcome to Decide!', html_content)

    def test_spanish_translation(self):

        #Vemos si se traducen las palabras correctamente al español desde el .po
        response_post = self.client.post(reverse('set_language'), {'language': 'es'})
        activate('es')
        self.assertEqual(response_post.status_code, 302)
        self.assertEqual(_("Congratulations. Your vote has been sent"), "Felicidades. Tu voto ha sido enviado.")
        deactivate_all()

    def test_english_translation(self):

        #Vemos si se traducen las palabras correctamente al inglés desde el .po
        response_post = self.client.post(reverse('set_language'), {'language': 'en'})
        activate('en')
        self.assertEqual(response_post.status_code, 302)
        self.assertEqual(_("Gracias por unirte a nuestra plataforma de votación electrónica"), "Thank you for joining our electronic voting platform")
        deactivate_all()

    def test_french_translation(self):

        #Vemos si se traducen las palabras correctamente al francés desde el .po
        response_post = self.client.post(reverse('set_language'), {'language': 'fr'})
        activate('fr')
        self.assertEqual(response_post.status_code, 302)
        self.assertEqual(_("Gracias por unirte a nuestra plataforma de votación electrónica"), "Merci d'avoir rejoint notre plateforme de vote électronique")
        deactivate_all()