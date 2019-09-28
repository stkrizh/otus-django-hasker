from django.contrib import admin

from .models import Answer, AnswerVote, Question, QuestionVote, Tag


admin.site.register(Answer)
admin.site.register(AnswerVote)
admin.site.register(Question)
admin.site.register(QuestionVote)
admin.site.register(Tag)
