class PIDDepthController:
    """标准水下深度 PID 闭环控制器"""
    def __init__(self, kp=2000.0, ki=50.0, kd=1000.0, max_thrust=5000.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        self.max_thrust = max_thrust
        self.integral_error = 0.0
        self.prev_error = 0.0

    def compute(self, target_depth, current_depth, dt):
        """
        计算为了维持目标深度需要的 Z 轴推进力
        """
        error = target_depth - current_depth
        
        self.integral_error += error * dt
        # 积分限幅 (Anti-windup)，防止积分爆炸
        self.integral_error = max(min(self.integral_error, 100.0), -100.0)
        
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        
        thrust = (self.kp * error) + (self.ki * self.integral_error) + (self.kd * derivative)
        
        self.prev_error = error
        
        # 限制推进器最大输出绝对值
        return max(min(thrust, self.max_thrust), -self.max_thrust)