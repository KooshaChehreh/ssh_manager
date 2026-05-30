import shlex
import paramiko
from django.core.management.base import BaseCommand
from clients.models import Client
from servers.models import Server


class Command(BaseCommand):
    help = "Set shell to nologin for selected users on all active servers"


    def handle(self, *args, **options):
        users = Client.objects.all()
        servers = Server.objects.filter(is_active=True)

        if not users.exists() or not servers.exists():
            self.stdout.write("کاربر یا سروری یافت نشد.")
            return

        for server in servers:
            self.stdout.write(f"Connecting to {server.name} ({server.host})...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                ssh.connect(
                    hostname=server.host,
                    port=server.port,
                    username=server.ssh_user,
                    password=server.ssh_password,
                    timeout=10,
                )
                self.stdout.write(f"Connected successfully to {server.host}")

                for user in users:
                    username = user.username
                    cmd = f"sudo usermod -s /usr/sbin/nologin {shlex.quote(username)}"
                    _, _, stderr = ssh.exec_command(cmd)
                    error = stderr.read().decode().strip()

                    if error:
                        self.stdout.write(self.style.ERROR(
                            f"  [!] Error for user {username}: {error}"))
                    else:
                        self.stdout.write(self.style.SUCCESS(
                            f"  [+] Shell updated to nologin for {username}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Failed on {server.host}: {e}"))
            finally:
                ssh.close()
                self.stdout.write(f"Disconnected from {server.host}\n")
