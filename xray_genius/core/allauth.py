from allauth.account.forms import SignupForm as AccountSignupForm
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.forms import SignupForm as SocialAccountSignupForm
from composed_configuration._allauth_support.adapter import EmailAsUsernameAccountAdapter
from django import forms
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


class XrayGeniusTOSCheckboxWidget(forms.CheckboxInput):
    template_name = 'widgets/tos_checkbox.html'


class XrayGeniusAccountSignupForm(AccountSignupForm):
    accepted_tos = forms.BooleanField(
        required=True,
        widget=XrayGeniusTOSCheckboxWidget(),
    )

    @property
    def field_order(self) -> list[str]:
        fields: list[str] = list(self.fields.keys())
        fields.remove('accepted_tos')
        fields.append('accepted_tos')
        return fields


class XrayGeniusSocialAccountSignupForm(SocialAccountSignupForm):
    accepted_tos = forms.BooleanField(
        required=True,
        widget=XrayGeniusTOSCheckboxWidget(),
    )

    @property
    def field_order(self) -> list[str]:
        fields: list[str] = list(self.fields.keys())
        fields.remove('accepted_tos')
        fields.append('accepted_tos')
        return fields
