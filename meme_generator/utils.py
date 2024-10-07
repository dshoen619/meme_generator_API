from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

def authenticate_user(request):
    """Validate the token against the user_id."""
    if request:
        print('headers in authenticate',request.headers)
        token = request.headers.get('Token')
        user_id = request.headers.get('Id')

        if not token or not user_id:
            raise AuthenticationFailed('Token or user_id missing')

        try:
            # Check if the token matches for the given user_id
            auth_token = Token.objects.get(key=token)

            if str(auth_token.user.id) == user_id:
                return auth_token.user  # Return the user for further processing
            else:
                raise AuthenticationFailed('Token does not match the user_id')

        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

    raise AuthenticationFailed('Error: Request headers missing')
