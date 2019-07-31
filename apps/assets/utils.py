# -*- coding: utf-8 -*-
# @Time    : 2019-07-31 14:49
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : utils.py
# @Software: PyCharm

from assets.models import Asset


def get_model_fields(model_name):
    """
    主要获取Model中设置的verbose_name
    :param model_name: Model的名称，即django的model对象，区分大小写
    :return: 返回值包括字段名以及其verbose_name,两者组成字典
    :rtype: dict
    """
    fileds = model_name._meta.fields
    field_dic = {}
    for i in fileds:
        field_dic[i.name] = i.verbose_name
    return field_dic


class ExportExcel:
    def __init__(self, filename, excel_obj, asset_obj, sheet_name):
        self.filename = filename
        self.excel_obj = excel_obj
        self.asset_obj = asset_obj
        self.sheet = sheet_name

    def gen_headers(self):
        headers = []
        fields = get_model_fields(Asset)
        for k, v in fields.items():
            if k == 'id' or k == 'asset_create_time' or k == 'asset_update_time':
                continue
            else:
                headers.append(v)
        if self.asset_obj.type == 'server':
            headers.extend(['服务器类型', '用户名称', '用户密码', 'SSH端口', '宿主机'])

        elif self.asset_obj.type == 'network':
            headers.append('网络设备类型')
        elif self.asset_obj.type == 'office':
            headers.append('办公设备类型')
        elif self.asset_obj.type == 'security':
            headers.append('安全设备类型')
        elif self.asset_obj.type == 'storage':
            headers.append('存储设备类型')
        elif self.asset_obj.type == 'software':
            headers.append('软件类型')

        # 写入表头
        i = 0
        for header in headers:
            self.sheet.write(0, i, header)
            i = i + 1

    def gen_body(self, row):
        self.sheet.write(row, 0, self.asset_obj.type)
        self.sheet.write(row, 1, self.asset_obj.sn)
        self.sheet.write(row, 2, self.asset_obj.asset_model)
        self.sheet.write(row, 3,
                         self.asset_obj.asset_provider.asset_provider_name if self.asset_obj.asset_provider else None)
        self.sheet.write(row, 4, self.asset_obj.get_asset_status_display())
        self.sheet.write(row, 5, self.asset_obj.asset_management_ip)
        self.sheet.write(row, 6, self.asset_obj.asset_admin.username)
        self.sheet.write(row, 7, self.asset_obj.idc.name if self.asset_obj.asset_idc else None)
        self.sheet.write(row, 8, self.asset_obj.asset_cabinet.cabinet_name if self.asset_obj.asset_cabinet else None)
        self.sheet.write(row, 9, str(self.asset_obj.asset_purchase_day))
        self.sheet.write(row, 10, str(self.asset_obj.asset_expire_day))
        self.sheet.write(row, 11, self.asset_obj.asset_price)
        self.sheet.write(row, 12, self.asset_obj.asset_memo)
        if self.asset_obj.type == 'server':
            self.sheet.write(row, 13, self.asset_obj.server.get_server_type_display())
            self.sheet.write(row, 14, self.asset_obj.server.username)
            self.sheet.write(row, 15, self.asset_obj.server.password)
            self.sheet.write(row, 16, self.asset_obj.server.port)
            self.sheet.write(row, 17,
                             self.asset_obj.server.hosted_on.assets.asset_management_ip if self.asset_obj.serverassets.hosted_on else None)
        elif self.asset_obj.type == 'network':
            self.sheet.write(row, 13, self.asset_obj.networkassets.get_network_type_display())
        elif self.asset_obj.type == 'office':
            self.sheet.write(row, 13, self.asset_obj.officeassets.get_network_type_display())
        elif self.asset_obj.type == 'security':
            self.sheet.write(row, 13, self.asset_obj.securityassets.get_security_type_display())
        elif self.asset_obj.type == 'storage':
            self.sheet.write(row, 13, self.asset_obj.storageassets.get_storage_type_display())
        elif self.asset_obj.type == 'software':
            self.sheet.write(row, 13, self.asset_obj.softwareassets.get_software_type_display())

    def save_excel(self):
        self.excel_obj.save(self.filename)

    def download_excel(self, chunk_size=512):
        with open(self.filename, 'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
