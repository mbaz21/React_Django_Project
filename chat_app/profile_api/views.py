from django.http.response import JsonResponse
from rest_framework import generics,status 
from rest_framework.views import APIView
from rest_framework.response import Response 
from account.models import Account
from .serializers import *
from django.http import Http404

class ProfileView(generics.RetrieveAPIView):

    """ views a user's profile by id specified in url """

    queryset = Account.objects.all()
    serializer_class = ProfileSerializer
    lookup_url_kwarg = 'pk'

class SendFriendRequestView(generics.ListCreateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer


class UpdateFriendRequestView(APIView):
    serializer_class = FriendRequestSerializer

    def get_object(self, pk):
        try:
            return FriendRequest.objects.get(pk=pk)
        except FriendRequest.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = self.serializer_class(obj)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = self.serializer_class(obj, data=request.data)
        if serializer.is_valid():
            declined = serializer.validated_data.get('declined',None)
            approved = serializer.validated_data.get('approved',None)
            if declined and approved:
                return Response({'error':'invalid input'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                instance = serializer.save()
            
            if instance.approved:
                friend = Friend.objects.filter(friend=instance.sent_by)

                if friend.exists():
                    return Response({'detail':'request already approved'}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    my_new_friend = Friend(account=instance.sent_to, friend=instance.sent_by, approved_request=instance)
                    his_new_friend = Friend(account=instance.sent_by, friend=instance.sent_to, approved_request=instance)
                    my_new_friend.save()
                    his_new_friend.save()

                    return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        request = self.get_object(pk)
        request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)