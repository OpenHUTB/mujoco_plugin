import xml.etree.ElementTree as ET
import mujoco
import mujoco.viewer
from pathlib import Path

def build_underwater_assembly():
    print("=" * 60)
    print("正在执行水下机器人全系统组装...")
    print("架构：长方体基座 + 绝对路径网格暴力重构")
    print("=" * 60)

    # 1. 现代化安全路径寻址
    current_dir = Path(__file__).resolve().parent
    plugin_root = current_dir.parents[1]
    
    data_dir = current_dir / "data"
    menagerie_dir = plugin_root / "assets" / "mujoco_menagerie"
    ur5e_dir = menagerie_dir / "universal_robots_ur5e"
    robotiq_dir = menagerie_dir / "robotiq_2f85"
    
    rov_xml_path = data_dir / "rov_base.xml"
    ur5e_gripper_xml_path = ur5e_dir / "ur5e_with_gripper.xml"

    # 2. XML 树解析与动态挂载
    rov_tree = ET.parse(str(rov_xml_path))
    rov_root = rov_tree.getroot()

    ur5e_tree = ET.parse(str(ur5e_gripper_xml_path))
    ur5e_root = ur5e_tree.getroot()

    rov_body = rov_root.find(".//body[@name='rov']")
    ur5e_base = ur5e_root.find(".//body[@name='base']")

    # 挂载到长方体腹部前端 (Z = -0.2)，
    ur5e_base.set("pos", "0.2 0 -0.2")
    ur5e_base.set("quat", "0 0 1 0")
    rov_body.append(ur5e_base)

    # 3. 核心修复：相对路径映射，确保跨平台兼容
    # 相对路径基于 XML 文件所在位置 (src/underwater/data/)
    # 最终模型目录结构: src/underwater/data/meshes/{ur5e|robotiq}/...
    data_dir_abs = data_dir.resolve()
    ur5e_mesh_dir = ur5e_dir / "assets"
    robotiq_mesh_dir = robotiq_dir / "assets"
    
    # 从 Menagerie 复制 mesh 到 data/meshes/ 目录（一次性操作）
    meshes_output_dir = data_dir / "meshes"
    ur5e_output_dir = meshes_output_dir / "ur5e"
    robotiq_output_dir = meshes_output_dir / "robotiq"
    ur5e_output_dir.mkdir(parents=True, exist_ok=True)
    robotiq_output_dir.mkdir(parents=True, exist_ok=True)
    
    import shutil
    
    # 复制 UR5e meshes
    if ur5e_mesh_dir.exists():
        for src_mesh in ur5e_mesh_dir.glob("*.obj"):
            dst = ur5e_output_dir / src_mesh.name
            if not dst.exists():
                shutil.copy2(src_mesh, dst)
    
    # 复制 Robotiq meshes
    if robotiq_mesh_dir.exists():
        for src_mesh in robotiq_mesh_dir.glob("*.stl"):
            dst = robotiq_output_dir / src_mesh.name
            if not dst.exists():
                shutil.copy2(src_mesh, dst)
    
    # 使用相对路径 (meshes/ur5e/xxx.obj, meshes/robotiq/xxx.stl)
    for mesh in ur5e_root.iter("mesh"):
        file_attr = mesh.get("file")
        if file_attr:
            filename = Path(file_attr).name
            # 判断是 Robotiq 还是 UR5e
            if "robotiq" in file_attr.lower() or filename.startswith("base_") and "gripper" in str(robotiq_mesh_dir):
                rel_path = f"meshes/robotiq/{filename}"
            else:
                rel_path = f"meshes/ur5e/{filename}"
            mesh.set("file", rel_path)

    # 4. 全局流体力学属性覆盖
    for geom in ur5e_root.iter("geom"):
        geom_class = geom.get("class", "")
        if "visual" not in geom_class:
            geom.set("fluidshape", "ellipsoid")

    # 5. 碰撞干涉屏蔽与资源合并
    contact_tag = rov_root.find("contact")
    if contact_tag is None:
        contact_tag = ET.SubElement(rov_root, "contact")
    
    ET.SubElement(contact_tag, "exclude", {"body1": "rov", "body2": "base"})
    ET.SubElement(contact_tag, "exclude", {"body1": "rov", "body2": "shoulder_link"})

    tags_to_merge = ["asset", "actuator", "sensor", "contact", "tendon", "default", "equality"]
    for tag in tags_to_merge:
        ur5e_tag = ur5e_root.find(tag)
        if ur5e_tag is not None:
            rov_tag = rov_root.find(tag)
            if rov_tag is None:
                rov_tag = ET.SubElement(rov_root, tag)
            for item in ur5e_tag:
                rov_tag.append(item)

    # 6. 处理 Compiler 标签：解除 meshdir 劫持
    compiler_tag = rov_root.find("compiler")
    ur5e_compiler = ur5e_root.find("compiler")
    if compiler_tag is not None and ur5e_compiler is not None:
        for key, val in ur5e_compiler.attrib.items():
            # 剔除 meshdir，防止 MuJoCo 再次进行画蛇添足的相对路径拼接
            if key != "meshdir":
                compiler_tag.set(key, val)

    # 7. 导出与物理验证
    merged_model_path = data_dir / "underwater_rov_with_arm.xml"
    rov_tree.write(str(merged_model_path), encoding="utf-8")
    print(f"物理融合完成！相对路径已全部被绝对化重构。")

    print("正在拉起 MuJoCo 仿真器进行验证...")
    model = mujoco.MjModel.from_xml_path(str(merged_model_path))
    data = mujoco.MjData(model)
    mujoco.viewer.launch(model, data)

if __name__ == "__main__":
    build_underwater_assembly()