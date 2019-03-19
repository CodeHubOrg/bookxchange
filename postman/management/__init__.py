from __future__ import unicode_literals

from importlib import import_module
import sys

from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _

name = getattr(settings, 'POSTMAN_NOTIFIER_APP', 'notification')
if name and name in settings.INSTALLED_APPS:
    name = name + '.models'
    notification = import_module(name)
    create = notification.NoticeType.create

    def create_notice_types(*args, **kwargs):
        create("postman_rejection", _("Message Rejected"), _("Your message has been rejected"))
        create("postman_message", _("Message Received"), _("You have received a message"))
        create("postman_reply", _("Reply Received"), _("You have received a reply"))

    signals.post_migrate.connect(create_notice_types, sender=notification)
