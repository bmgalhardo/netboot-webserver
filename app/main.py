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
    try:
        mac = MACAddress(mac_addr)

        if mac.normalized[:6] == "020000":
            base_schematic = "376567988ad370138ad8b2698212367b8edcb69b5fd68c80be1f2ec7d603b4ba"
            talos_version = "1.10.1"
            ipxe_chain = f"https://pxe.factory.talos.dev/pxe/{base_schematic}/{talos_version}/metal-amd64"

            script = f"""
                #!ipxe
                echo Booting {mac.as_colon()}
                chain {ipxe_chain}
                """
        else:
            script = f"""
                #!ipxe
                echo No boot assers
                sleep 5
            """
    except ValueError:
        script = f"""
            #!ipxe
            echo Mac Address {mac_addr} not valid
            sleep 5
        """
    return Response(content=textwrap.dedent(script).lstrip('\n'), media_type="text/plain")

if __name__ == '__main__':
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
