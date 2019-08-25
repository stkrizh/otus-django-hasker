from django.contrib import admin

from .models import Answer, AnswerVote, Question, QuestionVote, Tag


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


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
