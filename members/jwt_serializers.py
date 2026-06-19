from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # 🔥 Inject role into token
        token['role'] = user.profile.role
        token['username'] = user.username

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # 🔥 Add role to response body (important for React)
        data['role'] = self.user.profile.role
        data['username'] = self.user.username

        return data
