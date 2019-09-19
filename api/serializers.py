from django.contrib.auth import get_user_model

from rest_framework import serializers

from questions.models import Answer, Question


class AuthorSerializer(serializers.ModelSerializer):
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
    author = AuthorSerializer(read_only=True)
    tags = serializers.StringRelatedField(many=True)

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


class AnswerSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

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
