from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (UserSignupSerializer, 
                          UserLoginSerializer, 
                          UserLogoutSerializer, 
                          AuthenticateSerializer,
                          MemeSerializer,
                          MemeTemplateSerializer,
                          RecieveMemeSerializer,
                          RateMemeSerializer
)

from .models import User, Meme, MemeTemplate, Rating
from rest_framework.pagination import PageNumberPagination
from django.db import IntegrityError
import random
from django.db.models import Avg

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
            serializer.delete_token(user)  
            
            return Response({"message": f"Successfully logged out user '{user.username}'."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MemeView(APIView):

    def post(self, request):
        # authenticate
        authenticate_serializer = AuthenticateSerializer(data=request.data, context={'request': request})
        if not authenticate_serializer.is_valid():
            return Response(authenticate_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        meme_serializer = MemeSerializer(data=request.data)

        # Validate and save the meme
        if meme_serializer.is_valid():
            user_id = request.headers.get('Id')
            user = User.objects.get(id=user_id)
            meme = meme_serializer.save(created_by=user)  # Set the creator
            return Response({'id': meme.id, 'message': 'Meme created successfully!'}, status=status.HTTP_201_CREATED)

        return Response(meme_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # authenticate
        authenticate_serializer = AuthenticateSerializer(data=request.data, context={'request': request})
        if not authenticate_serializer.is_valid():
            return Response(authenticate_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

       # Query all memes and paginate them
        memes = Meme.objects.all()

        # Use pagination
        paginator = PageNumberPagination()
        paginated_memes = paginator.paginate_queryset(memes, request)

        # Serialize the paginated memes
        memes_serializer = MemeSerializer(paginated_memes, many=True)

        # Return paginated response
        return paginator.get_paginated_response(memes_serializer.data)

class CreateMemeTemplateView(APIView):

    def post(self, request):
        # authenticate
        authenticate_serializer = AuthenticateSerializer(data=request.data, context={'request': request})
        if not authenticate_serializer.is_valid():
            return Response(authenticate_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # Create a serializer instance with the request data
        meme_template_serializer = MemeTemplateSerializer(data=request.data)

        # Validate and save the meme
        if meme_template_serializer.is_valid():
            meme_template = meme_template_serializer.save()  # Set the creator
            return Response({'id': meme_template.name, 'message': 'Meme template created successfully!'}, status=status.HTTP_201_CREATED)

        return Response(meme_template_serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

class RetrieveMemeView(APIView):

    def get(self,request, meme_id):

        # authenticate
        authenticate_serializer = AuthenticateSerializer(data=request.data, context={'request': request})
        if not authenticate_serializer.is_valid():
            return Response(authenticate_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            meme = Meme.objects.get(id=meme_id)
        except Meme.DoesNotExist:
            return Response({'error': 'Meme not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the meme instance
        meme_serializer = RecieveMemeSerializer(meme)

        # Return the serialized data
        return Response(meme_serializer.data, status=status.HTTP_200_OK)
    
class ReceiveAllTemplatesView(APIView):
     
     def get(self,request):

        # authenticate
        authenticate_serializer = AuthenticateSerializer(data=request.data, context={'request': request})
        if not authenticate_serializer.is_valid():
            return Response(authenticate_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Query all templates from MemeTemplate table
        templates = MemeTemplate.objects.all()
        print(templates)

        # Serialize the templates
        template_serializer = MemeTemplateSerializer(templates, many=True)

        # Return the serialized templates in the response
        return Response(template_serializer.data, status=status.HTTP_200_OK)
     
class RateMemeView(APIView):
    def post(self, request, meme_id):
        # Authenticate
        authenticate_serializer = AuthenticateSerializer(data=request.data, context={'request': request})
        if not authenticate_serializer.is_valid():
            return Response(authenticate_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get user
        user_id = request.headers.get('Id')
        user = User.objects.get(id=user_id)

        # Get meme
        try:
            meme = Meme.objects.get(id=meme_id)
        except Meme.DoesNotExist:
            return Response({'error': 'Meme not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has already rated the meme
        existing_rating = Rating.objects.filter(meme=meme, user=user).first()
        if existing_rating:
            # If the rating exists, update it
            existing_rating.score = request.data.get('score')
            existing_rating.save()
            return Response({'id': existing_rating.id, 'message': 'Rating updated successfully!'}, status=status.HTTP_201_CREATED)
        else:
            # Create a new rating
            rate_serializer = RateMemeSerializer(data=request.data, context={'meme': meme, 'user': user})
            if rate_serializer.is_valid():
                rating = rate_serializer.save()
                return Response({'id': rating.id, 'message': 'Rating created successfully!'}, status=status.HTTP_201_CREATED)
        
        return Response(rate_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RandomMemeView(APIView):
    
    def get(self,request):

        # authenticate
        authenticate_serializer = AuthenticateSerializer(data=request.data, context={'request': request})
        if not authenticate_serializer.is_valid():
            return Response(authenticate_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
         # Get all memes
        memes = Meme.objects.all()

        # Randomly select one meme
        random_meme = random.choice(memes) if memes else None
        
        if random_meme:
            meme_serializer = MemeSerializer(random_meme)
            return Response(meme_serializer.data, status=status.HTTP_200_OK)
        
        return Response({'message': 'No memes found.'}, status=status.HTTP_404_NOT_FOUND)
    

class TopRatedMemesView(APIView):
    def get(self, request):
        # Authenticate
        authenticate_serializer = AuthenticateSerializer(data=request.data, context={'request': request})
        if not authenticate_serializer.is_valid():
            return Response(authenticate_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

          # Query to get the top 10 rated memes that have at least one rating
        top_memes = (
            Meme.objects
            .annotate(avg_rating=Avg('rating__score'))  # Calculate the average rating
            .filter(avg_rating__isnull=False)  # Only include memes with ratings
            .order_by('-avg_rating')[:10]  # Get the top 10 rated memes
        )

        # Create a response list with memes and their average ratings
        response_data = []
        for meme in top_memes:
            response_data.append({
                'id': meme.id,
                'template': meme.template.id,  # Assuming you want to include the template id
                'top_text': meme.top_text,
                'bottom_text': meme.bottom_text,
                'avg_rating': meme.avg_rating,  # Include the average rating
            })

        return Response(response_data, status=status.HTTP_200_OK)