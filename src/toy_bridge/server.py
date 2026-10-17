"""FastMCP tools for inspecting a BLE device and sending captured packets."""

import asyncio
import json

from fastmcp import FastMCP

from .ble import inspect_gatt, scan_devices, write_packet
from .config import Settings

mcp = FastMCP("toy-bridge")


@mcp.tool
async def toy_scan(timeout_seconds: float = 8.0) -> str:
    """List nearby BLE devices by advertising name and address."""
    devices = await scan_devices(timeout_seconds)
    return json.dumps(devices, ensure_ascii=False, indent=2)


@mcp.tool
async def toy_inspect() -> str:
    """Connect to the configured device and list its GATT services and characteristic permissions."""
    settings = Settings.from_environment()
    settings.require_device_selector()
    services = await inspect_gatt(
        settings.device_name,
        settings.device_address,
        settings.scan_timeout,
        settings.connect_timeout,
    )
    return json.dumps(services, ensure_ascii=False, indent=2)


@mcp.tool
async def toy_send_packet(packet_hex: str) -> str:
    """Send one packet captured from this exact device protocol; no packet is guessed or repeated."""
    settings = Settings.from_environment()
    characteristic_uuid = settings.require_write_uuid()
    try:
        packet = bytes.fromhex(packet_hex)
    except ValueError as exc:
        raise ValueError("packet_hex must contain valid hexadecimal bytes.") from exc
    return await write_packet(
        name=settings.device_name,
        address=settings.device_address,
        characteristic_uuid=characteristic_uuid,
        packet=packet,
        with_response=settings.write_with_response,
        scan_timeout=settings.scan_timeout,
        connect_timeout=settings.connect_timeout,
    )


def main() -> None:
    # Local MCP clients launch this process through STDIO.
    mcp.run()


if __name__ == "__main__":
    main()
