"""AirSea 数据集规范：目录布局、落盘写入与合法性校验。"""

from .layout import SequenceLayout, make_sequence_layout
from .schema import (
    IMU_FIELDS,
    POSE_FIELDS,
    SensorMeta,
    Settings,
    validate_imu_row,
    validate_pose_row,
)
from .writer import SequenceWriter

__all__ = [
    "IMU_FIELDS",
    "POSE_FIELDS",
    "SensorMeta",
    "Settings",
    "SequenceLayout",
    "SequenceWriter",
    "make_sequence_layout",
    "validate_imu_row",
    "validate_pose_row",
]
