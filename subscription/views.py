import json
import base64
from django.http import HttpResponse
from servers.models import Server
import json
import base64

from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from django.utils import timezone

from clients.models import Client

def subscription_view(request, token):
    try:
        client = get_object_or_404(Client, token=token, is_active=True)

        # if client.expire_date and client.expire_date < timezone.now():
        #     raise Http404("expired")

        # servers = client.servers.filter(is_active=True)
        servers = Server.objects.filter(is_active=True)

        outbounds = []
        for s in servers:
            outbounds.append({
                "type": "ssh",
                "tag": s.name,
                "server": s.host,
                "server_port": s.port,
                "user": client.username,        
                "password": client.password,  
                "host_key": [s.host_key],
                "host_key_algorithms": ["ssh-ed25519"],
                "client_version": "SSH-2.0-OpenSSH_8.9",
            })

        config = {"outbounds": outbounds}
        body = json.dumps(config, ensure_ascii=False, indent=2)

        response = HttpResponse(body, content_type="application/json; charset=utf-8")

        title_b64 = base64.b64encode(client.name.encode("utf-8")).decode("ascii")
        response["profile-title"] = "base64:" + title_b64
        response["profile-update-interval"] = "24"
    except Exception as e:
        print(e)

    # subscription-userinfo داینامیک
    # total = client.traffic_limit
    # used = client.traffic_used
    # expire_ts = int(client.expire_date.timestamp()) if client.expire_date else 0
    # response["subscription-userinfo"] = (
    #     f"upload=0; download={used}; total={total}; expire={expire_ts}"
    # )

    return response
