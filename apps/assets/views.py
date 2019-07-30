from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# Create your views here.
from . import models


class AssetListView(ListView):
    model = models.Asset
    template_name = "assets/assets_list.html"
    context_object_name = 'assets_list'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AssetListView,self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(AssetListView,self).get_context_data(*args, **kwargs)
        asset_types = models.Asset.asset_type_choice
        asset_status = models.Asset.asset_status
        server_types = models.Server.sub_asset_type_choice
        context.update({'asset_types':asset_types,'server_types':server_types,'asset_status_':asset_status})
        return context