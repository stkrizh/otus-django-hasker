from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["content"] = "Azaza!"
        return context
