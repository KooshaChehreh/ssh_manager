import uuid
from django.db import models
from django.utils import timezone
from servers.models import Server


class Client(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام")
    username = models.CharField(max_length=50, unique=True, verbose_name="نام کاربری")
    password = models.CharField(max_length=200, verbose_name="پسورد")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=True, verbose_name="توکن")
    servers = models.ManyToManyField(Server, blank=True, verbose_name="سرورها")
    traffic_limit = models.BigIntegerField(default=0, verbose_name="حد ترافیک (بایت)",
                                           help_text="0 = نامحدود")
    traffic_used = models.BigIntegerField(default=0, verbose_name="ترافیک مصرفی (بایت)")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    expire_date = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ انقضا")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "کلاینت"
        verbose_name_plural = "کلاینت‌ها"

    def __str__(self):
        return f"{self.name} ({self.username})"

    @property
    def is_expired(self):
        if self.expire_date and timezone.now() > self.expire_date:
            return True
        if self.traffic_limit > 0 and self.traffic_used >= self.traffic_limit:
            return True
        return False

    @property
    def traffic_used_mb(self):
        return round(self.traffic_used / (1024 * 1024), 2)

    @property
    def traffic_limit_mb(self):
        if self.traffic_limit == 0:
            return "نامحدود"
        return round(self.traffic_limit / (1024 * 1024), 2)
