"""Command-line helpers for BLE discovery and GATT inspection."""

import asyncio
import json

from .ble import inspect_gatt, scan_devices
from .config import Settings


def scan_main() -> None:
    settings = Settings.from_environment()
    devices = asyncio.run(scan_devices(settings.scan_timeout))
    print(json.dumps(devices, ensure_ascii=False, indent=2))


def inspect_main() -> None:
    settings = Settings.from_environment()
    settings.require_device_selector()
    services = asyncio.run(
        inspect_gatt(
            settings.device_name,
            settings.device_address,
            settings.scan_timeout,
            settings.connect_timeout,
        )
    )
    print(json.dumps(services, ensure_ascii=False, indent=2))
