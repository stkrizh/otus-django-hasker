from django.db.models import F
from django.db.models.signals import post_delete, post_save

from .models import Answer, AnswerVote, Question, QuestionVote


def answer_created(sender, instance, created, raw, *args, **kwargs):
    """ Update `number_of_answers` of `Question` model.
    """
    if created and not raw:
        Question.objects.filter(pk=instance.question.pk).update(
            number_of_answers=(F("number_of_answers") + 1)
        )


def answer_deleted(sender, instance, *args, **kwargs):
    """ Update `number_of_answers` of `Question` model.
    """
    Question.objects.filter(pk=instance.question.pk).update(
        number_of_answers=(F("number_of_answers") - 1)
    )


def vote_created(sender, instance, created, raw, *args, **kwargs):
    """ Update `rating` of `Answer` / `Question` model after
    a `Vote` instance creation.
    """
    post_model = type(instance.to)
    qs = post_model.objects.filter(pk=instance.to.pk)

    if created and not raw:
        qs.update(
            rating=(F("rating") + instance.value),
            number_of_votes=(F("number_of_votes") + 1),
        )
    else:
        qs.update(rating=(F("rating") + 2 * instance.value))


def vote_deleted(sender, instance, *args, **kwargs):
    """ Update `rating` of `Answer` / `Question` model after
    a `Vote` instance deletion.
    """
    post_model = type(instance.to)
    qs = post_model.objects.filter(pk=instance.to.pk)
    qs.update(
        rating=(F("rating") - instance.value),
        number_of_votes=(F("number_of_votes") - 1),
    )


post_save.connect(vote_created, sender=AnswerVote)
post_save.connect(vote_created, sender=QuestionVote)
post_delete.connect(vote_deleted, sender=AnswerVote)
post_delete.connect(vote_deleted, sender=QuestionVote)

post_save.connect(answer_created, sender=Answer)
post_delete.connect(answer_deleted, sender=Answer)
