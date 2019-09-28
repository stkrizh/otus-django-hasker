from django.contrib.auth import get_user_model

from rest_framework import serializers

from questions.models import Answer, Question, Tag


class QuestionTagsField(serializers.ListField):
    def get_attribute(self, question):
        return [str(tag) for tag in question.tags.all()]


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


class QuestionSerializer(serializers.Serializer):
    title = serializers.CharField()
    content = serializers.CharField()
    tags = QuestionTagsField(
        child=serializers.CharField(), allow_empty=True, max_length=3
    )
    author = AuthorSerializer(read_only=True)
    number_of_answers = serializers.IntegerField(read_only=True)
    number_of_votes = serializers.IntegerField(read_only=True)
    rating = serializers.IntegerField(read_only=True)
    posted = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        import ipdb; ipdb.set_trace()


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
