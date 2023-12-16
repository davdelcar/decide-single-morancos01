from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from .forms import LoginForm
from django.shortcuts import render
from voting.models import Voting
from django.views.generic import TemplateView
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .serializers import UserSerializer



class GetUserView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)


class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})


class RegisterView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        pwd = request.data.get('password', '')
        if not username or not pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User(username=username)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)

class WelcomeView(TemplateView):
    template_name = 'welcome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user

        closed_votings = Voting.objects.filter(tally__isnull=False)
        context['closed_votings'] = closed_votings

        open_votings = Voting.objects.filter(start_date__isnull=False, end_date__isnull=True)
        context['open_votings'] = open_votings

        return context

class LoginView(TemplateView):
    template_name = 'login.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = 'login.html'
    
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        msg = None

        if form.is_valid():
            identifier = form.cleaned_data.get("identifier")
            password = form.cleaned_data.get("password")
            remember_me = form.cleaned_data.get("remember_me")

            # Verifica si el identificador es un correo electrónico
            if '@' in identifier:
                try:
                    # Autenticar por correo electrónico
                    user = User.objects.get(email=identifier)
                    username = user.username
                    user = authenticate(request, username=username, password=password)
                except User.DoesNotExist:
                    user = None
            else:
                # Autenticar por nombre de usuario
                user = authenticate(request, username=identifier, password=password)
                username = identifier

            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)

                return redirect("/")
            else:
                msg = "Credenciales incorrectas"
        else:
            msg = "Error en el formulario"

        return render(request, self.template_name, {"form": form, "msg": msg, "user": None})

    def get(self, request, *args, **kwargs):
        form = LoginForm(None)
        return render(request, self.template_name, {"form": form, "msg": None})

    
class UserProfileView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        # Agregar el formulario de cambio de contraseña al contexto
        context['password_change_form'] = PasswordChangeForm(self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        # Procesar el formulario de cambio de contraseña si se envió por POST
        password_change_form = PasswordChangeForm(request.user, request.POST)
        if password_change_form.is_valid():
            user = password_change_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña ha sido cambiada con éxito.')
        else:
            for field, errors in password_change_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        # Volver a renderizar la página con el formulario actualizado
        context = self.get_context_data()
        return self.render_to_response(context)
    
class RegisterFormView(TemplateView):
    template_name = 'register.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = 'register.html'

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        msg = None

        try:
            if form.is_valid():
                user = form.save()
                user.refresh_from_db()
                user.username = form.cleaned_data.get('username')
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.email = form.cleaned_data.get('email')
                user.save()
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(request, username=user.username, password=raw_password)
                login(request, user)
                # Usa self.template_name aquí
                return redirect("/")
            else:
                msg = "Error en el formulario"
        except IntegrityError:
            messages.error(request, 'Error: El usuario ya existe.')
        except ValueError as e:
            messages.error(request, f'Error en el formulario: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
        
        # Retorno de la vista en el caso de credenciales incorrectas o error en el formulario
        return render(request, self.template_name, {"form": form, "msg": msg, "user": None})

    def get(self, request, *args, **kwargs):
        form = RegisterForm(None)
        return render(request, self.template_name, {"form": form, "msg": None})
