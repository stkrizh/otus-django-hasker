import logging

from django.db.models import F, Sum
from django.db.models.signals import post_delete, post_save

from .models import Answer, AnswerVote, Question, QuestionVote


logger = logging.getLogger(__name__)


def answer_created(sender, instance, created, raw, *args, **kwargs):
    """ Update `number_of_answers` of `Question` model.
    """
    if created and not raw:
        Question.objects.filter(pk=instance.question.pk).update(
            number_of_answers=(F("number_of_answers") + 1)
        )
        logger.debug(
            f"Number of answers has been increased "
            f"for {instance.question.pk}"
        )


def answer_deleted(sender, instance, *args, **kwargs):
    """ Update `number_of_answers` of `Question` model.
    """
    Question.objects.filter(pk=instance.question.pk).update(
        number_of_answers=(F("number_of_answers") - 1)
    )
    logger.debug(
        f"Number of answers has been decreased "
        f"for {instance.question.pk}. Answer has been deleted"
    )


def vote_created(sender, instance, created, raw, *args, **kwargs):
    """ Update `rating` of `Answer` / `Question` model after
    a `Vote` instance creation.
    """
    post_model = type(instance.to)
    qs = post_model.objects.filter(pk=instance.to.pk)

    if raw:
        return None

    if created:
        qs.update(
            rating=(F("rating") + instance.value),
            number_of_votes=(F("number_of_votes") + 1),
        )
        logger.debug(
            f"Number of votes / rating have been changed "
            f"for {post_model} ({instance.pk})"
        )
    else:
        model = type(instance)
        query = model.objects.filter(to=instance.to).aggregate(Sum("value"))
        new_rating = query["value__sum"]

        if new_rating is not None:
            qs.update(rating=new_rating)
            logger.debug(
                f"Rating has been changed for {post_model} ({instance.pk})"
            )


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
    logger.debug(
        f"Rating has been changed for {post_model} ({instance.pk}). "
        f"Vote has been deleted"
    )


post_save.connect(vote_created, sender=AnswerVote)
post_save.connect(vote_created, sender=QuestionVote)
post_delete.connect(vote_deleted, sender=AnswerVote)
post_delete.connect(vote_deleted, sender=QuestionVote)

post_save.connect(answer_created, sender=Answer)
post_delete.connect(answer_deleted, sender=Answer)
