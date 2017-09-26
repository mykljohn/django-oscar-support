from django import forms
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_model

from .. import utils

Attachment = get_model('oscar_support', 'Attachment')
Order = get_model('order', 'Order')
RelatedOrder = get_model("oscar_support", "RelatedOrder")
RelatedOrderLine = get_model("oscar_support", "RelatedOrderLine")
RelatedProduct = get_model("oscar_support", "RelatedProduct")
TicketStatus = get_model("oscar_support", "TicketStatus")


class AttachmentForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AttachmentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Attachment
        fields = ['file']


class RelatedOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RelatedOrderForm, self).__init__(*args, **kwargs)

    class Meta:
        model = RelatedOrder
        fields = ['order']


class RelatedOrderLineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RelatedOrderLineForm, self).__init__(*args, **kwargs)

    class Meta:
        model = RelatedOrderLine
        fields = ['line']


class RelatedProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RelatedProductForm, self).__init__(*args, **kwargs)

    class Meta:
        model = RelatedProduct
        fields = ['product']


class TicketUpdateForm(forms.ModelForm):
    message_text = forms.CharField(label=_("Message"), widget=forms.Textarea())

    class Meta:
        model = get_model("oscar_support", "Ticket")
        fields = ['message_text']


class TicketCreateForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(TicketCreateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(TicketCreateForm, self).save(commit=False)

        instance.status = utils.TicketStatusGenerator.get_initial_status()
        instance.requester = self.user

        if commit:
            instance.save()
        return instance

    class Meta:
        model = get_model("oscar_support", "Ticket")
        fields = ['type', 'subject', 'body']
