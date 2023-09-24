from django.urls import path
from .views import (
    UserRegistrationVS,
    UserSearchVS,
    FriendRequestVS,
    FriendRequestActionVS,
    FriendRequestListVS,
)

urlpatterns = [
    path("register/", UserRegistrationVS.as_view(), name="registration"),
    path("search/", UserSearchVS.as_view(), name="search"),
    path("friend_request/", FriendRequestListVS.as_view(), name="friend_request"),
    path(
        "friend_request/<int:receiver_id>/",
        FriendRequestVS.as_view(),
        name="friend_request",
    ),
    path(
        "friend_request_action/<int:sender_id>/",
        FriendRequestActionVS.as_view(),
        name="friend_request",
    ),
]
