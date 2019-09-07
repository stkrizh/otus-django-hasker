import re

from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from .models import Answer, Question, VOTE_CHOICES


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("content",)


class AskForm(forms.ModelForm):
    tags = forms.CharField(max_length=512, required=False)

    class Meta:
        model = Question
        fields = ("content", "title")

    def clean_tags(self):
        raw_tags = self.cleaned_data["tags"]
        raw_tags, _ = re.subn(r"\s+", " ", raw_tags)

        tags = (tag.strip().lower() for tag in raw_tags.split(","))
        tags = list(filter(bool, tags))

        if len(tags) > settings.QUESTIONS_MAX_NUMBER_OF_TAGS:
            n = settings.QUESTIONS_MAX_NUMBER_OF_TAGS
            raise forms.ValidationError(f"The maximum number of tags is {n}.")

        if any(len(tag) > settings.QUESTIONS_MAX_TAG_LEN for tag in tags):
            raise forms.ValidationError(
                "Ensure each tag has at most 128 characters."
            )

        return tags


class VoteForm(forms.Form):
    target_id = forms.IntegerField()
    value = forms.TypedChoiceField(choices=VOTE_CHOICES, coerce=int)

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop("model")
        super().__init__(*args, **kwargs)

    def clean_target_id(self):
        target_id = self.cleaned_data["target_id"]

        try:
            target = self.model.objects.get(pk=target_id)
        except ObjectDoesNotExist:
            raise forms.ValidationError("Target object doesn't exist.")

        self.cleaned_data["target"] = target
