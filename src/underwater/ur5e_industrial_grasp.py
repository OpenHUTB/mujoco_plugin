import os
import shutil
import xml.etree.ElementTree as ET
import mujoco
import mujoco.viewer

def build_and_launch():
    print("=" * 60)
    print("正在执行底层 XML 级模型组装...")
    print("架构：XML 树合并 + 命名空间隔离 + 接触对过滤")
    print("=" * 60)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    menagerie_dir = os.path.join(base_dir, "assets", "mujoco_menagerie")
    ur5e_dir = os.path.join(menagerie_dir, "universal_robots_ur5e")
    gripper_dir = os.path.join(menagerie_dir, "robotiq_2f85")
    
    ur5e_xml_path = os.path.join(ur5e_dir, "ur5e.xml")
    gripper_xml_path = os.path.join(gripper_dir, "2f85.xml")
    
    if not os.path.exists(ur5e_xml_path) or not os.path.exists(gripper_xml_path):
        print("错误：找不到官方模型文件，请确保已正确下载并放置在 assets/mujoco_menagerie 目录下")
        return

    ur5e_tree = ET.parse(ur5e_xml_path)
    ur5e_root = ur5e_tree.getroot()

    gripper_tree = ET.parse(gripper_xml_path)
    gripper_root = gripper_tree.getroot()

    # 全链路指针隔离
    for elem in gripper_root.iter():
        if elem.tag in ["mesh", "texture"] and "name" not in elem.attrib and "file" in elem.attrib:
            implicit_name = os.path.splitext(os.path.basename(elem.get("file")))[0]
            elem.set("name", implicit_name)

        file_attr = elem.get("file")
        if file_attr and not file_attr.startswith("../"):
            elem.set("file", f"../robotiq_2f85/assets/{file_attr}")
        
        for attr in ["name", "class", "childclass"]:
            val = elem.get(attr)
            if val:
                elem.set(attr, f"gripper_{val}")
                
        pointer_attrs = [
            "material", "mesh", "texture", 
            "joint", "joint1", "joint2", 
            "body", "body1", "body2", 
            "geom", "geom1", "geom2", 
            "site", "tendon", "tendon1", "tendon2", 
            "objname", "target", "slider", "crank"
        ]
        for attr in pointer_attrs:
            val = elem.get(attr)
            if val:
                elem.set(attr, f"gripper_{val}")

    # 寻找挂载点
    attachment_site = None
    for site in ur5e_root.iter("site"):
        if site.get("name") == "attachment_site":
            attachment_site = site
            break

    parent_body = None
    for body in ur5e_root.iter("body"):
        if attachment_site in list(body):
            parent_body = body
            break

    # 动态继承法兰盘位姿，消除穿模卡死
    site_pos = attachment_site.get("pos", "0 0 0")
    site_quat = attachment_site.get("quat", "1 0 0 0")
    
    gripper_base = gripper_root.find("worldbody/body")
    mount_body = ET.Element("body", {"name": "gripper_mount", "pos": site_pos, "quat": site_quat})
    mount_body.append(gripper_base)
    parent_body.append(mount_body)

    # 强制物理引擎忽略手腕与夹爪基座的相互干涉
    contact_tag = ur5e_root.find("contact")
    if contact_tag is None:
        contact_tag = ET.SubElement(ur5e_root, "contact")
    ET.SubElement(contact_tag, "exclude", {"body1": parent_body.get("name"), "body2": gripper_base.get("name")})

    tags_to_merge = ["asset", "actuator", "sensor", "contact", "tendon", "default", "equality"]
    for tag in tags_to_merge:
        gripper_tag = gripper_root.find(tag)
        if gripper_tag is not None:
            ur5e_tag = ur5e_root.find(tag)
            if ur5e_tag is None:
                ur5e_tag = ET.SubElement(ur5e_root, tag)
            for item in gripper_tag:
                ur5e_tag.append(item)

    # 导出最终 XML
    merged_model_path = os.path.join(ur5e_dir, "ur5e_with_gripper.xml")
    ur5e_tree.write(merged_model_path, encoding="utf-8")
    print("结构组合成功，已生成合并后的模型文件：", merged_model_path)

    # 搭建场景：从配置文件读取场景 XML
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    scene_template_path = os.path.join(data_dir, "ur5e_scene.xml")
    master_scene_path = os.path.join(ur5e_dir, "industrial_scene.xml")
    shutil.copy(scene_template_path, master_scene_path)
    
    #启动
    print("正在拉起查看器")
    model = mujoco.MjModel.from_xml_path(master_scene_path)
    data = mujoco.MjData(model)
    mujoco.viewer.launch(model, data)

if __name__ == "__main__":
    build_and_launch()