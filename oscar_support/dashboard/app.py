from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from shortuuid import get_alphabet

from oscar.core.application import Application
from oscar.views.decorators import staff_member_required

from . import views


class SupportDashboardApplication(Application):
    name = 'support-dashboard'

    ticket_list_view = views.TicketListView
    ticket_create_view = views.TicketCreateView
    ticket_update_view = views.TicketUpdateView

    def get_urls(self):
        urls = [
            url(r'^$', staff_member_required(self.ticket_list_view.as_view()), name='ticket-list'),
            url(r'^ticket/create/$', staff_member_required(self.ticket_create_view.as_view()),
                name='ticket-create'),
            url(
                r'^ticket/update/(?P<pk>[{0}]+)/$'.format(get_alphabet()),
                staff_member_required(self.ticket_update_view.as_view()),
                name='ticket-update'
            ),
        ]
        return self.post_process_urls(urls)


application = SupportDashboardApplication()
