from fastapi import APIRouter
from fastapi.responses import Response

from app.core.ipxe import IPXE

router = APIRouter()


@router.get("/boot")
def ipxe_talos(proxmox: bool) -> Response:
    ipxe = IPXE().add_boot(
        kernel_location="talos/proxmox/kernel-amd64",
        kernel_params=[
            "talos.platform=metal",
            "console=tty0",
            "init_on_alloc=1",
            "slab_nomerge",
            "pti=on",
            "consoleblank=0",
            "nvme_core.io_timeout=4294967295",
            "printk.devkmsg=on",
            "ima_template=ima-ng",
            "ima_appraise=fix",
            "ima_hash=sha512",
            "selinux=1",
        ],
        initrd_location="talos/proxmox/initramfs-amd64.xz",
    )

    return Response(content=ipxe.to_file(), media_type="text/plain")
