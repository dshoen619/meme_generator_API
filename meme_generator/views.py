from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSignupSerializer, UserLoginSerializer, UserLogoutSerializer

class UserSignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"id": user.id, "username": user.username}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            print('data',data)
            return Response({
                "message": f"Welcome {data['user'].username}",
                'id':data['user'].id,
                'token':data['token']
                }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):

    def post(self, request):
        serializer = UserLogoutSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['username']  # Retrieve the validated user
            serializer.delete_token(user)  # Call the method to delete the token
            
            return Response({"message": f"Successfully logged out user '{user.username}'."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)