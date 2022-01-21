from os import name
from django.urls import path
from .views import *

app_name = 'aws_app'


urlpatterns = [
    path('redirect/',RedirectView.as_view(),name="redirect"),
    path('',Mentoring.as_view() , name='index'),
    path('captured_frames/',SaveFrame.as_view() , name='captured_frames'),
    path('test_image/',test_image , name='test_image'),
    path('save_frame/',SaveFrame.as_view() , name='save_frame'),
    path('mentoring/',ExamMentoring.as_view() , name='mentoring'),

    path("userimages/<int:id>/",ImageView.as_view(),name="get-image"),
    path("redflagged/",FlaggedImagesView.as_view(),name='flagged-images'),
    ]