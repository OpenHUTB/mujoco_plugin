class PIDDepthController:
    """
    水下深度 PID 闭环控制器（含洋流前馈补偿）
    
    控制律：
        F = Kp·e + Ki·∫e·dt + Kd·ė  +  V_current·feedforward_gain
    
    洋流前馈：当洋流向 Z 轴方向流动时，提前增加推力抵消洋流影响。
    """
    def __init__(self, kp=2000.0, ki=50.0, kd=1000.0, max_thrust=5000.0,
                 feedforward_gain=500.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.max_thrust = max_thrust
        self.feedforward_gain = feedforward_gain  # 洋流前馈增益
        
        self.integral_error = 0.0
        self.prev_error = 0.0

    def compute(self, target_depth, current_depth, dt, current_velocity=0.0):
        """
        计算为了维持目标深度需要的 Z 轴推进力
        
        Args:
            target_depth: 目标深度 (m)
            current_depth: 当前深度 (m)
            dt: 时间步长 (s)
            current_velocity: 当前深度处的洋流 Z 分量 (m/s)
                             正值=向下，负值=向上
        """
        error = target_depth - current_depth
        
        self.integral_error += error * dt
        # 积分限幅 (Anti-windup)，防止积分爆炸
        self.integral_error = max(min(self.integral_error, 100.0), -100.0)
        
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        
        # PID 控制量
        thrust_pid = (self.kp * error) + (self.ki * self.integral_error) + (self.kd * derivative)
        
        # 洋流前馈补偿：洋流向下(正velocity)需要额外向上推力
        thrust = thrust_pid + self.feedforward_gain * current_velocity
        
        self.prev_error = error
        
        # 限制推进器最大输出绝对值
        return max(min(thrust, self.max_thrust), -self.max_thrust)