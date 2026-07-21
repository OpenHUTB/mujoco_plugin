import holoocean

cfg = {
    "name": "test_rgb_camera",
    "world": "SimpleUnderwater",
    "package_name": "Ocean",
    "main_agent": "auv0",
    "ticks_per_sec": 60,
    "agents": [
        {
            "agent_name": "auv0",
            "agent_type": "HoveringAUV",
            "sensors": [
                {
                    "sensor_type": "RGBCamera",
                    "socket": "CameraSocket",
                    "configuration": {
                        "CaptureWidth": 512,
                        "CaptureHeight": 512
                    }
                }
            ],
            "control_scheme": 0,
            "location": [0, 0, -10]
        }
    ]
}

with holoocean.make(scenario_cfg=cfg) as env:
    for _ in range(200):
        env.tick()