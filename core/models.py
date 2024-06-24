from django.db import models
from django.contrib.auth.models import User


class Theme(models.Model):
    theme_id = models.AutoField(primary_key=True, db_column='theme_id')
    title = models.CharField(max_length=255)
    year = models.IntegerField()


class Skill(models.Model):
    skill_id = models.AutoField(primary_key=True, db_column='skill_id')
    skill_type = models.CharField(max_length=1)
    skill_description = models.CharField(max_length=255)


class FeedbackStatus(models.TextChoices):
    CREATED = 'CREATED'
    QUEUED = 'QUEUED'
    PROCESSING = 'PROCESSING'
    FINISHED = 'FINISHED'
    FAILED = 'FAILED'


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True, db_column='feedback_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    theme = models.ForeignKey(Theme, on_delete=models.DO_NOTHING, db_column='theme_id')
    grade = models.IntegerField()
    quality = models.DecimalField(max_digits=5, decimal_places=2)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=FeedbackStatus.choices, default=FeedbackStatus.CREATED, max_length=50)
    retries = models.IntegerField(default=0)
    last_retry_datetime = models.DateTimeField()

    def queue(self):
        self.status = FeedbackStatus.QUEUED

    def process(self):
        self.status = FeedbackStatus.PROCESSING

    def finish(self):
        self.status = FeedbackStatus.FINISHED

    def fail(self):
        self.status = FeedbackStatus.FAILED

    @property
    def original_essay_text(self):
        return self.originalessaytext

    @property
    def refined_essay_text(self):
        return self.refinedessaytext


class SkillFeedback(models.Model):
    skill_feedback_id = models.AutoField(primary_key=True, db_column='skill_feedback_id')
    skill = models.ForeignKey(Skill, on_delete=models.DO_NOTHING, db_column='skill_id')
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, db_column='feedback_id')
    grade = models.IntegerField()
    text = models.TextField()


class OriginalEssayText(models.Model):
    feedback = models.OneToOneField(Feedback, on_delete=models.CASCADE, primary_key=True, db_column='feedback_id',
                                    related_name='originalessaytext')
    full_original_text = models.TextField()
    introduction = models.TextField()
    development = models.TextField()
    conclusion = models.TextField()


class RefinedEssayText(models.Model):
    feedback = models.OneToOneField(Feedback, on_delete=models.CASCADE, primary_key=True, db_column='feedback_id',
                                    related_name='refinedessaytext')
    introduction = models.TextField()
    development = models.TextField()
    conclusion = models.TextField()


class MotivationalText(models.Model):
    motivational_text_id = models.AutoField(primary_key=True, db_column='motivational_text_id')
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, db_column='theme_id')
    title = models.CharField(max_length=200)
    text = models.TextField()


class UserConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, db_column='user_id')
    generate_punctuation = models.BooleanField(default=False)
    expanded_correction = models.BooleanField(default=False)
    allow_notifications = models.BooleanField(default=False)
