import os
import matplotlib.pyplot as plt

# 解决 Windows 中文字体显示问题
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def plot_depth_tracking(time_data, actual_z, target_z, save_dir):
    """1. 绘制 PID 深度追踪对比图 (闭环控制验证)"""
    plt.figure(figsize=(10, 5))
    
    plt.plot(time_data, actual_z, label="实际深度 (Actual Z)", linewidth=2.5, color='blue')
    plt.axhline(y=target_z, color='red', linestyle='--', linewidth=2, label="目标深度 (Target Z)")
    
    plt.title("水下机器人 PID 深度悬浮控制追踪曲线", fontsize=14)
    plt.xlabel("时间 (Time / s)", fontsize=12)
    plt.ylabel("深度 (Depth / m)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=11)
    plt.tight_layout()

    os.makedirs(save_dir, exist_ok=True)
    graph_path = os.path.join(save_dir, "depth_control_result.png")
    plt.savefig(graph_path, dpi=300)
    print(f"\n[可视化] 悬浮控制折线图已保存至: {os.path.abspath(graph_path)}")
    plt.close()

def plot_basic_scenarios(results, save_dir):
    """2. 绘制三大基础物理场景对比图 (基础流体模型验证)"""
    plt.figure(figsize=(12, 6))

    # 子图 1：Z 轴垂直位移曲线
    plt.subplot(1, 2, 1)
    for label, (t, z, _) in results.items():
        plt.plot(t, z, label=label, linewidth=2)
    plt.title("ROV 垂直位置变化 (Position Z)", fontsize=12)
    plt.xlabel("时间 (Time / s)")
    plt.ylabel("深度 (Depth / m)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()

    # 子图 2：Z 轴垂直速度曲线
    plt.subplot(1, 2, 2)
    for label, (t, _, vz) in results.items():
        plt.plot(t, vz, label=label, linewidth=2)
    plt.title("ROV 垂直速度变化 (Velocity Z)", fontsize=12)
    plt.xlabel("时间 (Time / s)")
    plt.ylabel("速度 (Velocity / m/s)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()

    plt.tight_layout()

    os.makedirs(save_dir, exist_ok=True)
    graph_path = os.path.join(save_dir, "underwater_test_results.png")
    plt.savefig(graph_path, dpi=300)
    print(f"\n[可视化] 基础流体测试对比图已保存至: {os.path.abspath(graph_path)}")
    plt.close()

def plot_anisotropic_drag(drag_results, save_dir):
    """3. 绘制 6-DOF 各向异性阻力衰减对比图 (非线性动力学验证)"""
    plt.figure("6-DOF 流体各向异性测试", figsize=(10, 6))
    
    for label, (t, v) in drag_results.items():
        plt.plot(t, v, label=label, linewidth=2.5)

    plt.title("水下机器人不同姿态受力后的速度衰减对比 (各向异性流体阻力)", fontsize=14)
    plt.xlabel("时间 (Time / s)", fontsize=12)
    plt.ylabel("速度 / 角速度 响应值", fontsize=12)
    plt.axvline(x=0.1, color='r', linestyle='--', alpha=0.5, label="撤销外力点")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=11)
    plt.tight_layout()

    os.makedirs(save_dir, exist_ok=True)
    graph_path = os.path.join(save_dir, "anisotropic_drag_test.png")
    plt.savefig(graph_path, dpi=300)
    print(f"\n[可视化] 6-DOF 各向异性阻力测试图表已保存至: {os.path.abspath(graph_path)}")
    plt.close()


def plot_ocean_current(time_data, speed_data, save_dir):
    """
    4. 绘制洋流速度变化图 (洋流模型验证)
    
    显示洋流速度幅值随时间的变化，用于验证 Gauss-Markov 过程的统计特性。
    """
    plt.figure("洋流速度时间序列", figsize=(12, 5))
    
    plt.plot(time_data, speed_data, label="洋流速度幅值 (Current Speed)",
             linewidth=2, color='teal')
    plt.title("洋流速度时间序列 (Gauss-Markov 过程)", fontsize=14)
    plt.xlabel("时间 (Time / s)", fontsize=12)
    plt.ylabel("速度 (Speed / m/s)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=11)
    plt.tight_layout()

    os.makedirs(save_dir, exist_ok=True)
    graph_path = os.path.join(save_dir, "ocean_current_speed.png")
    plt.savefig(graph_path, dpi=300)
    print(f"\n[可视化] 洋流速度曲线已保存至: {os.path.abspath(graph_path)}")
    plt.close()


def plot_depth_comparison(no_oc_t, no_oc_z, with_oc_t, with_oc_z, target_z, save_dir):
    """
    5. 绘制洋流对 PID 悬浮的影响对比图

    对比无洋流和有洋流两种情况下的深度跟踪曲线。
    """
    plt.figure("PID 悬浮：无洋流 vs 有洋流", figsize=(12, 6))
    
    if len(no_oc_t) > 0:
        plt.plot(no_oc_t, no_oc_z, label="无洋流 (No Current)",
                 linewidth=2.5, alpha=0.8)
    if len(with_oc_t) > 0:
        plt.plot(with_oc_t, with_oc_z, label="有洋流 (With Current)",
                 linewidth=2.5, alpha=0.8)
    
    plt.axhline(y=target_z, color='red', linestyle='--', linewidth=2,
                label=f"目标深度 (Target: {target_z}m)")
    
    plt.title("洋流对 PID 深度悬浮控制的影响", fontsize=14)
    plt.xlabel("时间 (Time / s)", fontsize=12)
    plt.ylabel("深度 (Depth / m)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=11)
    plt.tight_layout()

    os.makedirs(save_dir, exist_ok=True)
    graph_path = os.path.join(save_dir, "depth_comparison_oc.png")
    plt.savefig(graph_path, dpi=300)
    print(f"\n[可视化] 深度对比图已保存至: {os.path.abspath(graph_path)}")
    plt.close()


# ══════════════════════════════════════════════════════════════
# 测绘任务 (Survey Mission) 可视化
# ══════════════════════════════════════════════════════════════

def plot_survey_trajectory(waypoints, actual_traj, save_dir):
    """6. 测绘任务航迹图：规划测线 vs 实际航迹"""
    fig, ax = plt.subplots(figsize=(9, 6))

    ax.plot(waypoints[:, 0], waypoints[:, 1], color='crimson', linestyle='--',
            linewidth=1.8, label="规划测线 (Planned)")
    if len(actual_traj) > 1:
        ax.plot(actual_traj[:, 0], actual_traj[:, 1], color='tab:blue',
                linewidth=1.5, label="实际航迹 (Actual)")

    ax.scatter(waypoints[0, 0], waypoints[0, 1], c='green', s=70, marker='o',
               zorder=5, label="起点")
    ax.scatter(waypoints[-1, 0], waypoints[-1, 1], c='black', s=70, marker='s',
               zorder=5, label="终点")

    ax.set_aspect('equal', adjustable='datalim')
    ax.set_title("水下机器人测绘任务航迹 (弓字形测线 + LOS 制导)", fontsize=14)
    ax.set_xlabel("X / m", fontsize=12)
    ax.set_ylabel("Y / m", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=10, loc='best')
    plt.tight_layout()

    os.makedirs(save_dir, exist_ok=True)
    graph_path = os.path.join(save_dir, "survey_trajectory.png")
    plt.savefig(graph_path, dpi=300)
    print(f"\n[可视化] 测绘航迹图已保存至: {os.path.abspath(graph_path)}")
    plt.close()


def plot_cross_track(time_data, cross_track, save_dir):
    """7. 横向偏差曲线 (路径跟踪精度)"""
    plt.figure("横向偏差", figsize=(10, 4.5))

    plt.plot(time_data, cross_track, color='darkorange', linewidth=2,
             label="横向偏差 (Cross-track)")
    plt.axhline(y=0.0, color='gray', linestyle='-', linewidth=1)
    plt.axhline(y=1.0, color='red', linestyle=':', linewidth=1.2, label="±1 m 容差")
    plt.axhline(y=-1.0, color='red', linestyle=':', linewidth=1.2)

    plt.title("LOS 制导横向偏差随时间变化", fontsize=14)
    plt.xlabel("时间 (Time / s)", fontsize=12)
    plt.ylabel("横向偏差 (m)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=10)
    plt.tight_layout()

    os.makedirs(save_dir, exist_ok=True)
    graph_path = os.path.join(save_dir, "survey_cross_track.png")
    plt.savefig(graph_path, dpi=300)
    print(f"\n[可视化] 横向偏差曲线已保存至: {os.path.abspath(graph_path)}")
    plt.close()


def plot_coverage_map(tracker, save_dir):
    """8. 覆盖率栅格图 (绿色=已覆盖)"""
    plt.figure("覆盖率", figsize=(9, 5))

    plt.imshow(tracker.visited.T, origin='lower', cmap='Greens', vmin=0, vmax=1,
               extent=[0, tracker.width, 0, tracker.height], aspect='equal',
               interpolation='nearest')

    plt.title(f"作业区域覆盖率: {tracker.coverage * 100:.1f}%", fontsize=14)
    plt.xlabel("X / m", fontsize=12)
    plt.ylabel("Y / m", fontsize=12)
    plt.colorbar(label="已覆盖")
    plt.tight_layout()

    os.makedirs(save_dir, exist_ok=True)
    graph_path = os.path.join(save_dir, "survey_coverage.png")
    plt.savefig(graph_path, dpi=300)
    print(f"\n[可视化] 覆盖率栅格图已保存至: {os.path.abspath(graph_path)}")
    plt.close()