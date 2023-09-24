from users.models.base import BaseModel
from users.models.users import User
from django.db import models


class FriendRequest(BaseModel):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_requests"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_requests"
    )

    PENDING = 1
    ACCEPTED = 2
    REJECTED = 3

    status = models.IntegerField(default=PENDING)


class Friends(BaseModel):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friends_1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friends_2")
