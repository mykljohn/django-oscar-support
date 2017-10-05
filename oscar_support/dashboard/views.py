from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from oscar.core.loading import get_model
from oscar_support.forms.formsets import (
    AttachmentFormSet,
    RelatedOrderFormSet,
    RelatedOrderLineFormSet,
    RelatedProductFormSet
)

from . import forms
from .. import utils

Ticket = get_model('oscar_support', 'Ticket')
Message = get_model('oscar_support', 'Message')
TicketStatus = get_model('oscar_support', 'TicketStatus')


class TicketListMixin(object):
    ticket_list = None

    def get_ticket_list(self, queryset=None):
        if self.ticket_list:
            return self.ticket_list

        if queryset is None:
            queryset = self.model.objects.all()

        self.ticket_list = queryset.filter(
            # A user can see tickets that are assigned to them
            # or one of the groups they belong to
            Q(assignee=self.request.user) |
            Q(assigned_group__in=self.request.user.groups.all()) |
            # they can also see tickets that have no assigned
            # group AND user
            Q(assignee=None, assigned_group=None)
        )
        return self.ticket_list


class TicketListView(TicketListMixin, generic.ListView):
    model = Ticket
    context_object_name = 'ticket_list'
    template_name = 'oscar_support/dashboard/ticket_detail.html'

    def get_queryset(self, queryset=None):
        return self.get_ticket_list()


class UserFormInlineMixin(object):
    def get_extra_form_kwargs(self):
        kwargs = super(UserFormInlineMixin, self).get_extra_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TicketCreateView(generic.CreateView):
    model = Ticket
    template_name = 'oscar_support/dashboard/ticket_create.html'
    default_status = None
    form_class = forms.TicketCreateForm

    def get_default_status(self):
        if not self.default_status:
            self.default_status = utils.TicketStatusGenerator.get_initial_status()  # noqa
        return self.default_status

    def get_form_kwargs(self):
        kwargs = super(TicketCreateView, self).get_form_kwargs()
        kwargs['initial'].update({'status': self.get_default_status()})
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(TicketCreateView, self).get_context_data(**kwargs)
        status = self.get_default_status()
        ctx['default_status'] = status
        ctx['status_list'] = TicketStatus.objects.exclude(name=status.name)
        ctx['requester_create_form'] = forms.RequesterCreateForm()
        ctx['title'] = _('New ticket')
        return ctx

    def get_success_url(self, **kwargs):
        return reverse("support-dashboard:ticket-list")


class TicketUpdateView(TicketListMixin, generic.UpdateView):
    model = Ticket
    default_message_model = Message
    context_object_name = 'selected_ticket'
    form_class = forms.TicketUpdateForm
    attachment_formset = AttachmentFormSet
    related_order_formset = RelatedOrderFormSet
    related_line_formset = RelatedOrderLineFormSet
    related_product_formset = RelatedProductFormSet
    template_name = 'oscar_support/dashboard/ticket_detail.html'

    def __init__(self, *args, **kwargs):
        super(TicketUpdateView, self).__init__(*args, **kwargs)
        self.formsets = {
            'attachment_formset': self.attachment_formset,
            'related_order_formset': RelatedOrderFormSet,
            'related_line_formset': RelatedOrderLineFormSet,
            'related_product_formset': RelatedProductFormSet,
        }

    def get_context_data(self, **kwargs):
        ctx = super(TicketUpdateView, self).get_context_data(**kwargs)
        ticket_name = self.object
        ctx['ticket_list'] = self.get_ticket_list()
        ctx['title'] = _('Update {name}').format(name=ticket_name)
        for ctx_name, formset_class in self.formsets.items():
            if ctx_name not in ctx:
                ctx[ctx_name] = formset_class(
                    # self.request.user,
                    self.object.requester,
                    instance=self.object
                )
        return ctx

    def process_all_forms(self, form):

        if form.is_valid():
            self.object = form.save()

        formsets = {}
        for ctx_name, formset_class in self.formsets.items():
            formsets[ctx_name] = formset_class(
                # self.request.user,
                self.object.requester,
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )

        is_valid = form.is_valid() and all(
            [formset.is_valid() for formset in formsets.values()]
        )

        cross_form_validation_result = self.clean(form, formsets)
        if is_valid and cross_form_validation_result:
            return self.forms_valid(form, formsets)
        else:
            return self.forms_invalid(form, formsets)

    form_valid = form_invalid = process_all_forms

    def clean(self, form, formsets):

        return True

    def forms_valid(self, form, formsets):
        ticket = form.save()
        message_type = form.cleaned_data.get('message_type', Message.PUBLIC)
        message_text = form.cleaned_data.get('message_text')
        Message.objects.create(
            user=self.request.user,
            type=message_type,
            text=message_text,
            ticket=ticket
        )

        # Save formsets
        for formset in formsets.values():
            formset.save()

        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, form, formsets):

        messages.error(
            self.request,
            _("Your submitted data was not valid - please "
              "correct the errors below")
        )
        ctx = self.get_context_data(form=form, **formsets)
        return self.render_to_response(ctx)

    def get_success_url(self):
        return reverse("support-dashboard:ticket-list")
