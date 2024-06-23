from django.urls import path, include

from core.views import RefinedEssayTextView, OriginalEssayTextView, ThemeView, UserConfigView, TextExtractionView, \
    FeedbackView, password_reset_confirm, activate, MotivationalTextByThemeView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/feedbacks/refined-essay/<int:pk>', RefinedEssayTextView.as_view(), name='essay_corrected_text_retrieve'),
    path('api/feedbacks/original-essay/<int:pk>', OriginalEssayTextView.as_view(), name='essay_original_text_retrieve'),
    path('api/configs/<int:pk>', UserConfigView.as_view(), name='user_config_update_retrieve'),
    path('api/themes', ThemeView.as_view(), name='themes_list'),
    path('api/text-extraction', TextExtractionView.as_view(), name='text_extraction_process'),
    path('api/ocr/base64', TextExtractionView.as_view(), name='text_extraction_process_ocr'), # deprecated
    path('api/ocr/feedback', FeedbackView.as_view(), name='feedback_process_ocr'), # deprecated
    path('api/feedbacks', FeedbackView.as_view(), name='feedback_process'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('password/reset/confirm/<uid>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('activate/<uid>/<token>/', activate, name='activate'),
    path('motivational-texts/theme/<int:theme_id>/', MotivationalTextByThemeView.as_view(), name='motivational-texts-by-theme'),
]
