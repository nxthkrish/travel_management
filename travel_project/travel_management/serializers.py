from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import CustomUser, TravelRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        token, _ = Token.objects.get_or_create(user=user)
        return user, token.key  # Return user and generated token

class TravelRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelRequest
        fields = '__all__'
        
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'role', 'status']
