import pprint
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext
from postman.models import get_user_name

from postman.forms import WriteForm
from postman.fields import CommaSeparatedUserField
from users.email_notifications import send_reply_notification

pp = pprint.PrettyPrinter(indent=4)


class BookxReplyForm(WriteForm):
    def __init__(self, *args, **kwargs):

        recipient = kwargs.pop('recipient', None)
        super(BookxReplyForm, self).__init__(*args, **kwargs)
        # pp.pprint(vars(*args))
        self.recipient = recipient

    def clean(self):
        """Check that the recipient is correctly initialized and no filter prohibits the exchange."""
        if not self.recipient:
            raise forms.ValidationError(ugettext("Undefined recipient."))

        exchange_filter = getattr(self, 'exchange_filter', None)
        if exchange_filter and isinstance(self.recipient, get_user_model()):
            try:
                reason = exchange_filter(self.instance.sender, self.recipient, None)
                if reason is not None:
                    raise forms.ValidationError(self.error_messages['filtered'].format(
                        users=self.error_messages[
                            'filtered_user_with_reason' if reason else 'filtered_user'
                        ].format(username=get_user_name(self.recipient), reason=reason)
                    ))
            except forms.ValidationError as e:
                raise forms.ValidationError(e.messages)
        return super(BookxReplyForm, self).clean()

    def save(self, *args, **kwargs):
        send_reply_notification(self.instance, self.recipient, self.site)
        return super(BookxReplyForm, self).save(self.recipient, *args, **kwargs)

allow_copies = not getattr(settings, 'POSTMAN_DISALLOW_COPIES_ON_REPLY', False)


class BookxFullReplyForm(BookxReplyForm):
    """The complete reply form."""
    if allow_copies:
        recipients = CommaSeparatedUserField(
            label=(("Additional recipients"), ("Additional recipient")), help_text='', required=False)

    class Meta(BookxReplyForm.Meta):
        fields = (['recipients'] if allow_copies else []) + ['subject', 'body']
