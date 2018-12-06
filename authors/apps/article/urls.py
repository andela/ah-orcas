from django.urls import path
from rest_framework_swagger.views import get_swagger_view
from .views import (
    ArticleCreateAPIView,
    ArticleListAPIView,
    ArticleDeleteAPIView,
    ArticleDetailAPIView,
    ArticleUpdateAPIView,
    Rate,
    ArticleRate,
    CommentsListCreateView,
    CommentsUpdateDeleteAPIView,
    ArticleTags, CommentHistoryAPIView)
from .likes_dislike_views import (
    Like,
    Dislike,
    FavoriteAPIView
)

schema_view = get_swagger_view(title="Article Comments")

urlpatterns = [
    path(
        'article/',
        ArticleListAPIView.as_view(),
        name='list'),
    path(
        'article/create',
        ArticleCreateAPIView.as_view(),
        name='create'),
    path(
        'article/delete/<slug>/',
        ArticleDeleteAPIView.as_view(),
        name='delete'),
    path(
        'article/detail/<slug>/',
        ArticleDetailAPIView.as_view(),
        name='detail'),
    path(
        'article/update/<slug>/',
        ArticleUpdateAPIView.as_view(),
        name='update'),
    path(
        'article/<str:slug>/rate/',
        Rate.as_view(),
        name="rate"),
    path(
        'article/rate/<str:pk>/',
        ArticleRate.as_view(),
        name="view_rate"),
    path(
        "article/like/<str:slug>/",
        Like.as_view(),
        name='like_article'),
    path(
        "article/dislike/<str:slug>/",
        Dislike.as_view(),
        name='dislike_article'),
    path('articles/<slug:slug>/comments',
         CommentsListCreateView.as_view(),
         name='comment_on_an_article'),
    path('articles/<slug:slug>/comments/<int:comment_id>',
         CommentsUpdateDeleteAPIView.as_view(),
         name='delete_comment'),

    path('articles/<slug>/favorite/',
         FavoriteAPIView.as_view(),
         name="favorite"),
    path(
        "article/tag/<str:slug>",
        ArticleTags.as_view(),
        name='tag_article'),

    path('articles/<slug:slug>/history/<int:id>',
         CommentHistoryAPIView.as_view(),
         name='comment_history'),

]
