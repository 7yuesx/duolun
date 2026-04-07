from scipy.spatial.transform import Rotation


class YawTracker:
    def __init__(self):
        self.yaw = [0, 0]
        self.lap = 0
        self.yaw_totalAngle = 0

    def get_euler(self, quat):
        global yaw, lap, yaw_totalAngle  # 声明全局变量
        r = Rotation.from_quat(quat)
        euler = r.as_euler('xyz')
        
        self.yaw[0] = euler[0] + 3.1415926
        
        if self.yaw[0] - self.yaw[1] > 3.14:
            self.lap -= 1
        elif self.yaw[0] - self.yaw[1] < -3.14:
            self.lap += 1
        yaw_totalAngle = self.lap * 3.1415926 * 2 + self.yaw[1]
        
        self.yaw[1] = self.yaw[0]
        
        return yaw_totalAngle