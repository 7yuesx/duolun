import numpy as np


# 离散积分差分
class Discreteness(object):

    def __init__(self, dt):
        self.dt = dt
        self.last_diff = 0.0
        self.last_sum = 0.0
        self.diff_num = 0.0
        self.sum_num = 0.0

    def Sum(self, s_num):
        self.sum_num = self.last_sum + self.dt * s_num
        self.last_sum = self.sum_num
        return self.sum_num

    def Diff(self, d_num):
        self.diff_num = (d_num - self.last_diff) / self.dt
        self.last_diff = d_num
        return self.diff_num


# PID
class PID_control(object):
    def __init__(self, kp, ki, kd, targ_value, max_output=300):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.targ_value = targ_value

        self.computed_input = 0.0
        self.err = 0.0
        self.last_err = 0.0

        self.last_time = 0.0
        self.sum_err = 0.0
        self.theta_last = 0.0

        self.max_integral = 20000
        self.max_output = max_output
        self.err_LpfRatio = 1

        self.integral = 0.0

        self.output = 0.0

    def pid_Calculation(self, feedback_value, targ):
        # single step duration
        self.last_err = self.err
        self.targ_value = targ # 增加的
        self.err = self.targ_value - feedback_value

        self.err = self.err * self.err_LpfRatio + self.last_err * (1 - self.err_LpfRatio)
        self.output = (self.err - self.last_err) * self.kd
        self.output += self.err * self.kp
        self.integral += self.err * self.ki
        if self.integral < -self.max_integral:
            self.integral = -self.max_integral
        if self.integral > self.max_integral:
            self.integral = self.max_integral
        self.output += self.integral

        # print('PID,P,I,D,', self.output, self.err * self.kp, self.err * self.ki, (self.err - self.last_err) * self.kd)
        if self.output < -self.max_output:
            self.output = -self.max_output
        if self.output > self.max_output:
            self.output = self.max_output

        return self.output
    
class LowPassFilter:
    """一阶低通滤波器"""
    def __init__(self, alpha=0.1, initial_value=0.0):
        """
        参数:
        alpha: 滤波系数 (0-1之间)，越小滤波效果越强，响应越慢
        initial_value: 初始值
        """
        self.alpha = alpha
        self.filtered_value = initial_value
        self.initialized = False
    
    def filter(self, value):
        """滤波函数"""
        if not self.initialized:
            self.filtered_value = value
            self.initialized = True
        else:
            self.filtered_value = self.alpha * value + (1 - self.alpha) * self.filtered_value
        return self.filtered_value
    
    def reset(self, value=None):
        """重置滤波器"""
        self.initialized = False
        if value is not None:
            self.filtered_value = value
            self.initialized = True