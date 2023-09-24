from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .serializers import RegisterSerializer, UserSerializer
from .response import prepare_error_response, prepare_success_response
from rest_framework.pagination import PageNumberPagination
from .models import User
from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import FriendRequest, Friends
from .serializers import FriendRequestSerializer
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit


class UserRegistrationVS(APIView):
    permission_classes = []

    def post(self, request):
        register_serializer = RegisterSerializer(data=request.data)
        if register_serializer.is_valid():
            register_serializer.save()
            return Response(prepare_success_response(), status.HTTP_200_OK)

        return Response(
            prepare_error_response(register_serializer.errors),
            status.HTTP_400_BAD_REQUEST,
        )


class UserSearchVS(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        search_keyword = self.request.query_params.get("keyword")
        if search_keyword:
            return User.objects.filter(
                Q(first_name__icontains=search_keyword)
                | Q(last_name__icontains=search_keyword)
                | Q(email__iexact=search_keyword)
            )
        return User.objects.all()


@method_decorator(
    ratelimit(key="user", rate="3/m", method="POST", block=True), name="create"
)
class FriendRequestVS(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer

    def create(self, request, *args, **kwargs):
        receiver_id = self.kwargs.get("receiver_id")

        sender = request.user
        receiver = get_object_or_404(User, pk=receiver_id)

        connection_exists_1 = Friends.objects.filter(
            user1=sender, user2=receiver
        ).exists()
        connection_exists_2 = Friends.objects.filter(
            user1=receiver, user2=sender
        ).exists()
        if connection_exists_1 or connection_exists_2:
            return Response(
                prepare_error_response("You are already connected"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_request = FriendRequest.objects.filter(
            sender=sender, receiver=receiver
        ).exists()
        if existing_request:
            return Response(
                prepare_error_response("A friend request already exists."),
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            data={"sender": sender.id, "receiver": receiver.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=sender, receiver=receiver)

        return Response(
            prepare_success_response(serializer.data), status=status.HTTP_201_CREATED
        )


class FriendRequestActionVS(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer

    def update(self, request, *args, **kwargs):
        sender_id = self.kwargs.get("sender_id")
        action = self.request.query_params.get("action")

        receiver = request.user
        sender = get_object_or_404(User, pk=sender_id)

        try:
            existing_request = FriendRequest.objects.get(
                sender=sender, receiver=receiver, status=FriendRequest.PENDING
            )
        except:
            return Response(
                prepare_error_response("Invalid Request, No FriendRequest exists"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action.upper() == "ACCEPTED":
            existing_request.status = FriendRequest.ACCEPTED
            existing_request.save()
            Friends.objects.create(user1=sender, user2=receiver)
        elif action.upper() == "REJECTED":
            existing_request.status = FriendRequest.REJECTED
            existing_request.save()
            Friends.objects.create(user1=sender, user2=receiver)
        else:
            return Response(
                prepare_error_response("Invalid Action"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(prepare_success_response(), status=status.HTTP_201_CREATED)


class FriendRequestListVS(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        receiver = self.request.user
        return FriendRequest.objects.filter(receiver=receiver)


class FriendListVS(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        user_list = Friends.objects.filter(Q(user1=user) | Q(user2=user)).values_list(
            "id"
        )
        return User.objects.filter(id__in=user_list)
