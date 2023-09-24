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


class FriendRequestVS(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer

    def create(self, request, *args, **kwargs):
        receiver_id = self.kwargs.get("receiver_id")

        sender = request.user
        receiver = get_object_or_404(User, pk=receiver_id)

        connection_exists_1 = Friends.objects.filter(
            user_1=sender, user2=receiver
        ).exists()
        connection_exists_2 = Friends.objects.filter(
            user_1=receiver, user2=sender
        ).exists()
        if connection_exists_1 or connection_exists_2:
            return Response(
                {"detail": "You are already connected"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_request = FriendRequest.objects.filter(
            sender=sender, receiver=receiver
        ).exists()
        if existing_request:
            return Response(
                {"detail": "A friend request already exists between these users."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            data={"sender": sender.id, "receiver": receiver.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=sender, receiver=receiver)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FriendRequestActionVS(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer

    def update(self, request, *args, **kwargs):
        sender_id = self.kwargs.get("sender_id")
        action = self.request.query_params.get("action")

        receiver = request.user
        sender = get_object_or_404(User, pk=sender_id)
        existing_request = FriendRequest.objects.get(
            sender=sender, receiver=receiver, status=FriendRequest.PENDING
        )

        if action.upper() == "ACCEPTED":
            existing_request.status = FriendRequest.ACCEPTED
            existing_request.save()
            Friends.objects.create(user_1=sender, user_2=receiver)
        elif action.upper() == "REJECTED":
            existing_request.status = FriendRequest.REJECTED
            existing_request.save()
            Friends.objects.create(user1=sender, user2=receiver)
        else:
            return Response(
                {"detail": "Invalid Actoon."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_201_CREATED)


class FriendRequestListVS(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        receiver = self.request.user
        return FriendRequest.objects.filter(receiver=receiver)
