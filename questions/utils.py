from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail


def send_notification_about_new_answer(
    request, to: str, question_id: int
) -> None:
    question_url = request.build_absolute_uri(
        reverse("question_detail", kwargs=dict(question_id=question_id))
    )
    message = (
        f"You've got a new answer for "
        f"<a href='{question_url}'>your question</a><br><br>"
        f"Best regards!"
    )
    send_mail(
        "Hasker - new answer!",
        "",
        settings.EMAIL_FROM,
        [to],
        fail_silently=False,
        html_message=message,
    )
