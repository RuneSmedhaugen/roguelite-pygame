"""Small Windows helper that replaces the game after its process exits."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path


def show_message(message, title, flags):
    user32 = ctypes.windll.user32
    user32.MessageBoxW.argtypes = (ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint)
    user32.MessageBoxW.restype = ctypes.c_int
    user32.MessageBoxW(None, message, title, flags)


def wait_for_process(pid):
    if os.name != "nt":
        return
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = (ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32)
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
    kernel.WaitForSingleObject.restype = ctypes.c_uint32
    kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
    kernel.CloseHandle.restype = ctypes.c_int
    synchronize = 0x00100000
    handle = kernel.OpenProcess(synchronize, False, pid)
    if handle:
        try:
            kernel.WaitForSingleObject(handle, 0xFFFFFFFF)
        finally:
            kernel.CloseHandle(handle)


def download_archive(url, destination):
    request = urllib.request.Request(url, headers={"User-Agent": "Small-Punch-Puppies-Updater"})
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output, length=1024 * 1024)


def verify_sha256(path, expected):
    if not expected:
        return
    digest = hashlib.sha256()
    with path.open("rb") as archive:
        for chunk in iter(lambda: archive.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest().lower() != expected.lower():
        raise ValueError("The downloaded update failed its SHA-256 check.")


def install_update(install_dir, archive_path, launch_name):
    install_dir = install_dir.resolve()
    if not install_dir.is_dir():
        raise FileNotFoundError(f"Game folder not found: {install_dir}")

    staging_dir = install_dir.parent / f".{install_dir.name}.update-staging"
    backup_dir = install_dir.parent / f".{install_dir.name}.update-backup"
    shutil.rmtree(staging_dir, ignore_errors=True)
    shutil.rmtree(backup_dir, ignore_errors=True)

    with zipfile.ZipFile(archive_path) as archive:
        root = staging_dir.resolve()
        for member in archive.infolist():
            member_path = (staging_dir / member.filename).resolve()
            if member_path != root and root not in member_path.parents:
                raise ValueError("The update archive contains an unsafe file path.")
        archive.extractall(staging_dir)

    new_executable = staging_dir / launch_name
    if not new_executable.is_file():
        raise FileNotFoundError(f"The update archive is missing {launch_name}.")

    os.replace(install_dir, backup_dir)
    try:
        os.replace(staging_dir, install_dir)
    except Exception:
        os.replace(backup_dir, install_dir)
        raise

    shutil.rmtree(backup_dir, ignore_errors=True)
    return install_dir / launch_name


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--install-dir", type=Path, required=True)
    parser.add_argument("--download-url", required=True)
    parser.add_argument("--launch", required=True)
    parser.add_argument("--sha256", default="")
    args = parser.parse_args()

    log_path = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "SmallPunchPuppies" / "update-error.log"
    try:
        if os.name == "nt":
            show_message(
                "The game is updating and will restart when the download is complete.",
                "Small Punch Puppies update",
                0x40,
            )
        wait_for_process(args.pid)
        local_data = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "SmallPunchPuppies" / "Updater"
        local_data.mkdir(parents=True, exist_ok=True)
        archive_path = local_data / "update.zip"
        download_archive(args.download_url, archive_path)
        verify_sha256(archive_path, args.sha256)
        executable = install_update(args.install_dir, archive_path, args.launch)
        archive_path.unlink(missing_ok=True)
        subprocess.Popen([str(executable)], cwd=str(executable.parent), close_fds=True)
    except Exception as error:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(f"Update failed: {error}\n", encoding="utf-8")
        message = f"The update could not be installed. You can try again by reopening the game.\n\nDetails were saved to:\n{log_path}"
        if os.name == "nt":
            show_message(message, "Small Punch Puppies update failed", 0x10)
        else:
            print(message, file=sys.stderr)
        time.sleep(0.25)


if __name__ == "__main__":
    run()
