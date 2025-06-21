from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# from core.views import RefinedEssayTextView, OriginalEssayTextView, ThemeView, UserConfigView, TextExtractionView, \
#     FeedbackView, password_reset_confirm, activate, MotivationalTextByThemeView
from core.views.authentication import RegisterView as UserRegisterView
from core.views.authentication import activate, password_reset_confirm
from core.views.content import MotivationalTextByThemeView as MotivationalTextView
from core.views.content import ThemeView as ThemeListView
from core.views.essay import FeedbackView as FeedbackProcessingView
from core.views.essay import TextExtractionView as TextExtractionProcessingView
from core.views.history import OriginalEssayTextView as OriginalEssayView
from core.views.history import RefinedEssayTextView as RefinedEssayView
from core.views.user_config import UserConfigView as UserConfigDetailView

urlpatterns = [
    path(
        "api/feedbacks/refined-essay/<int:pk>",
        RefinedEssayView.as_view(),
        name="essay_corrected_text_retrieve",
    ),
    path(
        "api/feedbacks/original-essay/<int:pk>",
        OriginalEssayView.as_view(),
        name="essay_original_text_retrieve",
    ),
    path(
        "api/configs/<int:pk>",
        UserConfigDetailView.as_view(),
        name="user_config_update_retrieve",
    ),
    path("api/themes", ThemeListView.as_view(), name="themes_list"),
    path(
        "api/text-extraction",
        TextExtractionProcessingView.as_view(),
        name="text_extraction_process",
    ),
    path(
        "api/ocr/base64",
        TextExtractionProcessingView.as_view(),
        name="text_extraction_process_ocr",
    ),  # deprecated
    path(
        "api/ocr/feedback",
        FeedbackProcessingView.as_view(),
        name="feedback_process_ocr",
    ),  # deprecated
    path("api/feedbacks", FeedbackProcessingView.as_view(), name="feedback_process"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
    path(
        "api/auth/register/", UserRegisterView.as_view(), name="register"
    ),  # Adicionado endpoint de registro
    path(
        "password/reset/confirm/<uid>/<token>/",
        password_reset_confirm,
        name="password_reset_confirm",
    ),
    path("activate/<uid>/<token>/", activate, name="activate"),
    path(
        "api/motivational-texts/theme/<int:theme_id>/",
        MotivationalTextView.as_view(),
        name="motivational-texts-by-theme",
    ),
]

# urlpatterns = [
#     path('api/feedbacks/refined-essay/<int:pk>', RefinedEssayTextView.as_view(), name='essay_corrected_text_retrieve'),
#     path('api/feedbacks/original-essay/<int:pk>', OriginalEssayTextView.as_view(), name='essay_original_text_retrieve'),
#     path('api/configs/<int:pk>', UserConfigView.as_view(), name='user_config_update_retrieve'),
#     path('api/themes', ThemeView.as_view(), name='themes_list'),
#     path('api/text-extraction', TextExtractionView.as_view(), name='text_extraction_process'),
#     path('api/ocr/base64', TextExtractionView.as_view(), name='text_extraction_process_ocr'), # deprecated
#     path('api/ocr/feedback', FeedbackView.as_view(), name='feedback_process_ocr'), # deprecated
#     path('api/feedbacks', FeedbackView.as_view(), name='feedback_process'),
#     path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
#     path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
#     path('api/auth/', include('djoser.urls')),
#     path('api/auth/', include('djoser.urls.jwt')),
#     path('password/reset/confirm/<uid>/<token>/', password_reset_confirm, name='password_reset_confirm'),
#     path('activate/<uid>/<token>/', activate, name='activate'),
#     path('api/motivational-texts/theme/<int:theme_id>/', MotivationalTextByThemeView.as_view(), name='motivational-texts-by-theme'),
# ]
