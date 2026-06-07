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