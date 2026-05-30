from django.core.management.base import BaseCommand
from clients.models import Client
from servers.models import Server
from servers.services import SSHService


class Command(BaseCommand):
    help = "Apply expire_date to existing linux users on all active servers"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        dry = opts["dry_run"]
        clients = Client.objects.exclude(username="").exclude(expire_date=None)

        for server in Server.objects.filter(is_active=True):
            ssh = SSHService(server)
            if not dry:
                ssh.connect()

            for c in clients:
                date = c.expire_date.strftime("%Y-%m-%d")
                cmd = f"sudo usermod -e {date} {c.username}"

                if dry:
                    self.stdout.write(f"[{server.host}] {cmd}")
                    continue

                out, err = ssh.run_command(cmd)
                msg = f"{c.username}@{server.host} -> {date}"
                if err:
                    self.stdout.write(self.style.ERROR(f"{msg} | {err}"))
                else:
                    self.stdout.write(self.style.SUCCESS(msg))

            if not dry:
                ssh.disconnect()
