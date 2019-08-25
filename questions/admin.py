from django.contrib import admin

from .models import Answer, AnswerVote, Question, QuestionVote


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(AnswerVote)
class AnswerVoteAdmin(admin.ModelAdmin):
    pass


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionVote)
class QuestionVoteAdmin(admin.ModelAdmin):
    pass
