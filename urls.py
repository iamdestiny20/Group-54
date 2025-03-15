from django.urls import path
from recommender_project.views import fetch_courses, recommend_course
urlpatterns = [
    path('fetch-courses/', fetch_courses, name='fetch_courses'),
    path('recommend/', recommend_course, name='recommend_course'),
]