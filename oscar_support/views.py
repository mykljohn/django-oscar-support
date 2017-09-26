from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
)

from oscar.core.loading import get_class
from oscar.core.loading import get_model
from oscar_support.forms.formsets import AttachmentFormSet

from . import utils
from .forms import TicketCreateForm
from .forms import TicketUpdateForm

Ticket = get_model('oscar_support', 'Ticket')
Message = get_model('oscar_support', 'Message')
TicketStatus = get_model('oscar_support', 'TicketStatus')
PageTitleMixin = get_class('customer.mixins', 'PageTitleMixin')


class TicketListView(PageTitleMixin, ListView):
    model = Ticket
    template_name = 'oscar_support/customer/ticket_list.html'
    context_object_name = 'ticket_list'
    active_tab = 'support'
    page_title = _('Your tickets')

    def get_queryset(self, queryset=None):
        # we only want so show top-level tickets for now
        return Ticket.objects.filter(
            requester=self.request.user,
            parent=None,
        )

    def get_context_data(self, **kwargs):
        ctx = super(TicketListView, self).get_context_data(**kwargs)
        resolved = utils.TicketStatusGenerator.get_resolved_status()
        ctx['open_ticket_list'] = self.get_queryset().exclude(status=resolved)
        ctx['resolved_ticket_list'] = self.get_queryset().filter(
            status=resolved
        )
        return ctx


class TicketCreateView(PageTitleMixin, CreateView):
    active_tab = 'support'
    attachment_formset = AttachmentFormSet
    context_object_name = 'ticket'
    form_class = TicketCreateForm
    model = Ticket
    page_title = _('Create a new ticket')
    template_name = 'oscar_support/customer/ticket_create.html'

    def __init__(self, *args, **kwargs):
        super(TicketCreateView, self).__init__(*args, **kwargs)
        self.formsets = {'attachment_formset': self.attachment_formset}

    def get_form_kwargs(self, **kwargs):
        kwargs = super(TicketCreateView, self).get_form_kwargs(**kwargs)
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(TicketCreateView, self).get_context_data(**kwargs)
        for ctx_name, formset_class in self.formsets.items():
            if ctx_name not in ctx:
                ctx[ctx_name] = formset_class(
                                              self.request.user,
                                              instance=self.object)
        return ctx

    def get_success_url(self):
        return reverse("support:customer-ticket-list")


class TicketUpdateView(PageTitleMixin, UpdateView):
    model = Ticket
    context_object_name = 'ticket'
    form_class = TicketUpdateForm
    template_name = 'oscar_support/customer/ticket_update.html'
    active_tab = 'support'

    def get_page_title(self):
        return _('Update ticket #{0}').format(self.object.number)

    def form_valid(self, form):
        message_text = form.cleaned_data.get('message_text')
        if not message_text:
            return self.form_invalid(form)
        Message.objects.create(
            ticket=self.object,
            text=message_text,
            user=self.request.user,
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        ctx = super(TicketUpdateView, self).get_context_data(**kwargs)
        ctx['message_list'] = Message.objects.filter(
            user=self.request.user,
            ticket=self.object,
        )
        return ctx

    def get_success_url(self):
        return reverse(
            "support:customer-ticket-update",
            kwargs={'pk': self.object.uuid}
        )
