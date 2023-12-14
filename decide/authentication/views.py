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
from django.views.generic import TemplateView
from django.views import View
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
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

class WelcomeView(APIView):
    def get(self, request):
        return render(request, 'welcome.html')

    def post(self, request):
        # Si necesitas manejar solicitudes POST, puedes agregar lógica aquí
        return Response({'message': 'This is a welcome view for POST requests.'}, status=status.HTTP_200_OK)

class LoginView(TemplateView):
    def post(self, request):
        form = LoginForm(request.POST)

        msg = None

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            remember_me = form.cleaned_data.get("remember_me")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)

                next_url = request.GET.get("next", None)
                if next_url:
                    return redirect(next_url)
                return redirect("/authentication/welcome")
            else:
                msg = "Credenciales incorrectas"
        else:
            msg = "Error en el formulario"

        return render(request, "login.html", {"form": form, "msg": msg})

    def get(self, request):
        form = LoginForm(None)

        return render(request, "login.html", {"form": form, "msg": None})
    
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

