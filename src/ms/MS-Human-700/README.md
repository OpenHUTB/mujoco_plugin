# MS-Human-700: Whole-body Human Musculoskeletal Model

<p align="center">
  <a href="https://lnsgroup.cc/research/MS-Human">Project Page</a> | <a href="https://github.com/LNSGroup/msgym">Reinforcement Learning Environments (msgym)</a>
</p>


<div align="center">
  <img src="Pictures/ms_human_render_front.png" width="40%">
  <img src="Pictures/render_gif.gif" width="40%">
</div>

## Overview

This directory contains the **MuJoCo XML** and asset files for the **MS-Human-700** model.

Related papers:
- [MS-Human-700 (ICRA 2024)](https://arxiv.org/abs/2312.05473)
- [DynSyn (ICML 2024)](https://arxiv.org/abs/2407.11472)
- [MPC2 (ICLR 2025)](https://arxiv.org/abs/2505.08238)
- [QFlex (ICLR 2026)](https://arxiv.org/abs/2601.19707)
- [and more (on balance & fall, contact-rich & deformable, vision language model ...)](https://lnsgroup.cc/research/MS-Human#papers)

For reinforcement learning environments and training scripts, see [msgym](https://github.com/LNSGroup/msgym).

To visualize the models, drag-and-drop the `MS-Human-700-*.xml` files into MuJoCo's `simulate` viewer.

## Models

### Primary Model (Full Body)

**File:** `MS-Human-700.xml`

Full body human musculoskeletal model for whole-body locomotion tasks.

* **Bodies:** 90 (optimized to **80**)
* **Joints:** 206 (constrained to **85** for control stability)
* **Muscles:** 700 actuators

### Legs Locomotion Model

**File:** `MS-Human-700-Locomotion.xml`

Focusing on lower-body dynamics. This model isolates the legs for locomotion research while simplifying the upper limbs and torso.

* **Bodies:** 80
* **Joints:** 36
* **Muscles:** 100

### Unimanual Manipulation Model

**File:** `MS-Human-700-Manipulation.xml`

Focusing on right arm and detailed right hand, designed for manipulation tasks.

* **Bodies:** 127
* **Joints:** 42
* **Muscles:** 81

## Control Demos

[**DynSyn**](https://lnsgroup.cc/research/DynSyn) control results:

<div align="center">
  <img src="Pictures/loco_full_gif.gif" width="32%">
  <img src="Pictures/loco_legs_gif.gif" width="32%">
  <img src="Pictures/mani_gif.gif" width="32%">
</div>
<br><br>

[**QFlex**](https://lnsgroup.cc/research/Qflex) control results:

<div align="center">
  <img src="Pictures/run_gif.gif" width="49%">
  <img src="Pictures/dance_gif.gif" width="49%">
</div>
<br><br>

**High-Fidelity Motion Tracking** results: 

Leveraging MuJoCo Warp for massively parallel **GPU** simulation enables the rapid and efficient training of control policies capable of high-precision motion tracking across diverse and dynamic trajectories.

The demos below illustrate these tracking capabilities of the MS-Human model:
*   **Overlap**: The model and reference trajectory are rendered directly to visualize tracking accuracy.
*   **Separate**: The model and reference trajectory are rendered with an offset to showcase motion details.

<table>
  <tr>
    <td align="center" width="25%">
      <img src="https://github.com/user-attachments/assets/0350ff08-2ab3-4019-a4be-bef6fbc276ad" alt="running_overlap" width="100%"><br>
      Running: Overlap
    </td>
    <td align="center" width="25%">
      <img src="https://github.com/user-attachments/assets/16084e8c-41f5-45a3-96b7-b69307c78e0c" alt="running_separate" width="100%"><br>
      Running: Separate
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <img src="https://github.com/user-attachments/assets/9aea44e9-3277-4d81-a096-6865e2dcc5e4" alt="walking_ovelap" width="100%"><br>
      Walking: Overlap
    </td>
    <td align="center" width="25%">
      <img src="https://github.com/user-attachments/assets/9c32033c-0ca6-4b0c-a6fd-f61f66481ee9" alt="walking_separate" width="100%"><br>
      Walking: Separate
    </td>
  </tr>
</table>
