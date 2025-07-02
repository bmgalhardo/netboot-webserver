from pathlib import Path

import uvicorn
import textwrap

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

from app.utils import MACAddress
from app.settings import settings

app = FastAPI()
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get('/entrypoint')
def entrypoint() -> Response:
    script = f"""
        #!ipxe
        chain {settings.netboot_url}/boot/${{mac}}
        """
    return Response(content=textwrap.dedent(script).lstrip('\n'), media_type="text/plain")

@app.get('/boot/{mac_addr}')
def dynamic_ipxe(mac_addr: str) -> Response:
    mac = MACAddress(mac_addr)

    if mac.as_dash().startswith("02-00-00-00-01"):
        script = f"""
            #!ipxe
            echo Booting {mac.as_colon()} with Talos
            chain {settings.netboot_url}/boot/talos
            """
    else:
        script = f"""
            #!ipxe
            chain {settings.netboot_url}/static/alpine/alpine.ipxe
        """

    return Response(content=textwrap.dedent(script).lstrip('\n'), media_type="text/plain")

@app.get('/talos')
def dynamic_talos_ipxe() -> Response:
    # siderolink.api=https://omni.bgalhardo.local:8090?jointoken=eaiaoYVEiz0bPCAoqiNJrnSretcDCDEMYuelfAtHzRnC&grpc_tunnel=true talos.events.sink=[fdae:41e4:649b:9303::1]:8091 talos.logging.kernel=tcp://[fdae:41e4:649b:9303::1]:8092
    script = f"""
        #!ipxe
        
        set boot-url {settings.netboot_url}
        set kernel-args talos.platform=metal console=tty0 init_on_alloc=1 slab_nomerge pti=on consoleblank=0 nvme_core.io_timeout=4294967295 printk.devkmsg=on ima_template=ima-ng ima_appraise=fix ima_hash=sha512 selinux=1

        kernel ${{boot-url}}/static/talos/proxmox/kernel-amd64 ${{kernel-args}} talos.config=${{boot-url}}/static/talos/boot-assets.yml
        initrd ${{boot-url}}/static/talos/proxmox/initramfs-amd64.xz
        boot
    """
    return Response(content=textwrap.dedent(script).lstrip('\n'), media_type="text/plain")

if __name__ == '__main__':
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
