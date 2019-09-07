from django.db.models import F
from django.db.models.signals import post_delete, post_save

from .models import AnswerVote, QuestionVote


def vote_created(sender, instance, created, *args, **kwargs):
    """ Update `rating` of `Answer` / `Question` model after
    a `Vote` instance creation.
    """
    post_model = type(instance.to)
    qs = post_model.objects.filter(pk=instance.to.pk)

    if created:
        qs.update(rating=(F("rating") + instance.value))
    else:
        qs.update(rating=(F("rating") + 2 * instance.value))


def vote_deleted(sender, instance, *args, **kwargs):
    """ Update `rating` of `Answer` / `Question` model after
    a `Vote` instance deletion.
    """
    post_model = type(instance.to)
    qs = post_model.objects.filter(pk=instance.to.pk)
    qs.update(rating=(F("rating") - instance.value))


post_save.connect(vote_created, sender=AnswerVote)
post_save.connect(vote_created, sender=QuestionVote)
post_delete.connect(vote_deleted, sender=AnswerVote)
post_delete.connect(vote_deleted, sender=QuestionVote)
