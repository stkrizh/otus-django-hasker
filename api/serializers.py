from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import serializers

from questions.models import Answer, AnswerVote, Question, QuestionVote


class QuestionTagsField(serializers.ListField):
    def get_attribute(self, question):
        return [str(tag) for tag in question.tags.all()]

    def run_validation(self, data):
        tags = (tag.strip().lower() for tag in data)
        tags = set(filter(bool, tags))
        return super().run_validation(sorted(tags))


class UserSerializer(serializers.ModelSerializer):
    photo_big_url = serializers.SerializerMethodField()
    photo_small_url = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ["id", "username", "photo_big_url", "photo_small_url"]

    def get_photo_big_url(self, user):
        return user.get_photo_url()

    def get_photo_small_url(self, user):
        return user.get_thumb_url()


class QuestionSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = QuestionTagsField(
        child=serializers.CharField(max_length=settings.QUESTIONS_MAX_TAG_LEN),
        allow_empty=True,
        max_length=settings.QUESTIONS_MAX_NUMBER_OF_TAGS,
    )

    class Meta:
        model = Question
        fields = "__all__"
        read_only_fields = [
            "author",
            "number_of_answers",
            "number_of_votes",
            "posted",
            "rating",
        ]

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        new_question = super().create(validated_data)
        new_question.add_tags(tags, new_question.author)
        return new_question


class AnswerSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = "__all__"
        read_only_fields = [
            "author",
            "is_accepted",
            "number_of_votes",
            "posted",
            "question",
            "rating",
        ]


class AnswerDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = "__all__"
        read_only_fields = [
            "author",
            "content",
            "number_of_votes",
            "posted",
            "question",
            "rating",
        ]


class AnswerVoteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AnswerVote
        exclude = ["to"]
        read_only_fields = [
            "user",
            "timestamp",
        ]

    def validate(self, data):
        answer_pk = self.context["view"].kwargs["pk"]
        user = self.context["request"].user

        if AnswerVote.objects.filter(to=answer_pk, user=user).exists():
            raise serializers.ValidationError("Vote already exists.")
        return data


class QuestionVoteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = QuestionVote
        exclude = ["to"]
        read_only_fields = [
            "user",
            "timestamp",
        ]

    def validate(self, data):
        question_pk = self.context["view"].kwargs["pk"]
        user = self.context["request"].user

        if QuestionVote.objects.filter(to=question_pk, user=user).exists():
            raise serializers.ValidationError("Vote already exists.")
        return data
