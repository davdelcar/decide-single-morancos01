#from allauth.socialaccount.models import SocialApp
from base import mods
from django.contrib.auth.models import User
#from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from voting.models import Voting
from voting.models import Question, QuestionOption
from django.contrib.auth.hashers import check_password
from django.contrib.messages import get_messages
from django.utils.translation import activate


from .forms import LoginForm

class AuthTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        u = User(username='voter1')
        u.set_password('123')
        u.save()

        u2 = User(username='admin')
        u2.set_password('admin')
        u2.is_superuser = True
        u2.save()

    def tearDown(self):
        self.client = None

    def testLogin(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

    def testLoginFail(self):
        data = {'username': 'voter1', 'password': '321'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def testGetuser(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 200)

        user = response.json()
        self.assertEqual(user['id'], 1)
        self.assertEqual(user['username'], 'voter1')

    def testGetuserInventedToken(self):
        token = {'token': 'invented'}
        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def testGetuserInvalidToken(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def testLogout(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 0)

    def testRegisterBadPermissions(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 401)

    def testRegisterBadRequest(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def testRegisterUserAlreadyExist(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update(data)
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def testRegister(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1', 'password': 'pwd1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            sorted(list(response.json().keys())),
            ['token', 'user_pk']
        )
class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("signin")
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
        self.assertIsInstance(response.context["form"], LoginForm)
        self.assertIsNone(response.context["msg"])

    def test_post_valid_credentials(self):
        data = {"identifier": "testuser", "password": "testpass", "remember_me": False}
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "welcome.html")

    def test_post_invalid_credentials(self):
        data = {"identifier": "testuser", "password": "wrongpass", "remember_me": False}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
        self.assertIsInstance(response.context["form"], LoginForm)
        self.assertEqual(response.context["msg"], "Credenciales incorrectas")

    def test_post_invalid_form(self):
        data = {"identifier": "", "password": "", "remember_me": False}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
        self.assertIsInstance(response.context["form"], LoginForm)
        self.assertEqual(response.context["msg"], "Error en el formulario")

class WelcomeTestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("welcome")
        self.url_logout = reverse("logout")
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_get_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "welcome.html")
         
        self.assertContains(response, "Go to Login", msg_prefix="La cadena esperada no se encontró en la respuesta.")


    
    def test_get_authenticated_user(self):
        
        self.client.force_login(self.user)
        q = Question(desc='test question', types='OQ')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        open_voting = Voting(name='test open voting', question=q , start_date="2023-01-01")
        open_voting.save()
        closed_voting = Voting(name='test open voting', question=q , start_date="2023-01-01", end_date="2023-02-01", tally={})
        closed_voting.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "welcome.html")

        self.assertNotContains(response, "Go to Login")

        self.assertContains(response, "Votaciones Abiertas:")
        self.assertContains(response, reverse("booth", args=[open_voting.id]))

        self.assertContains(response, "Votaciones Cerradas:")
        self.assertContains(response, reverse("visualizer", args=[closed_voting.id]))

    def test_logout_from_welcome_page(self):

        login_data = {'username': 'testuser', 'password': 'testpass'}
        login_response = self.client.post(reverse('login'), login_data, format='json')
        self.assertEqual(login_response.status_code, 200)

        self.client.force_login(self.user)  # Asegúrate de que el usuario esté autenticado
        response_welcome = self.client.get(self.url)
        self.assertEqual(response_welcome.status_code, 200)

        users_before_logout = User.objects.filter(id=self.user.id).count()+1

        self.assertContains(response_welcome, 'Cerrar Sesión', html=True)

        logout_response = self.client.post(self.url_logout)
        self.assertEqual(logout_response.status_code, 200)  # Código de estado OK después del cierre de sesión

        users_after_logout = User.objects.filter(id=self.user.id).count()
        self.assertEqual(users_after_logout, users_before_logout - 1)
    

class UserProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("user_profile")
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def testChangePasswordValidForm(self):
        self.client.force_login(self.user)

        activate('es')
        
        data = {
            'old_password': 'testpass',
            'new_password1': 'JMC112003',
            'new_password2': 'JMC112003',
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="testuser")
        self.assertTrue(check_password('JMC112003', user.password))
        self.assertContains(response, 'Tu contraseña ha sido cambiada con éxito.')

    # Comprueba dos restricciones: la contraseña actual es incorrecta y la contraseña nueva es muy corta (menos de 8 carracteres)
    def testChangePasswordInvalidForm(self):
        self.client.force_login(self.user)

        activate('en')

        data = {
            'old_password': 'wrongpassword',
            'new_password1': 'short',
            'new_password2': 'short',
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="testuser")
        self.assertTrue(check_password('testpass', user.password))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('old_password: Your old password was entered incorrectly. Please enter it again.', messages)
        self.assertIn('new_password2: This password is too short. It must contain at least 8 characters.', messages)

    def testChangePasswordNumericPassword(self): #No puede ser numérica
        self.client.force_login(self.user)

        activate('en')

        data = {
            'old_password': 'testpass',
            'new_password1': '12345678',
            'new_password2': '12345678',
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="testuser")
        self.assertTrue(check_password('testpass', user.password))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('new_password2: This password is entirely numeric.', messages)

    def testChangePasswordUsernamePassword(self): #No puede ser similar al username
        self.client.force_login(self.user)

        activate('en')

        data = {
            'old_password': 'testpass',
            'new_password1': 'testuser',
            'new_password2': 'testuser',
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="testuser")
        self.assertTrue(check_password('testpass', user.password))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('new_password2: The password is too similar to the username.', messages)

    def testChangePasswordCommonPassword(self):
        self.client.force_login(self.user)

        activate('en')

        data = {
            'old_password': 'testpass',
            'new_password1': 'password123',
            'new_password2': 'password123',
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="testuser")
        self.assertTrue(check_password('testpass', user.password))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('new_password2: This password is too common.', messages)

    def testChangePasswordUnauthenticatedUser(self):

        response = self.client.post(self.url, follow=True)  # Agrega follow=True para seguir redirecciones
        self.assertEqual(response.status_code, 200)  # Se espera un código 200 después de la redirección
        self.assertContains(response, 'Login')
        self.assertNotContains(response, 'Deseo cambiar de contraseña')  # Verifica que el botón de cambio de contraseña no esté presente

    def testGetAuthenticatedUser(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")
        self.assertEqual(response.context["user"], self.user)

    def testGetUnauthenticatedUser(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inicia sesión para acceder a tu perfil de usuario.")
        self.assertContains(response, reverse("signin"))
 
class RegisterUserTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("registerUser")
        self.user = User.objects.create_user(username="createuser", password="createuser123", email="createuser@gmail.com")
        self.data = {
            'username' : 'testuser',
            'first_name' : 'test',
            'last_name' : 'user',
            'email' : 'test@gmail.com',
            'password1' : '123456789test',
            'password2' : '123456789test'
        }

    def testGetRegisterFrom(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
        self.assertContains(response, "form")

    def testPostValidRegistration(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def testPostInvalidRegistration(self):
        data = {}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
        self.assertContains(response, 'This field is required.', status_code=200, html=True)

    def testPostExistingUserRegistration(self):
        self.data['username'] = 'createuser'
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
        self.assertContains(response, 'A user with that username already exists.', status_code=200, html=True)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def testPostValueErrorRegistration(self):
        self.data['password2'] = 'invalidpassword'
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
        self.assertContains(response, 'The two password fields didn’t match.', status_code=200, html=True)

    def testPostDuplicateEmailRegistration(self):
        self.data['email'] = 'createuser@gmail.com'
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
        self.assertContains(response, 'El correo electrónico ya está en uso', status_code=200, html=True)
        self.assertFalse(User.objects.filter(email='testuser@example.com').exists())

    def testPostInvalidRegistrationEmptyFields(self):
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

        for field in fields:
            with self.subTest(field=field):
                data = {'username': 'createuser', 'first_name': 'test', 'last_name': 'user',
                        'email': 'test@gmail.com', 'password1': '123456789test', 'password2': '123456789test'}

                data[field] = ''

                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "register.html")
                self.assertContains(response, 'This field is required.', status_code=200, html=True)