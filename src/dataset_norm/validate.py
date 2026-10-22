"""序列合法性校验：结构完整性、时间戳、物理合理性。CLI 入口见 main。"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .layout import make_sequence_layout
from .schema import ALLOWED_SENSOR_TYPES, CAMERA_TYPES


@dataclass
class Issue:
    level: str  # "error" | "warn"
    path: str
    message: str


@dataclass
class Report:
    sequence_dir: str
    ok: bool = True
    n_error: int = 0
    n_warn: int = 0
    sensors: list[str] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    def error(self, path: str, message: str) -> None:
        self.issues.append(Issue("error", path, message))
        self.n_error += 1
        self.ok = False

    def warn(self, path: str, message: str) -> None:
        self.issues.append(Issue("warn", path, message))
        self.n_warn += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence_dir": self.sequence_dir,
            "ok": self.ok,
            "n_error": self.n_error,
            "n_warn": self.n_warn,
            "sensors": self.sensors,
            "issues": [asdict(i) for i in self.issues],
        }


def _parse_simple_yaml(text: str) -> dict[str, str]:
    """解析 writer 产出的极简 YAML（key: value，无嵌套）。"""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip('"')
    return out


def _read_csv_rows(path: Path) -> list[list[str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return []
    # 跳过表头
    return rows[1:]


def _check_timestamps(
    report: Report, path: Path, timestamps: list[float], expected_rate: float | None
) -> None:
    if not timestamps:
        report.error(str(path), "empty data.csv")
        return
    if any(t < 0 for t in timestamps):
        report.error(str(path), "negative timestamp found")
    for a, b in zip(timestamps, timestamps[1:]):
        if b <= a:
            report.error(str(path), f"timestamp not strictly increasing: {a} -> {b}")
            return
    if expected_rate and len(timestamps) >= 3:
        dts = [(b - a) / 1e9 for a, b in zip(timestamps, timestamps[1:])]
        mean_dt = sum(dts) / len(dts)
        if mean_dt <= 0:
            report.error(str(path), "non-positive mean dt")
            return
        actual_hz = 1.0 / mean_dt
        # 允许 ±30% 宽松带（抽帧/仿真抖动）
        if abs(actual_hz - expected_rate) / expected_rate > 0.3:
            report.warn(
                str(path),
                f"rate mismatch: expected ~{expected_rate:.3g} Hz, "
                f"got ~{actual_hz:.3g} Hz (mean dt={mean_dt:.4g}s)",
            )


def _check_imu(report: Report, path: Path, rate: float | None) -> None:
    rows = _read_csv_rows(path)
    if not rows:
        report.error(str(path), "no data rows")
        return
    ts: list[float] = []
    for i, row in enumerate(rows, start=2):
        if len(row) != 7:
            report.error(str(path), f"line {i}: expect 7 columns, got {len(row)}")
            return
        try:
            vals = [float(x) for x in row]
        except ValueError as e:
            report.error(str(path), f"line {i}: non-numeric ({e})")
            return
        if any(math.isnan(v) or math.isinf(v) for v in vals):
            report.error(str(path), f"line {i}: NaN/Inf")
            return
        ts.append(vals[0])
    _check_timestamps(report, path, ts, rate)


def _check_pose(report: Report, path: Path, rate: float | None) -> None:
    rows = _read_csv_rows(path)
    if not rows:
        report.error(str(path), "no data rows")
        return
    ts: list[float] = []
    for i, row in enumerate(rows, start=2):
        if len(row) != 8:
            report.error(str(path), f"line {i}: expect 8 columns, got {len(row)}")
            return
        try:
            vals = [float(x) for x in row]
        except ValueError as e:
            report.error(str(path), f"line {i}: non-numeric ({e})")
            return
        if any(math.isnan(v) or math.isinf(v) for v in vals):
            report.error(str(path), f"line {i}: NaN/Inf")
            return
        qw, qx, qy, qz = vals[4:8]
        norm = math.sqrt(qw * qw + qx * qx + qy * qy + qz * qz)
        if abs(norm - 1.0) > 1e-2:
            report.error(str(path), f"line {i}: quaternion norm={norm:.4f}")
            return
        ts.append(vals[0])
    _check_timestamps(report, path, ts, rate)


def _check_camera_csv(report: Report, path: Path, images_dir: Path, rate: float | None) -> None:
    rows = _read_csv_rows(path)
    if not rows:
        report.error(str(path), "no data rows")
        return
    ts: list[float] = []
    for i, row in enumerate(rows, start=2):
        if len(row) != 2:
            report.error(str(path), f"line {i}: expect 2 columns (ts, filename)")
            return
        try:
            t = float(row[0])
        except ValueError:
            report.error(str(path), f"line {i}: bad timestamp {row[0]!r}")
            return
        ts.append(t)
        fn = row[1].strip()
        if not fn:
            report.error(str(path), f"line {i}: empty filename")
            return
        img = images_dir / fn
        if not img.is_file():
            report.error(str(path), f"line {i}: missing image {img}")
            return
    _check_timestamps(report, path, ts, rate)


def validate_sequence(
    root: str | Path | None = None,
    world: str | None = None,
    agent: str | None = None,
    track: str | None = None,
    sequence_dir: str | Path | None = None,
) -> Report:
    """校验一条序列。

    要么传 sequence_dir 直接指向序列根（含 settings.json），
    要么传 root+world+agent+track。
    """
    if sequence_dir is not None:
        seq = Path(sequence_dir)
        # 从路径推断 world/agent/track（.../world/agent/track）
        if len(seq.parts) >= 3 and world is None:
            world, agent, track = seq.parts[-3], seq.parts[-2], seq.parts[-1]
        else:
            world = world or "unknown"
            agent = agent or "unknown"
            track = track or "unknown"
    else:
        if not (root and world and agent and track):
            raise ValueError("need sequence_dir or root+world+agent+track")
        seq = make_sequence_layout(root, world, agent, track).sequence_dir

    report = Report(sequence_dir=str(seq))
    if not seq.is_dir():
        report.error(str(seq), "sequence directory not found")
        return report

    settings_path = seq / "settings.json"
    if not settings_path.is_file():
        report.error(str(settings_path), "missing settings.json")
        settings: dict[str, Any] = {}
    else:
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            report.error(str(settings_path), f"invalid JSON: {e}")
            settings = {}
        for key in ("world", "package", "ticks_per_sec", "frames_per_sec", "agents"):
            if key not in settings:
                report.error(str(settings_path), f"missing key {key!r}")

    # 扫描子目录 = 传感器
    sensor_dirs = sorted(
        [p for p in seq.iterdir() if p.is_dir() and p.name not in {"__pycache__"}],
        key=lambda p: p.name,
    )
    if not sensor_dirs:
        report.error(str(seq), "no sensor directories")

    for sdir in sensor_dirs:
        name = sdir.name
        report.sensors.append(name)

        # 相机：name/cam0/{sensor.yaml,data.csv,data/}
        cam0 = sdir / "cam0"
        if cam0.is_dir() and (cam0 / "sensor.yaml").is_file():
            _validate_sensor_node(report, cam0, name, camera=True)
            continue
        if (sdir / "sensor.yaml").is_file():
            _validate_sensor_node(report, sdir, name, camera=False)
            continue
        # 允许空目录？视为错误，保证规范性
        report.error(str(sdir), "missing sensor.yaml (or cam0/sensor.yaml)")

    return report


def _validate_sensor_node(report: Report, node: Path, name: str, camera: bool) -> None:
    yaml_path = node / "sensor.yaml"
    csv_path = node / "data.csv"
    meta = _parse_simple_yaml(yaml_path.read_text(encoding="utf-8"))
    stype = meta.get("sensor_type", "")
    if stype not in ALLOWED_SENSOR_TYPES:
        report.error(str(yaml_path), f"invalid sensor_type {stype!r}")
    try:
        rate = float(meta.get("rate_hz", "nan"))
        if rate <= 0 or math.isnan(rate):
            raise ValueError
    except ValueError:
        report.error(str(yaml_path), f"invalid rate_hz {meta.get('rate_hz')!r}")
        rate = None
    if not meta.get("frame_id"):
        report.error(str(yaml_path), "empty frame_id")

    if not csv_path.is_file():
        report.error(str(csv_path), "missing data.csv")
        return

    if stype == "imu":
        _check_imu(report, csv_path, rate)
    elif stype == "pose":
        _check_pose(report, csv_path, rate)
    elif camera or stype in CAMERA_TYPES:
        images = node / "data"
        if not images.is_dir():
            report.error(str(images), "missing images data/ directory")
            return
        _check_camera_csv(report, csv_path, images, rate)
    else:
        # 其他时序传感器：至少有 ts + 至少 1 列数值
        rows = _read_csv_rows(csv_path)
        if not rows:
            report.error(str(csv_path), "no data rows")
            return
        width = len(rows[0])
        if width < 2:
            report.error(str(csv_path), "need timestamp + at least one value column")
            return
        ts: list[float] = []
        for i, row in enumerate(rows, start=2):
            if len(row) != width:
                report.error(str(csv_path), f"line {i}: ragged row")
                return
            try:
                ts.append(float(row[0]))
            except ValueError:
                report.error(str(csv_path), f"line {i}: bad timestamp")
                return
        _check_timestamps(report, csv_path, ts, rate)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate AirSea sequence layout")
    parser.add_argument("sequence", help="path to sequence dir (contains settings.json)")
    parser.add_argument("--json", dest="json_out", help="write report JSON to this path")
    args = parser.parse_args(argv)

    report = validate_sequence(sequence_dir=args.sequence)
    # 打印
    status = "PASS" if report.ok else "FAIL"
    print(f"[{status}] {report.sequence_dir}")
    print(f"  sensors: {', '.join(report.sensors) or '(none)'}")
    for issue in report.issues:
        print(f"  {issue.level.upper():5s}  {issue.path}: {issue.message}")
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
