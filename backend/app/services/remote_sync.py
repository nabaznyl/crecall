"""Remote synchronization via SSH/SCP/SFTP.

Provides push/pull operations for exporting/importing data bundles to a
remote host. Uses system `scp` if available; optional Paramiko fallback.
"""

import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.portable import export_full, import_full

try:
    import paramiko  # type: ignore

    PARAMIKO_AVAILABLE = True
except Exception:
    PARAMIKO_AVAILABLE = False


class RemoteSync:
    @staticmethod
    async def push(
        db: AsyncSession,
        host: str,
        user: Optional[str] = None,
        path: str = "/tmp/crecall_bundle.json",
        encryption_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        bundle = await export_full(db, encryption_key=encryption_key)
        tmpdir = tempfile.mkdtemp(prefix="crecall_sync_")
        bundle_file = os.path.join(tmpdir, "bundle.json")
        with open(bundle_file, "w") as f:
            f.write(bundle["payload"] if bundle.get("encrypted") else bundle["payload"])

        scp_target = f"{user+'@' if user else ''}{host}:{path}"
        method = "scp"
        if shutil.which("scp"):
            try:
                subprocess.check_call(["scp", bundle_file, scp_target])
                status = "ok"
            except subprocess.CalledProcessError as e:
                status = f"scp_failed:{e}"
        elif PARAMIKO_AVAILABLE:
            method = "paramiko"
            try:
                transport = paramiko.Transport((host, 22))
                transport.connect()
                sftp = paramiko.SFTPClient.from_transport(transport)
                if sftp is not None:
                    sftp.put(bundle_file, path)
                    sftp.close()
                transport.close()
                status = "ok"
            except Exception as e:
                status = f"paramiko_failed:{e}"
        else:
            status = "no_method_available"

        os.remove(bundle_file)
        os.rmdir(tmpdir)
        return {
            "status": status,
            "method": method,
            "encrypted": bundle.get("encrypted", False),
            "target": scp_target,
        }

    @staticmethod
    async def pull(
        db: AsyncSession,
        host: str,
        user: Optional[str] = None,
        path: str = "/tmp/crecall_bundle.json",
        encryption_key: Optional[str] = None,
        encrypted: bool = False,
    ) -> Dict[str, Any]:
        tmpdir = tempfile.mkdtemp(prefix="crecall_sync_")
        local_file = os.path.join(tmpdir, "bundle_in.json")
        scp_source = f"{user+'@' if user else ''}{host}:{path}"
        method = "scp"
        if shutil.which("scp"):
            try:
                subprocess.check_call(["scp", scp_source, local_file])
                status = "ok"
            except subprocess.CalledProcessError as e:
                status = f"scp_failed:{e}"
        elif PARAMIKO_AVAILABLE:
            method = "paramiko"
            try:
                transport = paramiko.Transport((host, 22))
                transport.connect()
                sftp = paramiko.SFTPClient.from_transport(transport)
                if sftp is not None:
                    sftp.get(path, local_file)
                    sftp.close()
                transport.close()
                status = "ok"
            except Exception as e:
                status = f"paramiko_failed:{e}"
        else:
            status = "no_method_available"

        if status == "ok":
            with open(local_file, "r") as f:
                payload = f.read()
            result = await import_full(
                db, payload=payload, encrypted=encrypted, encryption_key=encryption_key
            )
        else:
            result = {}

        try:
            if os.path.exists(local_file):
                os.remove(local_file)
            os.rmdir(tmpdir)
        except Exception:
            pass

        return {
            "status": status,
            "method": method,
            "import_result": result,
        }
