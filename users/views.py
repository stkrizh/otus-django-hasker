from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.views.generic.edit import CreateView, FormView
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .forms import LogInForm, SignUpForm


class LogIn(FormView):
    form_class = LogInForm
    success_url = reverse_lazy("index")
    template_name = "users/login.html"

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            messages.info(self.request, "You are already logged in.")
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        messages.success(self.request, "You have succesfully logged in!")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class SignUp(CreateView):
    form_class = SignUpForm
    model = get_user_model()
    success_url = reverse_lazy("index")
    template_name = "users/signup.html"

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            messages.info(self.request, "You are already logged in.")
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, *args, **kwargs):
        messages.success(self.request, "Thank you for registration!")
        return super().form_valid(*args, **kwargs)
