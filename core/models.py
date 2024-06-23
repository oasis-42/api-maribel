from django.db import models
from django.contrib.auth.models import User


class Theme(models.Model):
    theme = models.AutoField(primary_key=True, db_column='theme_id')
    title = models.CharField(max_length=255)
    year = models.IntegerField()


class Skill(models.Model):
    skill = models.AutoField(primary_key=True, db_column='skill_id')
    skill_type = models.CharField(max_length=1)
    skill_description = models.CharField(max_length=100)


class Feedback(models.Model):
    feedback = models.AutoField(primary_key=True, db_column='feedback_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    theme = models.ForeignKey(Theme, on_delete=models.DO_NOTHING, db_column='theme_id')
    grade = models.IntegerField()
    quality = models.DecimalField(max_digits=5, decimal_places=2)
    creation_date = models.DateTimeField(auto_now_add=True)


class SkillFeedback(models.Model):
    skill_feedback = models.AutoField(primary_key=True)
    skill = models.ForeignKey(Skill, on_delete=models.DO_NOTHING, db_column='skill_id')
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, db_column='feedback_id')
    grade = models.IntegerField()
    text = models.TextField()


class OriginalEssayText(models.Model):
    feedback = models.OneToOneField(Feedback, on_delete=models.CASCADE, primary_key=True, db_column='feedback_id')
    introduction = models.TextField()
    development = models.TextField()
    conclusion = models.TextField()


class RefinedEssayText(models.Model):
    feedback = models.OneToOneField(Feedback, on_delete=models.CASCADE, primary_key=True, db_column='feedback_id')
    introduction = models.TextField()
    development = models.TextField()
    conclusion = models.TextField()


class MotivationalText(models.Model):
    motivational_text = models.AutoField(primary_key=True, db_column='motivational_text_id')
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, db_column='theme_id')
    title = models.CharField(max_length=200)
    text = models.TextField()


class UserConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, db_column='user_id')
    generate_punctuation = models.BooleanField(default=False)
    expanded_correction = models.BooleanField(default=False)
    allow_notifications = models.BooleanField(default=True)
