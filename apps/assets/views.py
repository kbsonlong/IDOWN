import json
import xlwt
import logging
from django.shortcuts import render
from django.views.generic import ListView,DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.http import FileResponse
# Create your views here.
from . import models
from .utils.tools import ExportExcel

@method_decorator(login_required,name="dispatch")
class AssetListView(ListView):
    model = models.Asset
    template_name = "assets/assets_list.html"
    context_object_name = 'assets_list'


    def get_context_data(self, *args, **kwargs):
        context = super(AssetListView,self).get_context_data(*args, **kwargs)
        asset_types = models.Asset.asset_type_choice
        asset_status = models.Asset.asset_status
        server_types = models.Server.sub_asset_type_choice
        context.update({'asset_types':asset_types,'server_types':server_types,'asset_status_':asset_status})
        return context


@method_decorator(login_required,name="dispatch")
class AssetDetailView(DetailView):
    model = models.Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"



@permission_required('assets.add_assets', raise_exception=True)
def export_assets(request):
    if request.method == 'POST':
        pks = request.POST.get('pks')
        server_row = network_row = office_row = security_row = storage_row = software_row = 1
        excel = None
        filename = '资产列表.csv'
        try:
            file = xlwt.Workbook(encoding='utf-8', style_compression=0)

            # 生成sheet
            server_sheet = file.add_sheet('server', cell_overwrite_ok=True)
            network_sheet = file.add_sheet('network', cell_overwrite_ok=True)
            office_sheet = file.add_sheet('office', cell_overwrite_ok=True)
            security_sheet = file.add_sheet('security', cell_overwrite_ok=True)
            storage_sheet = file.add_sheet('storage', cell_overwrite_ok=True)
            software_sheet = file.add_sheet('software', cell_overwrite_ok=True)

            # 导出数据
            for pk in json.loads(pks):
                asset = models.Asset.objects.get(id=int(pk))

                if asset.type == 'server':
                    excel = ExportExcel(filename, excel_obj=file, asset_obj=asset, sheet_name=server_sheet)
                    excel.gen_body(server_row)
                    server_row = server_row + 1
                elif asset.type == 'network':
                    excel = ExportExcel(filename, excel_obj=file, asset_obj=asset, sheet_name=network_sheet)
                    excel.gen_body(network_row)
                    network_row = network_row + 1
                elif asset.type == 'office':
                    excel = ExportExcel(filename, excel_obj=file, asset_obj=asset, sheet_name=office_sheet)
                    excel.gen_body(office_row)
                    office_row = office_row + 1
                elif asset.type == 'security':
                    excel = ExportExcel(filename, excel_obj=file, asset_obj=asset, sheet_name=security_sheet)
                    excel.gen_body(security_row)
                    security_row = security_row + 1
                elif asset.type == 'storage':
                    excel = ExportExcel(filename, excel_obj=file, asset_obj=asset, sheet_name=storage_sheet)
                    excel.gen_body(storage_row)
                    storage_row = storage_row + 1
                elif asset.type == 'software':
                    excel = ExportExcel(filename, excel_obj=file, asset_obj=asset, sheet_name=software_sheet)
                    excel.gen_body(software_row)
                    software_row = software_row + 1
                excel.gen_headers()
            excel.save_excel()
            response = FileResponse(excel.download_excel())
            response['Content-Type'] = 'application/octet-stream'
            response['charset'] = 'utf-8'
            response['Content-Disposition'] = 'attachment;filename="{filename}"'.format(filename=filename)
            return response
        except Exception as e:
            logging.getLogger().error('导出失败！{}'.format(e))
