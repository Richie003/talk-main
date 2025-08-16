from rest_framework_simplejwt.tokens import RefreshToken


class CustomRefreshToken(RefreshToken):
    def payload(self):
        payload = super().payload()
        user = self.user
        data = {
            'user_id': user.id,
            'email': user.email,
            'user_role': eval(user.user_role)[0],
        }
        
        payload.update(data)
        return payload
