from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

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