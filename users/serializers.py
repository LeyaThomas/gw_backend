from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

# Assuming CustomUser is a custom user model
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()  # Use the custom user model
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Set the role to 'reader' if not provided in the request
        role = validated_data.get('role', 'reader')

        user = get_user_model()(  # Create the user using the custom user model
            username=validated_data['username'],
            email=validated_data['email'],
            role=role,  # Ensure role is properly passed and defaulted
        )
        user.set_password(validated_data['password'])  # Hash password before saving
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Fetch the user based on email
        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError('Invalid credentials')

        # Check the password
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid credentials')

        # If the user is found and password matches
        data['user'] = user
        return data
