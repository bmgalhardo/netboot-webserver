from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, Response

from app.alpine.utils import AlpineAssets
from app.core.ipxe import IPXE
from app.core.settings import settings

router = APIRouter()


@router.get("/boot")
def ipxe_alpine(proxmox: bool) -> Response:
    latest = AlpineAssets.list_versions()[0]

    if proxmox:
        kernel = "vmlinuz-virt"
        initrd = "initramfs-virt"
    else:
        kernel = "vmlinuz-lts"
        initrd = "initramfs-lts"

    ipxe = IPXE().add_boot(
        kernel_location=f"alpine/x86_64/{latest}/boot/{kernel}",
        kernel_params=[
            "console=tty0",
            "modules=loop,squashfs",
            "quiet",
            "nomodeset",
        ],
        initrd_location=f"alpine/x86_64/{latest}/boot/{initrd}",
    )

    return Response(content=ipxe.to_file(), media_type="text/plain")


@router.post("/bootstrap")
def create_assets() -> JSONResponse:
    versions = AlpineAssets.list_versions()[:2]  # latest 2 versions
    assets = [AlpineAssets(version=v, arch=arch) for v in versions for arch in settings.alpine_arch_list]

    for asset in assets:
        asset.download(settings.static_dir / "alpine" / asset.arch / asset.version)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Assets created successfully"})
