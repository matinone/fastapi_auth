import pathlib

import yagmail
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import get_settings
from app.models import User

templates_path = pathlib.Path(__file__).parent / "templates"
settings = get_settings()


def send_password_recovery_email(user: User, url: str):
    send_template_email(
        template="password_recovery.html",
        to=user.email,
        subj=f"Password Recovery for user {user.email}",
        username=user.email,
        url=url,
        token_expire=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
    )


def send_template_email(template, to, subj, **kwargs):

    env = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template(template)
    html_email = template.render(**kwargs)
    send_email(to, subj, html_email)


# edit this function to send emails using transactional email services like Sendgrid
def send_email(to, subj, body):  # pragma: no cover
    yag = yagmail.SMTP(settings.EMAIL_SENDER, oauth2_file="google_oauth2_creds.json")
    yag.send(
        to=to,
        subject=subj,
        contents=body,
    )
