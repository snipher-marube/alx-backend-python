from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions

class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that handles UUID
    """
    def get_user(self, validated_token):
        try:
            user_id = validated_token.get(user_id)
            if user_id:
                return self.user_model.objects.get(user_id=user_id)
        except self.user_model.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found', coder='user_not_found')
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid Token', code='invalid_code')
        return None