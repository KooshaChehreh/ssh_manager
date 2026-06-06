from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Client
from servers.models import Server
from servers.services import SSHService
from django.db import transaction


import logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Client)
def sync_user_on_servers(sender, instance, created, **kwargs):

    def do_sync():
        active_servers = Server.objects.filter(is_active=True)

        if created:
            if not instance.is_active:
                return
            for server in active_servers:
                try:
                    ssh = SSHService(server)
                    success, msg = ssh.create_user(
                        instance.username,
                        instance.password,
                        instance.expire_date,
                    )
                    if success:
                        ssh.setup_traffic_rules(instance.username)
                        instance.servers.add(server)
                    else:
                        logger.error("create_user failed on %s: %s", server.name, msg)
                except Exception as e:
                    logger.exception("Failed to create user on %s: %s", server.name, e)
        else:
            for server in active_servers:
                try:
                    ssh = SSHService(server)
                    ssh.update_user(
                        instance.username,
                        instance.password,
                        instance.expire_date,
                    )
                except Exception as e:
                    logger.exception("Failed to update user on %s: %s", server.name, e)

    transaction.on_commit(do_sync)
@receiver(pre_delete, sender=Client)
def delete_user_from_servers(sender, instance, **kwargs):
    for server in instance.servers.all():
        ssh = SSHService(server)
        ssh.delete_user(instance.username)