from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages


def login_view(request):
  # Si el usuario ya está autenticado, redirige a la página principal
  if request.user.is_authenticated:
    return redirect('home')  # Cambia 'home' por tu URL de inicio principal

  if request.method == "POST":
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
      user = form.get_user()
      login(request, user)
      messages.success(request, "¡Has iniciado sesión exitosamente!")

      # Redirigir a la página anterior o a la principal
      next_url = request.GET.get('next', 'home')  # 'home' es un ejemplo, cámbialo según sea necesario
      return redirect(next_url)
    else:
      messages.error(request, "Nombre de usuario o contraseña incorrectos.")
  else:
    form = AuthenticationForm()

  return render(request, "login.html", {"form": form})


def logout_view(request):
  logout(request)
  messages.success(request, "Has cerrado sesión.")
  return redirect("login")  # Redirige a la página de login después del logout
