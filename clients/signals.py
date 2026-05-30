from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Client
from servers.models import Server
from servers.services import SSHService


@receiver(post_save, sender=Client)
def create_user_on_servers(sender, instance, created, **kwargs):
    """وقتی کلاینت جدید ساخته میشه، روی همه سرورهای فعال یوزر بساز"""
    if created and instance.is_active:
        active_servers = Server.objects.filter(is_active=True)
        for server in active_servers:
            ssh = SSHService(server)
            success, msg = ssh.create_user(instance.username, instance.password, instance.expire_date)
            if success:
                ssh.setup_traffic_rules(instance.username)
                instance.servers.add(server)
