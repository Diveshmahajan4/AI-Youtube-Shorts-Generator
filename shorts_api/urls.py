from django.urls import path
from .views import ShortsGeneratorView, VideoProcessingStatusView, UserVideosView

urlpatterns = [
    path('shorts/', ShortsGeneratorView.as_view(), name='generate-shorts'),
    path('shorts/status/<int:processing_id>/', VideoProcessingStatusView.as_view(), name='processing-status'),
    path('shorts/user/<str:username>/', UserVideosView.as_view(), name='user-videos'),
] 