"""BLE discovery, GATT inspection, and one-shot packet writing."""

from __future__ import annotations

from bleak import BleakClient, BleakScanner


async def scan_devices(timeout: float = 8.0) -> list[dict[str, str | None]]:
    if timeout <= 0 or timeout > 60:
        raise ValueError("Scan timeout must be between 0 and 60 seconds.")
    devices = await BleakScanner.discover(timeout=timeout)
    return [
        {"name": device.name, "address": device.address}
        for device in devices
    ]


async def _find_device(name: str | None, address: str | None, timeout: float):
    if not name and not address:
        raise ValueError("Provide a BLE name or address, or configure one in .env.")
    devices = await BleakScanner.discover(timeout=timeout)
    for device in devices:
        if address and device.address.lower() == address.lower():
            return device
        if name and (device.name or "").casefold() == name.casefold():
            return device
    selector = address or name
    raise RuntimeError(
        f"Could not find '{selector}'. Make sure it is advertising and try again."
    )


async def inspect_gatt(
    name: str | None, address: str | None, scan_timeout: float, connect_timeout: float
) -> list[dict[str, object]]:
    device = await _find_device(name, address, scan_timeout)
    result: list[dict[str, object]] = []
    async with BleakClient(device, timeout=connect_timeout) as client:
        for service in client.services:
            characteristics = []
            for characteristic in service.characteristics:
                characteristics.append(
                    {
                        "uuid": characteristic.uuid,
                        "properties": list(characteristic.properties),
                    }
                )
            result.append(
                {"service_uuid": service.uuid, "characteristics": characteristics}
            )
    return result


async def write_packet(
    *,
    name: str | None,
    address: str | None,
    characteristic_uuid: str,
    packet: bytes,
    with_response: bool | None,
    scan_timeout: float,
    connect_timeout: float,
) -> str:
    if not packet:
        raise ValueError("The packet is empty.")
    if len(packet) > 512:
        raise ValueError("The packet is too long (maximum 512 bytes).")

    device = await _find_device(name, address, scan_timeout)
    async with BleakClient(device, timeout=connect_timeout) as client:
        matches = [
            characteristic
            for service in client.services
            for characteristic in service.characteristics
            if characteristic.uuid.lower() == characteristic_uuid.lower()
        ]
        if not matches:
            raise RuntimeError(
                f"Characteristic {characteristic_uuid} was not found on this device."
            )
        if len(matches) > 1:
            raise RuntimeError(
                "That UUID appears more than once. This scaffold needs a unique "
                "characteristic UUID before it can write safely."
            )

        characteristic = matches[0]
        properties = set(characteristic.properties)
        supports_response = "write" in properties
        supports_no_response = "write-without-response" in properties
        if with_response is None:
            if supports_response:
                with_response = True
            elif supports_no_response:
                with_response = False
            else:
                raise RuntimeError("The selected characteristic does not support writing.")
        elif with_response and not supports_response:
            raise RuntimeError("The selected characteristic does not support write-with-response.")
        elif not with_response and not supports_no_response:
            raise RuntimeError("The selected characteristic does not support write-without-response.")

        await client.write_gatt_char(
            characteristic, packet, response=with_response
        )
    return (
        f"Sent {len(packet)} bytes to {characteristic_uuid}; "
        f"write-with-response={with_response}."
    )
