"""合成一条最小合法序列，并用 validate 校验；不依赖 HoloOcean。"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

# 允许 `python -m tests.test_dataset_norm` 与直接运行
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from dataset_norm import SequenceWriter, Settings  # noqa: E402
from dataset_norm.validate import validate_sequence  # noqa: E402


def build_synthetic_sequence(root: Path) -> Path:
    settings = Settings(
        world="SimpleUnderwater",
        package="Ocean",
        ticks_per_sec=60,
        frames_per_sec=20,
        agents=("auv0",),
        random_seed=42,
        holoocean_version="2.3.0",
        notes="dataset_norm synthetic smoke",
    )
    seq_root = root / "AirSea-UV"
    n = 40  # 20 Hz * 2 s
    with SequenceWriter(
        root=seq_root,
        world=settings.world,
        agent="auv0",
        track="track0",
        settings=settings,
    ) as w:
        w.register_pose(name="pose_groundtruth", rate_hz=20.0, frame_id="world")
        w.register_imu(name="imu0", rate_hz=200.0, frame_id="auv0/imu")
        w.register_camera(
            name="rgb", sensor_type="rgb", rate_hz=20.0, frame_id="auv0/cam_front"
        )

        for i in range(n):
            t_ns = 50_000_000 * i  # 20 Hz
            x = 0.05 * i
            w.add_pose("pose_groundtruth", t_ns, (x, 0.0, -2.0), (1.0, 0.0, 0.0, 0.0))
            # IMU 200 Hz：每 pose 周期写 10 条
            for k in range(10):
                t_imu = t_ns + 5_000_000 * k
                if t_imu >= 50_000_000 * n and k > 0:
                    break
                w.add_imu("imu0", t_imu, (0.0, 0.0, 0.01), (0.0, 0.0, -9.81))
            # 1x1 PNG 占位（不引入 PIL 依赖：写最小合法 PNG 字节）
            fn = f"{t_ns:019d}.png"
            img_path = w.camera_image_path("rgb", fn)
            img_path.write_bytes(_MIN_PNG)
            w.add_camera_frame("rgb", t_ns, fn)

        stats = w.stats()
        assert stats["pose:pose_groundtruth"] == n, stats
        assert stats["cam:rgb"] == n, stats
        assert stats["imu:imu0"] >= n, stats

    return seq_root / settings.world / "auv0" / "track0"


# 1x1 灰色 PNG
_MIN_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108000000003776fe9a"
    "0000001049444154789c6360000002000100ffff03000006000557bfabd4000000"
    "0049454e44ae426082"
)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="dataset_norm_"))
    try:
        seq = build_synthetic_sequence(tmp)
        report = validate_sequence(sequence_dir=seq)
        print(f"sequence: {seq}")
        print(f"sensors: {report.sensors}")
        for issue in report.issues:
            print(f"  {issue.level}: {issue.path}: {issue.message}")
        if not report.ok:
            print("FAIL")
            return 1
        print("PASS")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
