from django.utils.translation import ugettext_lazy as _
from corekit.utils import render


class InlineMixin(object):

    def admin_url(self, instance):
        opt = instance._meta
        url_name = f"admin:{opt.app_label}_{opt.model_name}_change"
        return render(
            '<a href="{% url u i.id %}">{{i}}</a>', 
            u=url_name, i=instance)
    
    admin_url.short_description =  _('Admin Url')