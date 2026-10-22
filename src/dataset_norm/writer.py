"""序列写入器：按规范创建目录并增量写 data.csv / sensor.yaml / settings.json。"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Sequence

from .layout import SequenceLayout, make_sequence_layout
from .schema import (
    CAMERA_TYPES,
    IMU_FIELDS,
    POSE_FIELDS,
    SchemaError,
    SensorMeta,
    Settings,
    validate_imu_row,
    validate_pose_row,
)


def _dump_sensor_yaml(meta: SensorMeta) -> str:
    # 手写极简 YAML，避免强依赖 PyYAML；键序固定，便于 diff。
    lines = [
        f"sensor_type: {meta.sensor_type}",
        f"rate_hz: {meta.rate_hz}",
        f"frame_id: {meta.frame_id}",
        f"topic: {meta.topic or meta.sensor_type}",
    ]
    if meta.notes:
        # 单行 notes；含换行则替换为空格
        notes = meta.notes.replace("\n", " ").strip()
        lines.append(f'notes: "{notes}"')
    return "\n".join(lines) + "\n"


class _CsvChannel:
    """一路时序 CSV 的追加写（首行写表头）。"""

    def __init__(self, path: Path, fields: Sequence[str]) -> None:
        self.path = path
        self.fields = tuple(fields)
        self._fh = None
        self._writer: csv.writer | None = None
        self._count = 0
        self._last_ts: float | None = None

    def open(self, append: bool = False) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        self._fh = open(self.path, mode, newline="", encoding="utf-8")
        self._writer = csv.writer(self._fh)
        if not append:
            self._writer.writerow(self.fields)
        elif self._count == 0 and append:
            # 追加模式下文件可能已有表头；若刚创建仍写表头
            if self.path.stat().st_size == 0:
                self._writer.writerow(self.fields)

    def append(self, row: Sequence[Any]) -> None:
        if self._writer is None or self._fh is None:
            raise RuntimeError("channel not opened")
        ts = float(row[0])
        if ts < 0:
            raise SchemaError(f"{self.path.name}: negative timestamp {ts}")
        if self._last_ts is not None and ts <= self._last_ts:
            raise SchemaError(
                f"{self.path.name}: timestamp not increasing "
                f"({self._last_ts} -> {ts})"
            )
        self._writer.writerow(row)
        self._last_ts = ts
        self._count += 1

    @property
    def count(self) -> int:
        return self._count

    def close(self) -> None:
        if self._fh is not None:
            self._fh.flush()
            self._fh.close()
            self._fh = None
            self._writer = None


class SequenceWriter:
    """创建一条序列并接收各传感器样本。

    用法::

        w = SequenceWriter(root, world="SimpleUnderwater", agent="auv0",
                           track="track0", settings=Settings(...))
        w.register_imu("imu0", rate_hz=200, frame_id="auv0/imu")
        w.add_imu("imu0", t_ns, gyro, acc)
        w.close()
    """

    def __init__(
        self,
        root: str | Path,
        world: str,
        agent: str,
        track: str,
        settings: Settings,
        *,
        append: bool = False,
    ) -> None:
        self.layout: SequenceLayout = make_sequence_layout(root, world, agent, track)
        self.settings = settings
        self.append = append
        self._imu: dict[str, _CsvChannel] = {}
        self._pose: dict[str, _CsvChannel] = {}
        self._cam_channels: dict[str, _CsvChannel] = {}
        self._cams: dict[str, Path] = {}  # sensor_name -> images dir
        self._cam_meta: dict[str, SensorMeta] = {}
        self._closed = False

        if not append and self.layout.sequence_dir.exists():
            # 允许目录已存在（同次会话重复 open），但 settings 覆盖写
            pass
        self.layout.sequence_dir.mkdir(parents=True, exist_ok=True)
        self._write_settings()

    def _write_settings(self) -> None:
        path = self.layout.settings_path
        payload = self.settings.to_dict()
        if self.append and path.exists():
            return
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def register_imu(self, name: str, rate_hz: float, frame_id: str, notes: str = "") -> None:
        meta = SensorMeta(
            sensor_type="imu", rate_hz=rate_hz, frame_id=frame_id, notes=notes
        )
        yaml_path = self.layout.sensor_yaml_path(name)
        csv_path = self.layout.data_csv_path(name)
        if not self.append or not yaml_path.exists():
            yaml_path.parent.mkdir(parents=True, exist_ok=True)
            yaml_path.write_text(_dump_sensor_yaml(meta), encoding="utf-8")
        ch = _CsvChannel(csv_path, IMU_FIELDS)
        ch.open(append=self.append)
        self._imu[name] = ch

    def register_pose(self, name: str = "pose_groundtruth", rate_hz: float = 20.0, frame_id: str = "world") -> None:
        meta = SensorMeta(
            sensor_type="pose", rate_hz=rate_hz, frame_id=frame_id, notes="ground truth"
        )
        yaml_path = self.layout.sensor_yaml_path(name)
        csv_path = self.layout.data_csv_path(name)
        if not self.append or not yaml_path.exists():
            yaml_path.parent.mkdir(parents=True, exist_ok=True)
            yaml_path.write_text(_dump_sensor_yaml(meta), encoding="utf-8")
        ch = _CsvChannel(csv_path, POSE_FIELDS)
        ch.open(append=self.append)
        self._pose[name] = ch

    def register_camera(
        self,
        name: str,
        sensor_type: str,
        rate_hz: float,
        frame_id: str,
        cam: str = "cam0",
        notes: str = "",
    ) -> Path:
        if sensor_type not in CAMERA_TYPES:
            raise SchemaError(f"register_camera: invalid sensor_type {sensor_type!r}")
        meta = SensorMeta(
            sensor_type=sensor_type, rate_hz=rate_hz, frame_id=frame_id, notes=notes
        )
        yaml_path = self.layout.sensor_yaml_path(name, cam=cam)
        csv_path = self.layout.data_csv_path(name, cam=cam)
        img_dir = self.layout.images_dir(name, cam)
        if not self.append or not yaml_path.exists():
            yaml_path.parent.mkdir(parents=True, exist_ok=True)
            yaml_path.write_text(_dump_sensor_yaml(meta), encoding="utf-8")
        img_dir.mkdir(parents=True, exist_ok=True)
        ch = _CsvChannel(csv_path, ("#timestamp [ns]", "filename"))
        ch.open(append=self.append)
        self._cam_channels[name] = ch
        self._cams[name] = img_dir
        self._cam_meta[name] = meta
        return img_dir

    def add_imu(
        self,
        name: str,
        t_ns: int | float,
        gyro: Sequence[float],
        acc: Sequence[float],
    ) -> None:
        ch = self._imu[name]
        row = validate_imu_row([t_ns, *gyro, *acc])
        # 整数时间戳写整型，避免 1.0e16 科学计数
        ch.append([int(row[0]), *row[1:]])

    def add_pose(
        self,
        name: str,
        t_ns: int | float,
        position: Sequence[float],
        quaternion_wxyz: Sequence[float],
    ) -> None:
        ch = self._pose[name]
        row = validate_pose_row([t_ns, *position, *quaternion_wxyz])
        ch.append([int(row[0]), *row[1:]])

    def add_camera_frame(self, name: str, t_ns: int | float, filename: str) -> None:
        if name not in self._cam_channels:
            raise KeyError(f"camera not registered: {name}")
        if not filename or "/" in filename or "\\" in filename:
            raise SchemaError(f"filename must be a bare name, got {filename!r}")
        t = int(t_ns)
        if t < 0:
            raise SchemaError(f"camera timestamp must be >= 0, got {t}")
        self._cam_channels[name].append([t, filename])

    def camera_image_path(self, name: str, filename: str) -> Path:
        return self._cams[name] / filename

    def close(self) -> None:
        if self._closed:
            return
        for ch in list(self._imu.values()):
            ch.close()
        for ch in list(self._pose.values()):
            ch.close()
        for ch in self._cam_channels.values():
            ch.close()
        self._closed = True

    def __enter__(self) -> "SequenceWriter":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def stats(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for k, ch in self._imu.items():
            out[f"imu:{k}"] = ch.count
        for k, ch in self._pose.items():
            out[f"pose:{k}"] = ch.count
        for k, ch in self._cam_channels.items():
            out[f"cam:{k}"] = ch.count
        return out
