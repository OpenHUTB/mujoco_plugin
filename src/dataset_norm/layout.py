"""序列目录布局：World / agent / track / sensor。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .schema import CAMERA_TYPES


@dataclass(frozen=True)
class SequenceLayout:
    """一条采集序列的根路径及约定子目录。"""

    root: Path
    world: str
    agent: str
    track: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", Path(self.root))
        if not self.world or not self.agent or not self.track:
            raise ValueError("world/agent/track must be non-empty")

    @property
    def sequence_dir(self) -> Path:
        return self.root / self.world / self.agent / self.track

    @property
    def settings_path(self) -> Path:
        return self.sequence_dir / "settings.json"

    def sensor_dir(self, sensor_name: str) -> Path:
        """例如 sensor_dir('imu0') -> .../imu0；相机类在其下再分 cam0。"""
        return self.sequence_dir / sensor_name

    def camera_dir(self, sensor_name: str, cam: str = "cam0") -> Path:
        return self.sensor_dir(sensor_name) / cam

    def sensor_yaml_path(self, sensor_name: str, cam: str | None = None) -> Path:
        base = self.sensor_dir(sensor_name)
        if cam is not None:
            base = base / cam
        return base / "sensor.yaml"

    def data_csv_path(self, sensor_name: str, cam: str | None = None) -> Path:
        base = self.sensor_dir(sensor_name)
        if cam is not None:
            base = base / cam
        return base / "data.csv"

    def images_dir(self, sensor_name: str, cam: str = "cam0") -> Path:
        return self.camera_dir(sensor_name, cam) / "data"

    def is_camera(self, sensor_type: str) -> bool:
        return sensor_type in CAMERA_TYPES


def make_sequence_layout(
    root: str | Path,
    world: str,
    agent: str,
    track: str,
) -> SequenceLayout:
    return SequenceLayout(root=Path(root), world=world, agent=agent, track=track)
