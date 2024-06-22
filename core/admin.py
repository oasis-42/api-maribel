from django.contrib import admin

from core.models import Theme, Skill, Feedback, SkillFeedback, OriginalEssayText, RefinedEssayText, MotivationalText, UserConfig

admin.site.register(Theme)
admin.site.register(Skill)
admin.site.register(Feedback)
admin.site.register(SkillFeedback)
admin.site.register(OriginalEssayText)
admin.site.register(RefinedEssayText)
admin.site.register(MotivationalText)
admin.site.register(UserConfig)
