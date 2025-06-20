from pathlib import Path

import uvicorn
import textwrap

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

from app.utils import MACAddress

app = FastAPI()
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get('/boot/{mac_addr}')
def dynamic_ipxe(mac_addr: str) -> Response:
    mac = MACAddress(mac_addr)

    if mac.as_dash().startswith("02-00-00-00-01"):
        script = f"""
            #!ipxe
            echo Booting {mac.as_colon()} with Talos
            chain http://netboot.bgalhardo.local/static/talos/proxmox/talos.ipxe
            """
    else:
        script = f"""
            #!ipxe
            chain http://netboot.bgalhardo.local/static/alpine/alpine.ipxe
        """

    return Response(content=textwrap.dedent(script).lstrip('\n'), media_type="text/plain")

if __name__ == '__main__':
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
