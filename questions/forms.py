import re

from django import forms
from django.conf import settings

from .models import Question


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
