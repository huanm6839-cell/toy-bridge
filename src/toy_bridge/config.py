"""Environment-backed configuration for the BLE bridge."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv


def _optional_bool(name: str) -> bool | None:
    value = os.getenv(name, "").strip().lower()
    if not value:
        return None
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be true or false")


@dataclass(frozen=True)
class Settings:
    device_name: str | None
    device_address: str | None
    write_uuid: str | None
    write_with_response: bool | None
    scan_timeout: float
    connect_timeout: float

    @classmethod
    def from_environment(cls) -> "Settings":
        load_dotenv()
        scan_timeout = float(os.getenv("TOY_SCAN_TIMEOUT", "8"))
        connect_timeout = float(os.getenv("TOY_CONNECT_TIMEOUT", "15"))
        if scan_timeout <= 0 or connect_timeout <= 0:
            raise ValueError("Scan and connection timeouts must be positive")
        return cls(
            device_name=os.getenv("TOY_BLE_NAME", "").strip() or None,
            device_address=os.getenv("TOY_BLE_ADDRESS", "").strip() or None,
            write_uuid=os.getenv("TOY_WRITE_UUID", "").strip() or None,
            write_with_response=_optional_bool("TOY_WRITE_WITH_RESPONSE"),
            scan_timeout=scan_timeout,
            connect_timeout=connect_timeout,
        )

    def require_device_selector(self) -> None:
        if not self.device_name and not self.device_address:
            raise ValueError(
                "Set TOY_BLE_NAME or TOY_BLE_ADDRESS in .env before connecting."
            )

    def require_write_uuid(self) -> str:
        self.require_device_selector()
        if not self.write_uuid:
            raise ValueError(
                "Set TOY_WRITE_UUID to a characteristic confirmed to support writing."
            )
        return self.write_uuid
