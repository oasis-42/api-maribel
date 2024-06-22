from django.urls import path

from core.views import RefinedEssayTextView, OriginalEssayTextView, ThemeView, UserConfigView, TextExtractionView, \
    RegisterView, FeedbackView

urlpatterns = [
    path('feedbacks/refined-essay/<int:pk>', RefinedEssayTextView.as_view(), name='essay_corrected_text_retrieve'),
    path('feedbacks/original-essay/<int:pk>', OriginalEssayTextView.as_view(), name='essay_original_text_retrieve'),
    path('configs/<int:pk>', UserConfigView.as_view(), name='user_config_update_retrieve'),
    path('themes', ThemeView.as_view(), name='themes_list'),
    path('text-extraction', TextExtractionView.as_view(), name='text_extraction_process'),
    path('ocr/base64', TextExtractionView.as_view(), name='text_extraction_process_ocr'), # deprecated
    path('ocr/feedback', FeedbackView.as_view(), name='feedback_process_ocr'), # deprecated
    path('feedback', FeedbackView.as_view(), name='feedback_process'),
    path('register', RegisterView.as_view(), name='register'),
]
