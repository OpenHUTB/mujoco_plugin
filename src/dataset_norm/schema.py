"""字段与元数据定义（EuRoC / ASL 风格，单位与列顺序固定）。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence

# data.csv 列名（不含表头注释）；顺序即写盘顺序
IMU_FIELDS: tuple[str, ...] = (
    "#timestamp [ns]",
    "w_x [rad s^-1]",
    "w_y [rad s^-1]",
    "w_z [rad s^-1]",
    "a_x [m s^-2]",
    "a_y [m s^-2]",
    "a_z [m s^-2]",
)

POSE_FIELDS: tuple[str, ...] = (
    "#timestamp [ns]",
    "p_x [m]",
    "p_y [m]",
    "p_z [m]",
    "q_w",
    "q_x",
    "q_y",
    "q_z",
)

ALLOWED_SENSOR_TYPES = frozenset(
    {
        "imu",
        "pose",
        "rgb",
        "depth",
        "segmentation",
        "dvl",
        "depth_sensor",
        "pressure",
        "gps",
        "magnetometer",
        "orientation",
        "velocity",
        "singlebeam_sonar",
        "profiling_sonar",
        "sidescan_sonar",
        "imaging_sonar",
        "lidar",
        "semantic_lidar",
        "acoustic_beacon",
        "optical_modem",
    }
)

# 相机类传感器：目录下应有 data/ 子目录存图像
CAMERA_TYPES = frozenset({"rgb", "depth", "segmentation"})


class SchemaError(ValueError):
    """字段/元数据不满足规范。"""


@dataclass(frozen=True)
class SensorMeta:
    """sensor.yaml 内容（YAML 友好的纯数据）。"""

    sensor_type: str
    rate_hz: float
    frame_id: str
    topic: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        if self.sensor_type not in ALLOWED_SENSOR_TYPES:
            raise SchemaError(
                f"unknown sensor_type {self.sensor_type!r}; "
                f"allowed: {sorted(ALLOWED_SENSOR_TYPES)}"
            )
        if self.rate_hz <= 0:
            raise SchemaError(f"rate_hz must be > 0, got {self.rate_hz}")
        if not self.frame_id:
            raise SchemaError("frame_id must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Settings:
    """settings.json：一次序列采集的全局参数。"""

    world: str
    package: str
    ticks_per_sec: int
    frames_per_sec: int
    agents: tuple[str, ...]
    random_seed: int = 0
    holoocean_version: str = ""
    notes: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.world:
            raise SchemaError("world must be non-empty")
        if self.ticks_per_sec <= 0 or self.frames_per_sec <= 0:
            raise SchemaError("ticks_per_sec / frames_per_sec must be > 0")
        if not self.agents:
            raise SchemaError("agents must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["agents"] = list(self.agents)
        return d


def _as_float_list(row: Sequence[Any], n: int, name: str) -> list[float]:
    if len(row) != n:
        raise SchemaError(f"{name}: expect {n} values, got {len(row)}")
    out: list[float] = []
    for i, v in enumerate(row):
        try:
            out.append(float(v))
        except (TypeError, ValueError) as e:
            raise SchemaError(f"{name}[{i}]: not a number: {v!r}") from e
    return out


def validate_imu_row(values: Sequence[Any]) -> list[float]:
    """校验一行 IMU：timestamp_ns + gyro(3) + acc(3)。返回 float 列表。"""
    nums = _as_float_list(values, 7, "imu row")
    if nums[0] < 0:
        raise SchemaError(f"imu timestamp must be >= 0 ns, got {nums[0]}")
    return nums


def validate_pose_row(values: Sequence[Any]) -> list[float]:
    """校验一行位姿：timestamp_ns + p(3) + q(4, wxyz)。四元数需近似单位长。"""
    nums = _as_float_list(values, 8, "pose row")
    if nums[0] < 0:
        raise SchemaError(f"pose timestamp must be >= 0 ns, got {nums[0]}")
    qw, qx, qy, qz = nums[4:8]
    norm = (qw * qw + qx * qx + qy * qy + qz * qz) ** 0.5
    if abs(norm - 1.0) > 1e-3:
        raise SchemaError(f"pose quaternion not unit: norm={norm:.6f}")
    return nums


def fields_to_header(fields: Sequence[str]) -> str:
    return "\n".join(fields)


def ensure_mapping(obj: Mapping[str, Any], keys: Sequence[str], name: str) -> None:
    missing = [k for k in keys if k not in obj]
    if missing:
        raise SchemaError(f"{name}: missing keys {missing}")
