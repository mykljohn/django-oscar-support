from django.contrib import admin
from django.apps import apps

admin.site.register(apps.get_model('oscar_support', 'TicketType'))
admin.site.register(apps.get_model('oscar_support', 'TicketStatus'))
admin.site.register(apps.get_model('oscar_support', 'Ticket'))
admin.site.register(apps.get_model('oscar_support', 'Priority'))
admin.site.register(apps.get_model('oscar_support', 'Message'))
admin.site.register(apps.get_model('oscar_support', 'RelatedOrder'))
admin.site.register(apps.get_model('oscar_support', 'RelatedOrderLine'))
admin.site.register(apps.get_model('oscar_support', 'RelatedProduct'))
admin.site.register(apps.get_model('oscar_support', 'Attachment'))
