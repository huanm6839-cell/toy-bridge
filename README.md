# toy-bridge

A configurable BLE discovery and MCP bridge scaffold based on the BLE connection guide.

## Included

- Scan nearby BLE devices and inspect their GATT services and characteristic permissions.
- Send one explicitly supplied hexadecimal packet to a configured, writable characteristic through MCP.
- Check characteristic write permissions before sending.

## Device-specific work still required

The repository does not contain the target device's real write UUID or captured protocol packets. This project does not guess modes, intensity values, stop packets, or keepalive traffic, and it does not repeat packets automatically. Actual control requires values confirmed for the exact device.

## Install

Use Python 3.11+ on a computer with a BLE adapter:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
Copy-Item .env.example .env
```

## Discover and inspect

Run `toy-bridge-scan`, put the matching name or address in `.env` as `TOY_BLE_NAME` or `TOY_BLE_ADDRESS`, then run `toy-bridge-inspect`. Set `TOY_WRITE_UUID` only after confirming a characteristic has `write` or `write-without-response` permission.

## MCP

Run `toy-bridge` to start a local STDIO MCP server. It provides:

- `toy_scan` - scan nearby BLE devices.
- `toy_inspect` - list the configured device's services and characteristics.
- `toy_send_packet` - send one caller-provided packet. No packet is inferred or repeated.

The MCP client must launch the local `toy-bridge` process. It does not open a public network port.

## Remote access

For an HTTPS tunnel, configure an authenticated access policy and forward only to a local service. Do not expose an unauthenticated device-control endpoint to the public internet. Remote deployment and the device protocol require separate confirmation in the target environment.

## Settings

| Variable | Purpose |
| --- | --- |
| `TOY_BLE_NAME` | BLE broadcast name; use this or the address |
| `TOY_BLE_ADDRESS` | BLE address; use this or the name |
| `TOY_WRITE_UUID` | Confirmed writable characteristic UUID |
| `TOY_WRITE_WITH_RESPONSE` | Optional; blank selects a supported write mode |
| `TOY_SCAN_TIMEOUT` | Scan duration in seconds; default 8 |
| `TOY_CONNECT_TIMEOUT` | Connection timeout in seconds; default 15 |
