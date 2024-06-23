from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Theme, Skill, Feedback, SkillFeedback, OriginalEssayText, RefinedEssayText, MotivationalText, UserConfig


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user


class FeedbackDtoSerializer(serializers.Serializer):
    text = serializers.CharField()


class CapturedPictureSerializer(serializers.Serializer):
    base64 = serializers.CharField()


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ['theme', 'title', 'year']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['skill', 'skill_type', 'skill_description']


class FeedbackSerializer(serializers.ModelSerializer):
    theme_title = serializers.CharField(source='theme.title', read_only=True)
    feedback_id = serializers.IntegerField(source='feedback_id', read_only=True)
    user_id = serializers.IntegerField(source='user_id', read_only=True)

    class Meta:
        model = Feedback
        fields = ['feedback_id', 'user_id', 'theme_title', 'grade', 'quality', 'creation_date']


class SkillFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillFeedback
        fields = ['skill_feedback', 'skill', 'feedback', 'grade', 'text']


class OriginalEssayTextSerializer(serializers.ModelSerializer):
    feedback_id = serializers.IntegerField(source='feedback.id')

    class Meta:
        model = OriginalEssayText
        fields = ['feedback_id', 'introduction', 'development', 'conclusion']


class RefinedEssayTextSerializer(serializers.ModelSerializer):
    feedback_id = serializers.IntegerField(source='feedback')

    class Meta:
        model = RefinedEssayText
        fields = ['feedback_id', 'introduction', 'development', 'conclusion']


class MotivationalTextSerializer(serializers.ModelSerializer):
    motivational_text_id = serializers.IntegerField(source='motivational_text')
    theme_id = serializers.IntegerField(source='theme.theme')

    class Meta:
        model = MotivationalText
        fields = ['motivational_text_id', 'theme_id', 'title', 'text']


class UserConfigSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = UserConfig
        fields = ['user_id', 'generate_punctuation', 'expanded_correction', 'allow_notifications']

