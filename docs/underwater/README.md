# 水下机器人

## UE 高保真渲染

水下机器人仿真的渲染层基于 [UE](https://github.com/OpenHUTB/engine) 构建，负责提供逼真的水下视觉效果，包括水体折射、光照衰减、能见度分级等。渲染层与动力学层解耦，UE 负责画面，MuJoCo 负责物理计算。

- [MIMIR-UW 数据集文档](../MIMIR-UW2.md)

---
## MuJoCo 动力学模拟

* [MuJoCo 水下动力学模拟入门](./mujoco_introduction.md)

* [Mujoco 鱼形机器人模拟](./fish.md)


## Chrono 多物理场

* 多物理场模拟涉水的[效果](https://openhutb.github.io/chrono_doc/effect/)

---



## 参考

- [本章节仿真复现指南](./support.md)
- [MuJoCo 流体受力官方文档](https://docs.mujoco.cn/en/stable/computation/fluid.html)
- [Simple Models, Real Swimming: Digital Twins for Tendon-Driven Underwater Robots](https://arxiv.org/html/2602.23283v1)（ETH Zurich, 2025）
- [UNav-Sim 水下仿真参考](https://github.com/open-airlab/UNav-Sim)
- [OpenHUTB/locomotion flybody](https://github.com/OpenHUTB/locomotion/tree/master/flybody)（果蝇飞行流体模型）