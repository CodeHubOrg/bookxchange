import pprint
from postman.views import ComposeMixin, DisplayMixin
from lending.forms import BookxReplyForm, BookxFullReplyForm
from postman.models import Message
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, TemplateView
from postman.utils import format_subject, format_body

login_required_m = method_decorator(login_required)
csrf_protect_m = method_decorator(csrf_protect)
never_cache_m = method_decorator(never_cache)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters('subject', 'body'))

pp = pprint.PrettyPrinter(indent=4)

class BookxDisplayMixin(DisplayMixin):
    form_class = BookxReplyForm
    template_name = 'lending/bookx_view.html'


class MessageView(BookxDisplayMixin, TemplateView):
    """Display one specific message."""

    def get(self, request, message_id, *args, **kwargs):
        self.filter = Q(pk=message_id)
        return super(MessageView, self).get(request, *args, **kwargs)

class ConversationView(BookxDisplayMixin, TemplateView):
    """Display a conversation."""

    def get(self, request, thread_id, *args, **kwargs):
        self.filter = Q(thread=thread_id)
        return super(ConversationView, self).get(request, *args, **kwargs)


class ReplyView(ComposeMixin, FormView):
    """
    Display a form to compose a reply.

    Optional attributes:
        ``form_class``: the form class to use
        ``formatters``: a 2-tuple of functions to prefill the
        subject and body fields
        ``autocomplete_channel``: a channel name
        ``template_name``: the name of the template to use
        + those of ComposeMixin

    """
    form_class = BookxFullReplyForm
    formatters = (format_subject, format_body)
    autocomplete_channel = None
    template_name = 'lending/bookx_reply.html'

    @sensitive_post_parameters_m
    @never_cache_m
    @csrf_protect_m
    @login_required_m
    def dispatch(self, request, message_id, *args, **kwargs):
        perms = Message.objects.perms(request.user)
        self.parent = get_object_or_404(Message, perms, pk=message_id)
        return super(ReplyView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        self.initial = self.parent.quote(*self.formatters)  # will also be partially used in get_form_kwargs()
        if self.request.method == 'GET':
            self.initial.update(self.request.GET.items())  # allow overwriting of the defaults by query string
        return self.initial

    def get_form_kwargs(self):
        kwargs = super(ReplyView, self).get_form_kwargs()
        kwargs['channel'] = self.autocomplete_channel
        if self.request.method == 'POST':
            if 'subject' not in kwargs['data']:  # case of the quick reply form
                post = kwargs['data'].copy()  # self.request.POST is immutable
                post['subject'] = self.initial['subject']
                kwargs['data'] = post
            kwargs['recipient'] = self.parent.sender or self.parent.email
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ReplyView, self).get_context_data(**kwargs)
        context['recipient'] = self.parent.obfuscated_sender
        return context
