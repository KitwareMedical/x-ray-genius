from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from composed_configuration._allauth_support.adapter import EmailAsUsernameAccountAdapter


class XrayGeniusAccountAdapter(EmailAsUsernameAccountAdapter):
    def new_user(self, request):
        user = super().new_user(request)
        # Disable all users on creation. Manual user approval is required.
        user.is_active = False
        return user


class XrayGeniusSocialAccountAdapter(DefaultSocialAccountAdapter):
    def new_user(self, request, sociallogin):
        user = super().new_user(request, sociallogin)
        # Disable all users on creation. Manual user approval is required.
        user.is_active = False
        return user
