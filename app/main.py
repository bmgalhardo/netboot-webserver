import uvicorn
import textwrap

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

from app.talos import Schematic
from app.utils import MACAddress

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

schematic = Schematic()

@app.get('/healthcheck')
def healthcheck() -> str:
    return "OK"

@app.get('/boot/{mac_addr}')
def dynamic_ipxe(mac_addr: str) -> Response:
    try:
        mac = MACAddress(mac_addr)
        ipxe_url = schematic.mac_to_factory_url(mac)
        script = f"""
            #!ipxe
            echo Booting {mac.as_colon()}
            chain {ipxe_url}
            """
    except ValueError:
        script = f"""
            #!ipxe
            echo Mac Address {mac_addr} not valid
            sleep 5
        """
    except KeyError:
        script = f"""
            #!ipxe
            echo No boot assets found
            sleep 5
        """
    return Response(content=textwrap.dedent(script).lstrip('\n'), media_type="text/plain")

if __name__ == '__main__':
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
