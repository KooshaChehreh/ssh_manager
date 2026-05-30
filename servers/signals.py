from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Server
from .services import SSHService


@receiver(post_save, sender=Server)
def create_existing_users_on_new_server(sender, instance, created, **kwargs):
    """وقتی سرور جدید اضافه میشه، یوزرهای موجود رو روش بساز"""
    if created and instance.is_active:
        from clients.models import Client
        clients = Client.objects.filter(is_active=True, servers=None) | \
                  Client.objects.filter(is_active=True)

        # فقط کلاینت‌هایی که این سرور رو دارن
        # چون سرور تازه ساخته شده، باید همه کلاینت‌های فعال رو بسازیم
        all_active_clients = Client.objects.filter(is_active=True)
        ssh = SSHService(instance)
        for client in all_active_clients:
            ssh.create_user(client.username, client.password)
            ssh.setup_traffic_rules(client.username)
            client.servers.add(instance)
