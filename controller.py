import time
import math
import mujoco as mj
import mujoco.viewer
import numpy as np
from pynput import keyboard
import threading
from quat import YawTracker
from pid import PID_control, LowPassFilter
import struct
import socket
cmd_vx = 0.0
cmd_vy = 0.0
cmd_omega_w = 0.0
mode=0
def on_press(key):
    global cmd_vx, cmd_vy, cmd_omega_w, mode
    try:
        if key == keyboard.Key.up: cmd_vy = 4
        if key == keyboard.Key.down: cmd_vy = -4
        if key == keyboard.Key.left: cmd_vx = -4
        if key == keyboard.Key.right: cmd_vx = 4
        if key == keyboard.Key.space: 
            cmd_omega_w = -4 
            mode=1
        else :mode=0
    except AttributeError:
        pass

def on_release(key):
    global cmd_vx, cmd_vy, cmd_omega_w, mode
    # 松开按键时归零
    cmd_vx = 0.0
    cmd_vy = 0.0
    cmd_omega_w = 0.0


# 开启后台监听

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()
#####

UDP_IP = "127.0.0.1"
UDP_PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
vofa_tail = b'\x00\x00\x80\x7f'


dir_path = "duolun.xml"
m = mujoco.MjModel.from_xml_path(dir_path)
d = mujoco.MjData(m)

ctrl = np.zeros(m.nu)

# # 舵轮和轮子的关节名称
# steer_joints = [f"joint_steer{i+1}" for i in range(4)]
# wheel_joints = [f"joint_wheel{i+1}" for i in range(4)]

# # 获取关节id
# steer_ids = [m.joint(name).id for name in steer_joints]
# wheel_ids = [m.joint(name).id for name in wheel_joints]

steer_poss = [f"pos_steer{i+1}" for i in range(4)]
steer_vels = [f"vel_steer{i+1}" for i in range(4)]
wheel_poss = [f"pos_wheel{i+1}" for i in range(4)]
wheel_vels = [f"vel_wheel{i+1}" for i in range(4)]

gimbal_pos = "pos_Yaw"
gimbal_vel = "vel_Yaw"

gimbal_gyro = "imu_gyro"
# 获取关节id

steer_pos_ids = [m.sensor(name).id for name in steer_poss]
steer_vel_ids = [m.sensor(name).id for name in steer_vels]
wheel_pos_ids = [m.sensor(name).id for name in wheel_poss]
wheel_vel_ids = [m.sensor(name).id for name in wheel_vels]

gimbal_pos_id = m.sensor(gimbal_pos).id
gimbal_vel_id = m.sensor(gimbal_vel).id

gimbal_gyro_id = m.sensor(gimbal_gyro).id

orientation_sensor_id = m.sensor('orientation').id
imu_chassis_id = m.sensor('imu_chassis').id

imu_chassis = YawTracker()
imu_yaw = YawTracker()

# yaw_target = 0
# wheel1_pid = PID_control(1, 0, 1, 0)
# wheel2_pid = PID_control(1, 0, 1, 0)
# wheel3_pid = PID_control(1, 0, 1, 0)
# wheel4_pid = PID_control(1, 0, 1, 0)
# 机器人参数（轮距、轴距、轮半径等）

num_bodies = m.nbody
print(f"刚体数量: {num_bodies}")

# 2. 遍历所有body，获取名称、质量和父body ID
print("\n--- 静态信息 ---")
for body_id in range(num_bodies):
    # 通过ID获取body名称 [citation:3]
    body_name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, body_id)
    # 获取质量 (model.body_mass是一个一维数组)
    mass = m.body_mass[body_id]
    # 获取父body的ID (根body的父ID为-1)
    parent_id = m.body_parentid[body_id]
    # 获取惯性对角矩阵 (Ixx, Iyy, Izz)
    inertia = m.body_inertia[body_id]
    print(f"ID: {body_id}, 名称: {body_name}, 质量: {mass}, 父ID: {parent_id}, 惯性: {inertia}")

M = 15.680000000000003+14.693
J = 0.81954133 + 0.12577308 + 4*0.00149103
R = 0.39597975  # 轴距
r = 0.075 # 轮半径

ar = 2.0
at = 8.0 

phi = [3*math.pi/4, -3*math.pi/4, -math.pi/4, math.pi/4]

steer_directions_f = [0.0, 0.0, 0.0, 0.0]  # 舵轮
wheel_speeds_f = [0.0, 0.0, 0.0, 0.0]  # 轮子

steer_directions_b = [0.0, 0.0, 0.0, 0.0]  # 舵轮
wheel_speeds_b = [0.0, 0.0, 0.0, 0.0]  # 轮子

steer_angles = [0.0, 0.0, 0.0, 0.0]  # 舵轮
steer_speeds = [0.0, 0.0, 0.0, 0.0]  # 舵轮
wheel_angles = [0.0, 0.0, 0.0, 0.0]  # 轮子
wheel_speeds = [0.0, 0.0, 0.0, 0.0]  # 轮子

gimbal_angle=0
gimbal_speed=0

steer_controls = [0.0, 0.0, 0.0, 0.0]  # 舵轮
wheel_controls = [0.0, 0.0, 0.0, 0.0]  # 轮子

Vx = 0.0
Vy = 0.0
Wz = 0.0

ax = 0.0
ay = 0.0
aw = 0.0

Vx_f = 0.0
Vy_f = 0.0
Wz_f = 0.0

target = [0, 0, 0]
dt=0.3
Angle_Target = 0.0
Angle_Now = 0.0
Vmax = 1.0

def pi_to_pi(angle_current, angle_ref):
    error0 = angle_ref - angle_current
    error = 0.0
    while error0 > math.pi:
        error0-= 2*math.pi
        error -= 2*math.pi
    while error0 < -math.pi:
        error0+= 2*math.pi
        error += 2*math.pi
    return error  # 返回误差而不是修改角度



def forward_kinematics(steer_directions, wheel_speeds):
    vx = r*(wheel_speeds[0]*math.cos(steer_directions[0]) + wheel_speeds[1]*math.cos(steer_directions[1]) + 
            wheel_speeds[2]*math.cos(steer_directions[2]) + wheel_speeds[3]*math.cos(steer_directions[3]))/4
    vy = r*(wheel_speeds[0]*math.sin(steer_directions[0]) + wheel_speeds[1]*math.sin(steer_directions[1]) + 
            wheel_speeds[2]*math.sin(steer_directions[2]) + wheel_speeds[3]*math.sin(steer_directions[3]))/4
    w  = r*(wheel_speeds[0]*math.sin(steer_directions[0]-phi[0]) + wheel_speeds[1]*math.sin(steer_directions[1]-phi[1]) + 
            wheel_speeds[2]*math.sin(steer_directions[2]-phi[2]) + wheel_speeds[3]*math.sin(steer_directions[3]-phi[3]))/4/R
    
    return vx, vy, w

def Wheel_Calculation(wheel_control, steer_direction, ax, ay, aw, phi):

    wheel_control =	r*(M*ax*R*math.cos(steer_direction) + 
                       M*ay*R*math.sin(steer_direction)+J*aw*math.sin(steer_direction - phi))/R/4 
    return wheel_control

def Wheel_Pid(wheel_speed, steer_direction, vx, vy, w, phi, PID_control):
    wheel_speed_target = (vx*math.cos(steer_direction)+vy*math.sin(steer_direction)+w*R*math.sin(steer_direction - phi))/r
    return PID_control.pid_Calculation(wheel_speed, wheel_speed_target)

def Steer_Calculation(steer_speed, steer_direction, steer_control, phi,PID_control_angle, PID_control_speed):

    if abs(ax) <= 0.001 and abs(ay) <= 0.001 and abs(aw) <= 0.001 :
        steer_control = 0
        Angle_IK_=0.0
    elif (abs(Vx_f-R*Wz_f*math.sin(phi)) <= 0.1 and abs(Vy_f+R*Wz_f*math.cos(phi)) <= 0.1) :
        if  Vx==0 and Vy==0 and Wz==0:#abs(ax) <= 1.0  and abs(ay) <= 1.0 and abs(aw) <= 1.0*math.pi and
            steer_control = 0
            Angle_IK_=0.0
        else :
            Angle_IK = math.atan2(ay+R*(aw*math.cos(phi)-Wz_f**2*math.sin(phi)),ax-R*(aw*math.sin(phi)+Wz_f**2*math.cos(phi)))
            Angle_IK=Angle_IK+pi_to_pi(steer_direction,Angle_IK)
            #DL_Motor->control.Wrpm_IK = PID_Calculate( &DL_Motor->PID_P, DL_Motor->control.Angle, DL_Motor->control.Angle_IK);
            steer_control = PID_control_speed.pid_Calculation(steer_speed,PID_control_angle.pid_Calculation(steer_direction, Angle_IK) )
            Angle_IK_=0.0
    else :
        Angle_IK = math.atan2(((Vy_f+ay) + R*(Wz_f+aw)*math.cos(phi)) , ((Vx_f+ax) - R*(Wz_f+aw)*math.sin(phi)))
        denominator = ((Vx_f - R * Wz_f * math.sin(phi))**2 + 
                      (Vy_f + R * Wz_f * math.cos(phi))**2)
        
        numerator = (Vx_f * ay - Vy_f * ax - 
                    Wz_f * (Vx_f**2 + Vy_f**2) +
                    R * math.cos(phi) * (aw * Vx_f - Wz_f * (ax + Wz_f * vy)) +
                    R * math.sin(phi) * (aw * Vy_f - Wz_f * (ay + Wz_f * Vx_f)))
        
        Angle_IK_ = numerator / denominator
       
    
        Angle_IK_ = Angle_IK_filter.filter(Angle_IK_)            
        Angle_IK=Angle_IK+pi_to_pi(steer_direction,Angle_IK)    
        # if abs(Angle_IK) < 90.0:
        #     pass
        # elif abs(Angle_IK) >= 90.0 :
        #     if Angle_IK>= 90 :
        #         Angle_IK -= 180.0
        #     if Angle_IK <= -90.0 :
        #         Angle_IK += 180.0    
        #DL_Motor->control.Wrpm_IK = DL_Motor->control.Angle_+PID_Calculate( &DL_Motor->PID_P, DL_Motor->control.Angle, DL_Motor->control.Angle_IK);	
        steer_control = PID_control_speed.pid_Calculation(steer_speed, Angle_IK_+PID_control_angle.pid_Calculation( steer_direction, Angle_IK) )
    return steer_control
	

    

Wz_pid=PID_control(5.0 ,0.0,0.1,0,)

ax_pid=PID_control(2,0.0,0.0,0,)
ay_pid=PID_control(2,0.0,0.0,0,)
aw_pid=PID_control(2*math.pi,0.0,0.0,0,)

ax_filter=LowPassFilter(1.0)
ay_filter=LowPassFilter(1.0)
aw_filter=LowPassFilter(1.0)

Vx_f_filter=LowPassFilter(1.0)
Vy_f_filter=LowPassFilter(1.0) 
Wz_f_filter=LowPassFilter(1.0)

Angle_IK_filter=LowPassFilter(1.0)

yaw_pid_pos=PID_control(0.05,0,0.00005,0,4.0)
yaw_pid_vel=PID_control(16.0,0,0.00005,0,8)

steer1_pid_pos=PID_control(200.5,0,0.0,0,20000)
steer2_pid_pos=PID_control(200.5,0,0.0,0,20000)
steer3_pid_pos=PID_control(200.5,0,0.0,0,20000)
steer4_pid_pos=PID_control(200.5,0,0.0,0,20000)

steer1_pid_vel=PID_control(4.0,0,0.0001,0,5000)
steer2_pid_vel=PID_control(4.0,0,0.0001,0,5000)
steer3_pid_vel=PID_control(4.0,0,0.0001,0,5000)
steer4_pid_vel=PID_control(4.0,0,0.0001,0,5000)

wheel1_pid_pos=PID_control(0.001,0,0,0)
wheel2_pid_pos=PID_control(0.001,0,0,0)
wheel3_pid_pos=PID_control(0.001,0,0,0)
wheel4_pid_pos=PID_control(0.001,0,0,0)

wheel1_pid_vel=PID_control(0.001,0,0,0)
wheel2_pid_vel=PID_control(0.001,0,0,0)
wheel3_pid_vel=PID_control(0.001,0,0,0)
wheel4_pid_vel=PID_control(0.001,0,0,0)

with mujoco.viewer.launch_passive(m, d) as viewer:
    
    while viewer.is_running():
        step_start = time.time()
        # 读取当前舵轮角度和轮子速度
        # steer_angles = [d.qpos[steer_ids[i]] for i in range(4)]
        # wheel_speeds = [d.qvel[wheel_ids[i]] for i in range(4)]

        Vx=cmd_vx
        Vy=cmd_vy
        Wz=cmd_omega_w#=2*5*math.pi*a
        
        addrs = [m.sensor_adr[steer_pos_ids[i]] for i in range(4)]
        dims = [m.sensor_dim[steer_pos_ids[i]] for i in range(4)]
        steer_angles= [d.sensordata[addrs[i] : addrs[i] + dims[i]].copy() for i in range(4)]    

        addrs = [m.sensor_adr[steer_vel_ids[i]] for i in range(4)]
        dims = [m.sensor_dim[steer_vel_ids[i]] for i in range(4)]
        steer_speeds= [d.sensordata[addrs[i] : addrs[i] + dims[i]].copy() for i in range(4)]     

        addrs = [m.sensor_adr[wheel_pos_ids[i]] for i in range(4)]
        dims = [m.sensor_dim[wheel_pos_ids[i]] for i in range(4)]
        wheel_angles= [d.sensordata[addrs[i] : addrs[i] + dims[i]].copy() for i in range(4)]    

        addrs = [m.sensor_adr[wheel_vel_ids[i]] for i in range(4)]
        dims = [m.sensor_dim[wheel_vel_ids[i]] for i in range(4)]
        wheel_speeds= [d.sensordata[addrs[i] : addrs[i] + dims[i]].copy() for i in range(4)]  

        addr = m.sensor_adr[gimbal_pos_id]
        dim = m.sensor_dim[gimbal_pos_id]
        gimbal_angle= d.sensordata[addr : addr + dim].copy() 

        addr = m.sensor_adr[gimbal_vel_id]
        dim = m.sensor_dim[gimbal_vel_id]
        gimbal_speed= d.sensordata[addr : addr + dim].copy()  

        addr = m.sensor_adr[gimbal_gyro_id]
        dim = m.sensor_dim[gimbal_gyro_id]
        yaw_gimbal_gyro= d.sensordata[addr : addr + dim].copy()  

        adr_gimbal = m.sensor_adr[orientation_sensor_id]
        quat_gimbal = d.sensordata[adr_gimbal:adr_gimbal + 4]
        # quat_scipy = [quat_gimbal[1], quat_gimbal[2], quat_gimbal[3], quat_gimbal[0]]
        yaw_gimbal = imu_yaw.get_euler(quat_gimbal)
        
        adr_chassis = m.sensor_adr[imu_chassis_id]
        quat_chassis = d.sensordata[adr_chassis:adr_chassis + 4]
        # quat_scipy = [quat_chassis[1], quat_chassis[2], quat_chassis[3], quat_chassis[0]]
        yaw_chassis = imu_chassis.get_euler(quat_chassis)
        # print(yaw_chassis)
        
        err_angle = (yaw_gimbal - yaw_chassis)
        vx = cmd_vx * math.cos(err_angle) + cmd_vy * math.sin(err_angle)
        vy = -cmd_vx * math.sin(err_angle) + cmd_vy * math.cos(err_angle)
        # if vy == -0.0:
        #     vy = 0.0

        if mode :
            w = cmd_omega_w
        else :
            
            target[1]=0
            target[1]=target[1]+pi_to_pi(err_angle,target[1]) 
            w = Wz_pid.pid_Calculation(err_angle,target[1])
        
        # 正运动学解算
        Vx_f, Vy_f, Wz_f=forward_kinematics(steer_angles, wheel_speeds)
        # back_kinematics(Vx_f, Vy_f, Wz_f, steer_directions_b, wheel_speeds_b)

        Vx_f=Vx_f_filter.filter(Vx_f)
        Vy_f=Vy_f_filter.filter(Vy_f)
        Wz_f=Wz_f_filter.filter(Wz_f)

        ax = ax_pid.pid_Calculation(Vx_f,vx)
        ay = ay_pid.pid_Calculation(Vy_f,vy)
        aw = aw_pid.pid_Calculation(Wz_f,w)

        ax = ax_filter.filter(ax)
        ay = ay_filter.filter(ay)
        aw = aw_filter.filter(aw)

        if math.sqrt(ax**2+ay**2)>ar:
            ax*=ar/math.sqrt(ax**2+ay**2)
            ay*=ar/math.sqrt(ax**2+ay**2)
        if aw**2>at**2:
            aw*=abs(at/aw)

        #gimbal_control=Gimbal_Calculation()

        wheel_controls[0]=Wheel_Calculation(wheel_controls[0],steer_angles[0],ax,ay,aw,phi[0])+\
        Wheel_Pid(wheel_speeds[0], steer_angles[0], Vx_f, Vy_f, Wz_f, phi[0], wheel1_pid_vel)
        wheel_controls[1]=Wheel_Calculation(wheel_controls[1],steer_angles[1],ax,ay,aw,phi[1])+\
        Wheel_Pid(wheel_speeds[1], steer_angles[1], Vx_f, Vy_f, Wz_f, phi[1], wheel2_pid_vel)
        wheel_controls[2]=Wheel_Calculation(wheel_controls[2],steer_angles[2],ax,ay,aw,phi[2])+\
        Wheel_Pid(wheel_speeds[2], steer_angles[2], Vx_f, Vy_f, Wz_f, phi[2], wheel3_pid_vel)
        wheel_controls[3]=Wheel_Calculation(wheel_controls[3],steer_angles[3],ax,ay,aw,phi[3])+\
        Wheel_Pid(wheel_speeds[3], steer_angles[3], Vx_f, Vy_f, Wz_f, phi[3], wheel4_pid_vel)

        steer_controls[0] = Steer_Calculation(steer_speeds[0], steer_angles[0], steer_controls[0], phi[0], steer1_pid_pos, steer1_pid_vel)
        steer_controls[1] = Steer_Calculation(steer_speeds[1], steer_angles[1], steer_controls[1], phi[1], steer2_pid_pos, steer2_pid_vel)
        steer_controls[2] = Steer_Calculation(steer_speeds[2], steer_angles[2], steer_controls[2], phi[2], steer3_pid_pos, steer3_pid_vel)
        steer_controls[3] = Steer_Calculation(steer_speeds[3], steer_angles[3], steer_controls[3], phi[3], steer4_pid_pos, steer4_pid_vel)

        # for i in range(4) :
        #     wheel_controls[i]*=0.01
        #     steer_controls[i]*=0.01

        # 确保 send_list 中所有元素都是 float
        send_list = [
            float(Vx_f), 
            float(Vy_f), 
            float(Wz_f), 
            float(vx), 
            float(vy),
            float(w),
            float(ax),
            float(ay),
            float(aw),
            float(steer_angles[0]),
            float(steer_angles[1]),
            float(steer_angles[2]),
            float(steer_angles[3]),
            float(wheel_speeds[0]),
            float(wheel_speeds[1]),
            float(wheel_speeds[2]),
            float(wheel_speeds[3]),
        ]

# 打包数据  
        binary_data = struct.pack('<' + 'f' * len(send_list), *send_list)
        sock.sendto(binary_data + vofa_tail, (UDP_IP, UDP_PORT))
       
        # forward_kinematics(vx, vy, 10.0)
        
        # d.ctrl[8] = -yaw_pid.position_pid(yaw_target, yaw_gimbal)
        # print()
        # 控制器：将目标写入控制量
        target[0]=4*math.pi/4
        target[0]=target[0]+pi_to_pi(yaw_gimbal,target[0]) 
        d.ctrl[8] = -yaw_pid_vel.pid_Calculation(yaw_gimbal_gyro[2],yaw_pid_pos.pid_Calculation(yaw_gimbal,target[0]))
        for i in range(4):
            d.ctrl[i] = steer_controls[i]  # 前4个是舵轮位置控制
            d.ctrl[4 + i] = wheel_controls[i]  # 后4个是轮子速度控制
            
        mujoco.mj_step(m, d)
        viewer.sync()
        # 控制仿真步长
        time.sleep(max(0, m.opt.timestep - (time.time() - step_start)))