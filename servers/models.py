from django.db import models


class Server(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام سرور")
    host = models.GenericIPAddressField(verbose_name="آدرس IP")
    port = models.PositiveIntegerField(default=22, verbose_name="پورت SSH")
    ssh_user = models.CharField(max_length=50, default='root', verbose_name="یوزر SSH")
    ssh_password = models.CharField(max_length=200, verbose_name="پسورد SSH")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    host_key = models.CharField(max_length=256, verbose_name="کلید هاست")

    class Meta:
        verbose_name = "سرور"
        verbose_name_plural = "سرورها"

    def __str__(self):
        return f"{self.name} ({self.host})"
