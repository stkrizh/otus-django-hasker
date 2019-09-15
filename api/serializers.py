from rest_framework import serializers

from questions.models import Answer, Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"
        read_only_fields = [
            "number_of_answers",
            "number_of_votes",
            "posted",
            "rating",
        ]


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = "__all__"
        read_only_fields = [
            "is_accepted",
            "number_of_votes",
            "posted",
            "question",
            "rating",
        ]
