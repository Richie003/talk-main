from rest_framework_simplejwt.tokens import RefreshToken


class CustomRefreshToken(RefreshToken):
    def payload(self):
        payload = super().payload()
        user = self.user
        data = {
            'user_id': user.id,
            'email': user.email,
            'user_role': eval(user.user_role)[0],
            'email_verified': user.email_verified,
            'jti': self.access_token.payload['jti'],
            'exp': self.access_token.payload['exp'],
            'iat': self.access_token.payload['iat'],
        }
        payload.update(data)
        return payload