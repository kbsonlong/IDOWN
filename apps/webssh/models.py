from django.db import models
from cryptography.fernet import Fernet
from django.contrib.auth import get_user_model

# Create your models here.


User = get_user_model()

class SshUser(models.Model):
    """
    WebSSH登录信息
    """
    username = models.OneToOneField(User, verbose_name='用户', on_delete=models.CASCADE)
    password = models.CharField(max_length=200,verbose_name="密码",help_text="存放登录密码或者秘钥密码")
    ssh_key = models.TextField(verbose_name="秘钥信息",null=True,blank=True,editable=False)
    is_key = models.BooleanField(default=True, verbose_name="是否使用秘钥登录", help_text="默认以秘钥登录")

    class Meta:
        verbose_name = "WebSSH登录信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class FortRecord(models.Model):
    """
    操作记录表
    """
    record_modes = (
        ('ssh', 'ssh'),
        ('guacamole', 'guacamole')
    )

    login_user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)
    fort = models.CharField(max_length=32, verbose_name='登录主机及用户')
    remote_ip = models.GenericIPAddressField(verbose_name='远程地址')
    start_time = models.CharField(max_length=64, verbose_name='开始时间')
    login_status_time = models.CharField(max_length=16, verbose_name='登录时长')
    record_file = models.CharField(max_length=256, verbose_name='操作记录')
    record_mode = models.CharField(max_length=10, choices=record_modes, verbose_name='登录协议', default='ssh')

    class Meta:
        db_table = 'ops_fort_record'
        verbose_name = '操作记录表'
        verbose_name_plural = '操作记录表'