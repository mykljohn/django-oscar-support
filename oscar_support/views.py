from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    ListView,
    UpdateView,
    View
)
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from oscar.core.loading import get_class
from oscar.core.loading import get_model

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
    model = Ticket
    form_class = TicketCreateForm
    context_object_name = 'ticket'
    template_name = 'oscar_support/customer/ticket_create.html'
    active_tab = 'support'

    def get_form_kwargs(self, **kwargs):
        kwargs = super(TicketCreateView, self).get_form_kwargs(**kwargs)
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("support:customer-ticket-list")


class TicketUpdateView(PageTitleMixin, UpdateView):
    model = Ticket
    context_object_name = 'ticket'
    form_class = TicketUpdateForm
    template_name = 'oscar_support/customer/ticket_update.html'
    active_tab = 'support'

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
