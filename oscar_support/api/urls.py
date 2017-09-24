import django
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
    # url(r'^', include(router.urls, namespace='support-api')),
    url(r'^$', views.api_root, name='support-api'),
    url(r'^tickets/$', views.TicketList.as_view(), name='ticket-list'),
    url(r'^tickets/(?P<pk>[a-zA-Z0-9]+)/$', views.TicketDetail.as_view(), name='ticket-detail'),
    # url(r'^ticket/add-ticket/$', views.AddTicketView.as_view(), name='api-tickets-add-ticket'),
    # url(r'^ticket/add-message/$', views.AddMessageView.as_view(), name='api-tickets-add-message'),
    # url(r'^products/(?P<pk>[0-9]+)/price/$', views.ProductPrice.as_view(), name='product-price'),
    # url(r'^products/(?P<pk>[0-9]+)/availability/$', views.ProductAvailability.as_view(), name='product-availability'),
    # url(r'^products/(?P<pk>[0-9]+)/stockrecords/$', views.StockRecordList.as_view(), name='product-stockrecord-list'),
    # url(r'^messages/$', views.MessageList.as_view(), name='message-list'),
    # url(r'^messages/(?P<pk>[0-9]+)/$', views.MessageDetail.as_view(), name='message-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

if django.VERSION[:2] < (1, 8):
    from django.conf.urls import patterns

    urlpatterns = patterns('', *urlpatterns)
