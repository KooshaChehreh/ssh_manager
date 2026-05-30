import paramiko


class SSHService:
    def __init__(self, server):
        self.server = server
        self.client = None

    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=self.server.host,
            port=self.server.port,
            username=self.server.ssh_user,
            password=self.server.ssh_password,
            timeout=10,
        )

    def disconnect(self):
        if self.client:
            self.client.close()

    def run_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode().strip(), stderr.read().decode().strip()

    def create_user(self, username, password, expire_date):
        try:
            self.connect()

            expire_part = ""
            if expire_date:
                expire_part = f"-e {expire_date.strftime('%Y-%m-%d')}"
            cmd = (
                f"sudo useradd -M {expire_part} -s /usr/sbin/nologin {username} "
                f"&& echo '{username}:{password}' | sudo chpasswd"
            )
            out, err = self.run_command(cmd)

            return True, out or err
        except Exception as e:
            return False, str(e)
        finally:
            self.disconnect()


    def delete_user(self, username):
        try:
            self.connect()
            cmd = f"userdel -r {username}"
            out, err = self.run_command(cmd)
            return True, out or err
        except Exception as e:
            return False, str(e)
        finally:
            self.disconnect()

    def get_traffic(self, username):
        """
        مصرف ترافیک بر اساس iptables
        باید قبلا rule اضافه شده باشد
        """
        try:
            self.connect()
            # ایجاد rule اگر وجود نداشت
            uid_cmd = f"id -u {username}"
            uid_out, _ = self.run_command(uid_cmd)
            if not uid_out:
                return 0

            uid = uid_out.strip()

            # خواندن بایت‌های ارسالی (OUTPUT)
            cmd = f"iptables -nvx -L OUTPUT | grep 'owner UID match {uid}' | awk '{{print $2}}'"
            out, _ = self.run_command(cmd)
            upload = int(out) if out.isdigit() else 0

            # خواندن بایت‌های دریافتی - بر اساس INPUT نمیشه دقیق گرفت
            # ساده‌ترین روش: فقط OUTPUT رو حساب کنیم
            return upload
        except Exception as e:
            return 0
        finally:
            self.disconnect()

    def setup_traffic_rules(self, username):
        """اضافه کردن rule iptables برای ردیابی ترافیک"""
        try:
            self.connect()
            uid_cmd = f"id -u {username}"
            uid_out, _ = self.run_command(uid_cmd)
            if not uid_out:
                return False

            uid = uid_out.strip()
            # اضافه کردن rule برای OUTPUT
            cmd = f"iptables -A OUTPUT -m owner --uid-owner {uid} -j ACCEPT"
            self.run_command(cmd)
            return True
        except Exception:
            return False
        finally:
            self.disconnect()
