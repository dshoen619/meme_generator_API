from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .utils import authenticate_user
from rest_framework.exceptions import AuthenticationFailed
from .models import Meme, MemeTemplate, Rating

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    email = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate(self, attrs):
        # Ensure all required fields are provided
        if 'username' not in attrs:
            raise serializers.ValidationError({"username": "This field is required."})
        if 'email' not in attrs:
            raise serializers.ValidationError({"email": "This field is required."})
        if 'password' not in attrs:
            raise serializers.ValidationError({"password": "This field is required."})
        return attrs

    def create(self, validated_data):
        # Check if a user with the same username already exists
        if User.objects.filter(username=validated_data['username']).exists():
            raise serializers.ValidationError({"username": "A user with this username already exists."})

        # Check if a user with the same email already exists
        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})

        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        print(data)

        user = authenticate(**data)
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        
        token, created = Token.objects.get_or_create(user=user)
        return {'user':user,
                'token': token.key}


class UserLogoutSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

    def validate_username(self, value):
        # Check if the user exists
        try:
            user = User.objects.get(username=value)
            print('user:',user)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        return user

    def delete_token(self, user):
        # Attempt to delete the token for the specified user
        try:
            token = Token.objects.get(user=user)
            token.delete()
        except Token.DoesNotExist:
            raise serializers.ValidationError("Token not found for this user.")
        
class AuthenticateSerializer(serializers.Serializer):

    def validate(self, attrs):
        # Call the authenticate function with the request
        request = self.context.get('request')
        
        try:
            auth_response = authenticate_user(request)
            return auth_response  # You can return the message if needed
        except AuthenticationFailed as e:
            raise serializers.ValidationError(str(e))  # Raise a validation error

class MemeSerializer(serializers.ModelSerializer):
    top_text = serializers.CharField(required=False, allow_blank=True)
    bottom_text = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Meme
        fields = ['template', 'top_text', 'bottom_text']

    def create(self, validated_data):
        # Extract the template and get the corresponding MemeTemplate instance
        template = validated_data.pop('template')
        meme_template = MemeTemplate.objects.get(id=template.id)

        # Use default values if top_text or bottom_text is not provided
        top_text = validated_data.get('top_text', meme_template.default_top_text)
        bottom_text = validated_data.get('bottom_text', meme_template.default_bottom_text)

        # Create the Meme instance with the final values
        meme = Meme.objects.create(
            template=meme_template,
            top_text=top_text,
            bottom_text=bottom_text,
            **validated_data
        )
        return meme

class MemeTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemeTemplate
        fields = ['name', 'image_url', 'default_top_text', 'default_bottom_text']

class RecieveMemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meme
        fields = ['id','top_text','bottom_text','created_at','created_by_id','template_id']

class RateMemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['score']

    def create(self, validated_data):
        # Retrieve meme and user from context
        meme = self.context.get('meme')
        user = self.context.get('user')

        # Create and return the Rating instance
        return Rating.objects.create(meme=meme, user=user, **validated_data)

