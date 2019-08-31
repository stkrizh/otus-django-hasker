from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from .forms import SignUpForm


class SignUp(CreateView):
    form_class = SignUpForm
    model = get_user_model()
    success_url = reverse_lazy("index")
    template_name = "users/signup.html"

    def form_valid(self, *args, **kwargs):
        messages.success(self.request, "Thank you for registration!")
        return super().form_valid(*args, **kwargs)
