from django.contrib import admin
from django.contrib.auth.models import User
import djclick as click

from xray_genius.core.admin import UserAdmin


@click.command()
def dump_users_to_csv() -> None:
    """Dump all users to a CSV file."""
    users = User.objects.all()
    response = UserAdmin.export_users_to_csv(UserAdmin(User, admin.site), None, users)
    click.echo(response.getvalue().decode())
