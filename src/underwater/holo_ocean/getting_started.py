import holoocean
import holodeck
import numpy as np

holoocean_version = holodeck.util.get_holodeck_version
print(f"Holoocean version: {holoocean_version}")

env = holoocean.make("PierHarbor-Hovering")

# 悬停的AUV对每个推进器发出指令
command = np.array([10,10,10,10,0,0,0,0])

for _ in range(1800):
   state = env.step(command)