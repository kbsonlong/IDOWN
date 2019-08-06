from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.


User = get_user_model()

class Asset(models.Model):
    """所有资产的共有数据表"""

    asset_type_choice = (
        ('server', '服务器'),
        ('networkdevice', '网络设备'),
        ('storagedevice', '存储设备'),
        ('securitydevice', '安全设备'),
        ('software', '软件资产'),
    )

    asset_status = (
        (0, '在线'),
        (1, '下线'),
        (2, '未知'),
        (3, '故障'),
        (4, '备用'),
        (5, '待初始化'),
    )

    type = models.CharField(choices=asset_type_choice, max_length=64, default='server', verbose_name='资产类型')
    name = models.CharField(max_length=64, unique=True, verbose_name='资产名称')  # 不可重复
    sn = models.CharField(max_length=128, unique=True, verbose_name='资产序列号')
    business_unit = models.ForeignKey('BusinessUnit', null=True, blank=True, verbose_name='所属业务线',
                                      on_delete=models.SET_NULL)

    status = models.SmallIntegerField(choices=asset_status, default=0, verbose_name='设备状态')

    manufacturer = models.ForeignKey('Manufacturer', null=True, blank=True, verbose_name='IDC服务商',
                                     on_delete=models.SET_NULL)
    manage_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='管理IP')
    admin = models.ForeignKey(User, null=True, blank=True, verbose_name='资产管理员', related_name='admin',
                              on_delete=models.SET_NULL)
    idc = models.ForeignKey('IDC', null=True, blank=True, verbose_name='所在机房', on_delete=models.SET_NULL)

    purchase_day = models.DateField(null=True, blank=True, verbose_name="购买日期")
    expire_day = models.DateField(null=True, blank=True, verbose_name="过保日期")
    price = models.FloatField(null=True, blank=True, verbose_name="价格")

    approved_by = models.ForeignKey(User, null=True, blank=True, verbose_name='批准人', related_name='approved_by',
                                    on_delete=models.SET_NULL)

    remark = models.TextField(null=True, blank=True, verbose_name='备注')
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='批准日期')
    m_time = models.DateTimeField(auto_now=True, verbose_name='更新日期')

    def __str__(self):
        return '<%s>  %s' % (self.get_type_display(), self.name)

    class Meta:
        verbose_name = '资产总表'
        verbose_name_plural = "资产总表"
        ordering = ['-c_time']


class Server(models.Model):
    """服务器设备"""

    sub_asset_type_choice = (
        (0, 'ECS'),
        (1, 'PC服务器'),
        (2, '小型机'),
    )

    created_by_choice = (
        ('auto', '自动添加'),
        ('manual', '手工录入'),
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)  # 非常关键的一对一关联！asset被删除的时候一并删除server
    i_ip = models.GenericIPAddressField(verbose_name="公网地址",  blank=True, null=True, default=None)
    local_ip = models.GenericIPAddressField(verbose_name="内网地址", blank=True, null=True, default=None)
    instance_id = models.CharField(verbose_name="ECS实例ID",max_length=100, blank=True, null=True, default=None)
    hostname = models.CharField(verbose_name="服务器主机名",max_length=150, blank=True, null=True, default=None)
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="服务器类型")
    created_by = models.CharField(choices=created_by_choice, max_length=32, default='auto', verbose_name="添加方式")
    hosted_on = models.ForeignKey('self', related_name='hosted_on_server',
                                  blank=True, null=True, verbose_name="宿主机", on_delete=models.CASCADE)  # 虚拟机专用字段
    model = models.CharField(max_length=128, null=True, blank=True, verbose_name='服务器型号')
    raid_type = models.CharField(max_length=512, blank=True, null=True, verbose_name='Raid类型')
    env = models.ForeignKey('Env', max_length=64, blank=True, null=True,on_delete=models.SET_NULL,verbose_name="所属环境")
    os_distribution = models.CharField('发行商', max_length=64, blank=True, null=True)
    os_release = models.CharField('操作系统版本', max_length=512, blank=True, null=True)
    cpu = models.CharField('CPU', max_length=64, blank=True, null=True)
    ram = models.CharField('内存', max_length=64, blank=True, null=True)

    def __str__(self):
        return '%s--%s--%s' % (self.hostname, self.get_sub_asset_type_display(), self.i_ip)

    class Meta:
        verbose_name = '服务器'
        verbose_name_plural = "服务器"


class Env(models.Model):
    name = models.CharField(verbose_name='环境名称',max_length=20,unique=True,help_text='dev',null=True,blank=True)
    name_cn = models.CharField(verbose_name='环境中文名称',max_length=20,help_text='开发环境',null=True,blank=True)
    class Meta:
        verbose_name = "环境名称"
        verbose_name_plural = "环境名称"
    def __str__(self):
        return self.name


class IDC(models.Model):
    """机房"""
    name = models.CharField(max_length=64, unique=True, verbose_name="机房名称")
    memo = models.CharField(max_length=128, blank=True, null=True, verbose_name='备注')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '机房'
        verbose_name_plural = "机房"


class Manufacturer(models.Model):
    """IDC服务商"""

    name = models.CharField('IDC名称', max_length=64, unique=True)
    telephone = models.CharField('支持电话', max_length=30, blank=True, null=True)
    memo = models.CharField('备注', max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'IDC服务商'
        verbose_name_plural = "IDC服务商"


class BusinessUnit(models.Model):
    """业务线"""

    parent_unit = models.ForeignKey('self', blank=True, null=True, related_name='parent_level',
                                    on_delete=models.SET_NULL)
    name = models.CharField('业务线', max_length=64, unique=True)
    memo = models.CharField('备注', max_length=64, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '业务线'
        verbose_name_plural = "业务线"


class App(models.Model):
    app_type_choice = (
        (0, 'api'),
        (1, 'base'),
        (2, 'db'),
        (3, 'dubbo'),
        (4, 'messages'),
        (5, 'search'),
        (6, 'web'),
    )
    active_choices = (
        (1, '在线'),
        (4, '禁用'),
        (9, '废弃'),
    )
    server = models.ManyToManyField('Server',verbose_name="部署主机")
    env = models.ForeignKey('Env',verbose_name="所属环境",on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=150,verbose_name="应用名称")
    name_cn = models.CharField(max_length=200,null=True,blank=True,verbose_name="应用中文名称")
    app_type = models.SmallIntegerField(choices=app_type_choice,  default=0, verbose_name='应用类型')
    domain = models.CharField(max_length=100,default='',verbose_name="域名")
    port  = models.IntegerField(default=0,verbose_name="应用端口")
    values  = models.CharField(max_length=500,default="'-Xms512m -Xmx512m'",verbose_name="启动参数")
    war_name  = models.CharField(max_length=200,default="app_name.jar",verbose_name="应用包名称")
    leader  = models.CharField(max_length=200,default="",verbose_name="应用负责人")
    remark = models.TextField(null=True, blank=True, verbose_name='备注')
    active  = models.SmallIntegerField(choices=active_choices,default=1,verbose_name="应用状态")
    app_init = models.CharField(default='n',max_length=10,verbose_name="应用是否初始化")
    create_user = models.CharField(default='',blank=True,null=True,max_length=50,verbose_name="创建人")
    create_time = models.DateField(auto_now_add=True,verbose_name="创建日期")
    update_user = models.CharField(default='',blank=True,null=True,max_length=10,verbose_name="更新人")
    update_time = models.DateTimeField(auto_now=True,verbose_name="更新时间")
    member = models.ManyToManyField(User,verbose_name="项目成员",help_text="一个应用对应多个成员")
    class Meta:
        verbose_name = "应用程序"
        verbose_name_plural = "应用程序"
        unique_together =('name','env')

    def __str__(self):
        return '{}'.format(self.name)



class SecurityDevice(models.Model):
    """安全设备"""

    sub_asset_type_choice = (
        (0, '防火墙'),
        (1, '入侵检测设备'),
        (2, '互联网网关'),
        (4, '运维审计系统'),
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="安全设备类型")
    model = models.CharField(max_length=128, default='未知型号', verbose_name='安全设备型号')

    def __str__(self):
        return self.asset.name + "--" + self.get_sub_asset_type_display() + str(self.model) + " id:%s" % self.id

    class Meta:
        verbose_name = '安全设备'
        verbose_name_plural = "安全设备"


class StorageDevice(models.Model):
    """存储设备"""

    sub_asset_type_choice = (
        (0, '磁盘阵列'),
        (1, '网络存储器'),
        (2, '磁带库'),
        (4, '磁带机'),
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="存储设备类型")
    model = models.CharField(max_length=128, default='未知型号', verbose_name='存储设备型号')

    def __str__(self):
        return self.asset.name + "--" + self.get_sub_asset_type_display() + str(self.model) + " id:%s" % self.id

    class Meta:
        verbose_name = '存储设备'
        verbose_name_plural = "存储设备"


class NetworkDevice(models.Model):
    """网络设备"""

    sub_asset_type_choice = (
        (0, '路由器'),
        (1, '交换机'),
        (2, '负载均衡'),
        (4, 'VPN设备'),
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="网络设备类型")

    vlan_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="VLanIP")
    intranet_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="内网IP")

    model = models.CharField(max_length=128, default='未知型号',  verbose_name="网络设备型号")
    firmware = models.CharField(max_length=128, blank=True, null=True, verbose_name="设备固件版本")
    port_num = models.SmallIntegerField(null=True, blank=True, verbose_name="端口个数")
    device_detail = models.TextField(null=True, blank=True, verbose_name="详细配置")

    def __str__(self):
        return '%s--%s--%s <sn:%s>' % (self.asset.name, self.get_sub_asset_type_display(), self.model, self.asset.sn)

    class Meta:
        verbose_name = '网络设备'
        verbose_name_plural = "网络设备"


class Software(models.Model):
    """
    只保存付费购买的软件
    """
    sub_asset_type_choice = (
        (0, '操作系统'),
        (1, '办公\开发软件'),
        (2, '基础服务'),
    )

    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="软件类型")
    license_num = models.IntegerField(default=1, verbose_name="授权数量")
    name = models.CharField(max_length=64,help_text='例如: RedHat release 7 (Final)',verbose_name="软件名称")
    version = models.CharField(max_length=64, help_text='1.8.1',
                               verbose_name='软件/系统版本')


    def __str__(self):
        return '%s-%s-%s' % (self.get_sub_asset_type_display(),self.name, self.version)

    class Meta:
        verbose_name = '软件/系统'
        verbose_name_plural = "软件/系统"
        unique_together = ('name', 'version',)


class Disk(models.Model):
    """硬盘设备"""

    disk_interface_type_choice = (
        ('SATA', 'SATA'),
        ('SAS', 'SAS'),
        ('SCSI', 'SCSI'),
        ('SSD', 'SSD'),
        ('unknown', 'unknown'),
    )

    asset = models.ForeignKey('Asset', on_delete=models.CASCADE)
    sn = models.CharField('硬盘SN号', max_length=128)
    instance_id = models.CharField('磁盘挂载实例', max_length=64, blank=True, null=True)
    model = models.CharField('磁盘型号', max_length=128, blank=True, null=True)
    size = models.FloatField('磁盘容量(GB)', blank=True, null=True)
    status = models.CharField('磁盘状态', max_length=16, choices=disk_interface_type_choice, default='unknown')

    def __str__(self):
        return '%s:  %s:  %sGB' % (self.asset.name, self.model,self.size)

    class Meta:
        verbose_name = '硬盘'
        verbose_name_plural = "硬盘"
        unique_together = ('asset', 'sn')


