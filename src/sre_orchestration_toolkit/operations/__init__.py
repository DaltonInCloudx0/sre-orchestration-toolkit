from __future__ import annotations

from typing import Callable, Dict, Any

from .start_instance import start_instance
from .stop_instance import stop_instance
from .snapshot_volume import snapshot_volume
from .cleanup_snapshots import cleanup_snapshots
from .rehydrate_instance import rehydrate_instance

OperationFn = Callable[..., Any]

registry: Dict[str, OperationFn] = {
    "start_instance": start_instance,
    "stop_instance": stop_instance,
    "snapshot_volume": snapshot_volume,
    "cleanup_snapshots": cleanup_snapshots,
    "rehydrate_instance": rehydrate_instance,
}
