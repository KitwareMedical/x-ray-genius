from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from composed_configuration._allauth_support.adapter import EmailAsUsernameAccountAdapter
from django.conf import settings


class XrayGeniusAccountAdapter(EmailAsUsernameAccountAdapter):
    def new_user(self, request):
        user = super().new_user(request)
        if settings.REQUIRE_APPROVAL_FOR_NEW_USERS:
            user.is_active = False
        return user


class XrayGeniusSocialAccountAdapter(DefaultSocialAccountAdapter):
    def new_user(self, request, sociallogin):
        user = super().new_user(request, sociallogin)
        if settings.REQUIRE_APPROVAL_FOR_NEW_USERS:
            user.is_active = False
        return user
