# import numpy as np

# # 参数设置
# m = 15.680000000000003+26.238000000000003
# R = 0.39597975
# J = 10.81954133 + 0.2811737 + 4*0.00149103
# mu = 1.0
# g = 9.81
# alpha = 3.0
# phi = np.array([3*np.pi/4, -3*np.pi/4, -np.pi/4, np.pi/4])
# rhs = (mu * m * g * R)**2

# A = (m * R)**2
# B = J**2

# # 生成网格点
# x = np.linspace(-2, 2, 50)
# y = np.linspace(-2, 2, 50)
# X, Y = np.meshgrid(x, y)

# # 计算满足条件的区域
# mask = np.ones_like(X, dtype=bool)
# for i in range(4):
#     C = m * R * J * np.sin(alpha - phi[i])
#     val = A * X**2 + B * Y**2 + 2 * C * X * Y
#     mask = mask & (val <= rhs)

# # ASCII 可视化
# print("\n可行域可视化（'#' 表示可行区域）：")
# print("x轴: rddot, y轴: thetadot\n")

# for i in range(mask.shape[0]):  # y 方向
#     row = ''
#     for j in range(mask.shape[1]):  # x 方向
#         if mask[i, j]:
#             row += '#'
#         else:
#             row += '.'
#     # 每隔几行打印一次
#     if i % 2 == 0:
#         print(row)

# # 输出统计信息
# print(f"\n可行域占总区域比例: {np.sum(mask) / mask.size * 100:.2f}%")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import numpy as np

# class CorrectSolver:
#     """正确的求解器 - 包含角加速度作为未知数"""
    
#     def __init__(self, m=1.0, R=1.0, J=1.0, mu=0.5, g=9.8):
#         """
#         参数:
#         m: 质量
#         R: 半径
#         J: 转动惯量
#         mu: 摩擦系数
#         g: 重力加速度
        
#         未知变量:
#         r_ddot: 径向加速度
#         alpha: 角度位置
#         theta_ddot: 角加速度（注意：这是角加速度，不是角速度）
#         """
#         self.m = m
#         self.R = R
#         self.J = J
#         self.mu = mu
#         self.g = g
        
#         # 四个方向的角度
#         self.phi = np.array([0, np.pi/2, np.pi, 3*np.pi/2])
        
#         # 不等式右边常数
#         self.rhs = mu**2 * m**2 * g**2 * R**2
        
#     def left_side(self, r_ddot, alpha, theta_ddot, phi_i):
#         """计算不等式左边"""
#         term1 = self.m * r_ddot * self.R * np.cos(alpha) - self.J * theta_ddot * np.sin(phi_i)
#         term2 = self.m * r_ddot * self.R * np.sin(alpha) + self.J * theta_ddot * np.cos(phi_i)
#         return term1**2 + term2**2
    
#     def check_feasibility(self, r_ddot, alpha, theta_ddot, tolerance=1e-8):
#         """检查点是否可行"""
#         for phi_i in self.phi:
#             lhs = self.left_side(r_ddot, alpha, theta_ddot, phi_i)
#             if lhs > self.rhs + tolerance:
#                 return False
#         return True
    
#     def grid_search_2d(self, theta_ddot_fixed=1.0, r_range=(-20, 20), 
#                        alpha_range=(0, 2*np.pi), resolution=300):
#         """
#         固定角加速度，求解 (r_ddot, alpha) 的可行域
#         """
#         print(f"固定角加速度 θ̈ = {theta_ddot_fixed} rad/s²")
#         print(f"求解 (r̈, α) 的可行域...")
        
#         r_vals = np.linspace(r_range[0], r_range[1], resolution)
#         alpha_vals = np.linspace(alpha_range[0], alpha_range[1], resolution)
        
#         feasible_points = []
        
#         for r_ddot in r_vals:
#             for alpha in alpha_vals:
#                 if self.check_feasibility(r_ddot, alpha, theta_ddot_fixed):
#                     feasible_points.append((r_ddot, alpha))
            
#             if len(r_vals) > 0 and (np.where(r_vals == r_ddot)[0][0] + 1) % 50 == 0:
#                 progress = (np.where(r_vals == r_ddot)[0][0] + 1) / len(r_vals) * 100
#                 print(f"  进度: {progress:.1f}%, 已找到 {len(feasible_points)} 个可行点")
        
#         return np.array(feasible_points)
    
#     def grid_search_3d(self, r_range=(-20, 20), alpha_range=(0, 2*np.pi), 
#                        theta_ddot_range=(-10, 10), resolution=50):
#         """
#         三维网格搜索，求解所有三个未知数的可行域
#         """
#         print("三维网格搜索...")
#         print(f"r̈ 范围: {r_range}")
#         print(f"α 范围: [{alpha_range[0]:.2f}, {alpha_range[1]:.2f}] rad")
#         print(f"θ̈ 范围: {theta_ddot_range}")
#         print(f"网格分辨率: {resolution} x {resolution} x {resolution}")
        
#         r_vals = np.linspace(r_range[0], r_range[1], resolution)
#         alpha_vals = np.linspace(alpha_range[0], alpha_range[1], resolution)
#         theta_vals = np.linspace(theta_ddot_range[0], theta_ddot_range[1], resolution)
        
#         feasible_points = []
#         total = resolution ** 3
        
#         count = 0
#         for r_ddot in r_vals:
#             for alpha in alpha_vals:
#                 for theta_ddot in theta_vals:
#                     count += 1
#                     if self.check_feasibility(r_ddot, alpha, theta_ddot):
#                         feasible_points.append((r_ddot, alpha, theta_ddot))
                    
#                     if count % 10000 == 0:
#                         print(f"  进度: {count/total*100:.1f}%")
        
#         print(f"三维搜索完成！找到 {len(feasible_points)} 个可行点")
#         return np.array(feasible_points)
    
#     def analyze_results(self, feasible_points, variable_names):
#         """分析结果"""
#         if len(feasible_points) == 0:
#             print("未找到可行解！")
#             return None
        
#         print("\n" + "="*60)
#         print("可行域分析结果")
#         print("="*60)
        
#         print(f"\n参数设置:")
#         print(f"  质量 m = {self.m}")
#         print(f"  半径 R = {self.R}")
#         print(f"  转动惯量 J = {self.J}")
#         print(f"  摩擦系数 μ = {self.mu}")
#         print(f"  重力加速度 g = {self.g}")
#         print(f"  不等式右边常数 = {self.rhs:.4f}")
        
#         print(f"\n可行域统计:")
#         print(f"  可行点总数: {len(feasible_points)}")
        
#         for i, name in enumerate(variable_names):
#             values = feasible_points[:, i]
#             print(f"\n{name} 范围:")
#             print(f"  最小值: {np.min(values):.4f}")
#             print(f"  最大值: {np.max(values):.4f}")
#             print(f"  平均值: {np.mean(values):.4f}")
#             print(f"  标准差: {np.std(values):.4f}")
            
#             if name == "α":
#                 print(f"  最小值(角度): {np.min(values)*180/np.pi:.1f}°")
#                 print(f"  最大值(角度): {np.max(values)*180/np.pi:.1f}°")
        
#         return True
    
#     def parameter_sweep(self, theta_ddot_values=None, r_range=(-20, 20), 
#                         alpha_range=(0, 2*np.pi), resolution=200):
#         """
#         参数扫描：分析不同角加速度下的可行域变化
#         """
#         if theta_ddot_values is None:
#             theta_ddot_values = np.linspace(-10, 10, 10)
        
#         results = {}
        
#         print("\n参数扫描分析")
#         print("="*60)
        
#         for theta_ddot in theta_ddot_values:
#             feasible_points = self.grid_search_2d(theta_ddot, r_range, alpha_range, resolution)
            
#             if len(feasible_points) > 0:
#                 r_min, r_max = np.min(feasible_points[:,0]), np.max(feasible_points[:,0])
#                 alpha_min, alpha_max = np.min(feasible_points[:,1]), np.max(feasible_points[:,1])
                
#                 results[theta_ddot] = {
#                     'num_points': len(feasible_points),
#                     'r_range': (r_min, r_max),
#                     'alpha_range_rad': (alpha_min, alpha_max),
#                     'alpha_range_deg': (alpha_min*180/np.pi, alpha_max*180/np.pi),
#                     'r_span': r_max - r_min,
#                     'alpha_span_deg': (alpha_max - alpha_min) * 180/np.pi
#                 }
                
#                 print(f"\nθ̈ = {theta_ddot:.2f} rad/s²:")
#                 print(f"  可行点数: {len(feasible_points)}")
#                 print(f"  r̈ 范围: [{r_min:.2f}, {r_max:.2f}]")
#                 print(f"  α 范围: [{alpha_min*180/np.pi:.1f}°, {alpha_max*180/np.pi:.1f}°]")
#             else:
#                 print(f"\nθ̈ = {theta_ddot:.2f} rad/s²: 无可行解")
#                 results[theta_ddot] = None
        
#         return results

# def main():
#     print("="*60)
#     print("不等式求解器 - 正确版本（角加速度作为未知数）")
#     print("="*60)
    
#     # 创建求解器
#     solver = CorrectSolver(
#         m=1.0,    # 质量
#         R=1.0,    # 半径
#         J=1.0,    # 转动惯量
#         mu=0.5,   # 摩擦系数
#         g=9.8     # 重力加速度
#     )
    
#     print("\n变量说明:")
#     print("  r̈  - 径向加速度（未知）")
#     print("  α  - 角度位置（未知）")
#     print("  θ̈  - 角加速度（未知）")
    
#     # 选择求解模式
#     print("\n请选择求解模式:")
#     print("  1 - 固定角加速度，求解 (r̈, α) 的2D可行域")
#     print("  2 - 三维求解 (r̈, α, θ̈) 的可行域")
#     print("  3 - 参数扫描：分析不同角加速度下的可行域")
    
#     try:
#         mode = int(input("\n请输入模式 (1/2/3) [默认: 1]: ") or "1")
#     except:
#         mode = 1
    
#     if mode == 1:
#         # 2D求解
#         try:
#             theta_ddot = float(input("请输入角加速度 θ̈ 的值 (rad/s²) [默认: 1.0]: ") or "1.0")
#         except:
#             theta_ddot = 1.0
        
#         feasible_points = solver.grid_search_2d(theta_ddot)
        
#         if len(feasible_points) > 0:
#             solver.analyze_results(feasible_points, ["r̈", "α"])
#             np.savetxt(f'feasible_2d_theta_ddot_{theta_ddot}.csv', feasible_points, 
#                       delimiter=',', header='r_ddot,alpha', comments='')
#             print(f"\n结果已保存到 feasible_2d_theta_ddot_{theta_ddot}.csv")
#         else:
#             print("未找到可行解，请尝试调整角加速度参数")
    
#     elif mode == 2:
#         # 3D求解
#         feasible_points = solver.grid_search_3d(resolution=40)
        
#         if len(feasible_points) > 0:
#             solver.analyze_results(feasible_points, ["r̈", "α", "θ̈"])
#             np.savetxt('feasible_3d.csv', feasible_points, 
#                       delimiter=',', header='r_ddot,alpha,theta_ddot', comments='')
#             print("\n结果已保存到 feasible_3d.csv")
    
#     elif mode == 3:
#         # 参数扫描
#         results = solver.parameter_sweep()
        
#         # 保存参数扫描结果
#         with open('parameter_sweep_results.txt', 'w') as f:
#             f.write("角加速度 θ̈ 对可行域的影响\n")
#             f.write("="*60 + "\n")
#             for theta_ddot, result in results.items():
#                 if result:
#                     f.write(f"\nθ̈ = {theta_ddot:.2f} rad/s²:\n")
#                     f.write(f"  可行点数: {result['num_points']}\n")
#                     f.write(f"  r̈ 范围: [{result['r_range'][0]:.2f}, {result['r_range'][1]:.2f}]\n")
#                     f.write(f"  α 范围: [{result['alpha_range_deg'][0]:.1f}°, {result['alpha_range_deg'][1]:.1f}°]\n")
#                     f.write(f"  r̈ 跨度: {result['r_span']:.2f}\n")
#                     f.write(f"  α 跨度: {result['alpha_span_deg']:.1f}°\n")
        
#         print("\n参数扫描结果已保存到 parameter_sweep_results.txt")
    
#     print("\n" + "="*60)
#     print("计算完成！")
#     print("="*60)

# if __name__ == "__main__":
#     main()

import numpy as np

class AdvancedSolver:
    """高级求解器 - 支持多种求解模式"""
    
    def __init__(self, m=1.0, R=1.0, J=1.0, mu=0.5, g=9.8):
        """
        参数:
        m: 质量
        R: 半径
        J: 转动惯量
        mu: 摩擦系数
        g: 重力加速度
        """
        self.m = m
        self.R = R
        self.J = J
        self.mu = mu
        self.g = g
        
        # 四个方向的角度
        self.phi = np.array([3*np.pi/4, -3*np.pi/4, -np.pi/4, np1.pi/4])
        
        # 不等式右边常数
        self.rhs = mu**2 * m**2 * g**2 * R**2
        
    def left_side(self, r_ddot, alpha, theta_ddot, phi_i):
        """计算不等式左边"""
        term1 = self.m * r_ddot * self.R * np.cos(alpha) - self.J * theta_ddot * np.sin(phi_i)
        term2 = self.m * r_ddot * self.R * np.sin(alpha) + self.J * theta_ddot * np.cos(phi_i)
        return term1**2 + term2**2
    
    def check_feasibility(self, r_ddot, alpha, theta_ddot, tolerance=1e-8):
        """检查点是否可行"""
        for phi_i in self.phi:
            lhs = self.left_side(r_ddot, alpha, theta_ddot, phi_i)
            if lhs > self.rhs + tolerance:
                return False
        return True
    
    def solve_for_fixed_alpha(self, alpha_deg, r_range=(-30, 30), 
                              theta_ddot_range=(-20, 20), resolution=500):
        """
        给定角度α，求解(r̈, θ̈)的可行域
        
        参数:
        alpha_deg: 给定的角度（度数）
        r_range: 径向加速度搜索范围
        theta_ddot_range: 角加速度搜索范围
        resolution: 网格分辨率
        """
        alpha_rad = alpha_deg * np.pi / 180
        
        print(f"\n{'='*60}")
        print(f"求解模式：固定角度 α = {alpha_deg}° ({alpha_rad:.4f} rad)")
        print(f"{'='*60}")
        
        r_vals = np.linspace(r_range[0], r_range[1], resolution)
        theta_vals = np.linspace(theta_ddot_range[0], theta_ddot_range[1], resolution)
        
        feasible_points = []
        constraint_values = np.zeros((resolution, resolution))
        
        print("正在搜索可行解...")
        for i, r_ddot in enumerate(r_vals):
            for j, theta_ddot in enumerate(theta_vals):
                # 检查是否满足所有四个不等式
                is_feasible = True
                max_lhs = 0
                
                for phi_i in self.phi:
                    lhs = self.left_side(r_ddot, alpha_rad, theta_ddot, phi_i)
                    max_lhs = max(max_lhs, lhs)
                    if lhs > self.rhs:
                        is_feasible = False
                
                constraint_values[j, i] = max_lhs - self.rhs
                
                if is_feasible:
                    feasible_points.append((r_ddot, theta_ddot))
            
            # 显示进度
            if (i + 1) % 50 == 0:
                progress = (i + 1) / resolution * 100
                print(f"  进度: {progress:.1f}% (找到 {len(feasible_points)} 个可行点)")
        
        print(f"\n搜索完成！找到 {len(feasible_points)} 个可行点")
        
        return np.array(feasible_points), r_vals, theta_vals, constraint_values
    
    def analyze_fixed_alpha_results(self, feasible_points, alpha_deg, 
                                    r_range, theta_ddot_range):
        """分析固定角度下的结果"""
        if len(feasible_points) == 0:
            print(f"\n在 α = {alpha_deg}° 时未找到可行解！")
            print("可能的原因：")
            print("  1. 该角度下没有满足摩擦约束的加速度组合")
            print("  2. 搜索范围不够大")
            print("  3. 需要调整系统参数（如摩擦系数）")
            return None
        
        r_ddot_vals = feasible_points[:, 0]
        theta_ddot_vals = feasible_points[:, 1]
        
        print(f"\n{'='*60}")
        print(f"分析结果 (α = {alpha_deg}°)")
        print(f"{'='*60}")
        
        print(f"\n参数设置:")
        print(f"  质量 m = {self.m}")
        print(f"  半径 R = {self.R}")
        print(f"  转动惯量 J = {self.J}")
        print(f"  摩擦系数 μ = {self.mu}")
        print(f"  重力加速度 g = {self.g}")
        
        print(f"\n可行域统计:")
        print(f"  可行点总数: {len(feasible_points)}")
        print(f"  网格总点数: {len(r_ddot_vals) * len(theta_ddot_vals)}")
        
        print(f"\n径向加速度 r̈ 范围:")
        print(f"  最小值: {np.min(r_ddot_vals):.4f}")
        print(f"  最大值: {np.max(r_ddot_vals):.4f}")
        print(f"  平均值: {np.mean(r_ddot_vals):.4f}")
        print(f"  中位数: {np.median(r_ddot_vals):.4f}")
        print(f"  标准差: {np.std(r_ddot_vals):.4f}")
        
        print(f"\n角加速度 θ̈ 范围:")
        print(f"  最小值: {np.min(theta_ddot_vals):.4f}")
        print(f"  最大值: {np.max(theta_ddot_vals):.4f}")
        print(f"  平均值: {np.mean(theta_ddot_vals):.4f}")
        print(f"  中位数: {np.median(theta_ddot_vals):.4f}")
        print(f"  标准差: {np.std(theta_ddot_vals):.4f}")
        
        # 计算可行域面积（近似）
        r_span = np.max(r_ddot_vals) - np.min(r_ddot_vals)
        theta_span = np.max(theta_ddot_vals) - np.min(theta_ddot_vals)
        approx_area = r_span * theta_span
        print(f"\n可行域近似面积: {approx_area:.2f}")
        
        # 相关性分析
        correlation = np.corrcoef(r_ddot_vals, theta_ddot_vals)[0, 1]
        print(f"\nr̈ 和 θ̈ 的相关系数: {correlation:.4f}")
        
        if abs(correlation) > 0.7:
            print("  强相关性：径向加速度和角加速度高度相关")
        elif abs(correlation) > 0.3:
            print("  中等相关性：径向加速度和角加速度有一定关系")
        else:
            print("  弱相关性：径向加速度和角加速度相对独立")
        
        return {
            'alpha_deg': alpha_deg,
            'alpha_rad': alpha_deg * np.pi / 180,
            'num_points': len(feasible_points),
            'r_ddot_range': (np.min(r_ddot_vals), np.max(r_ddot_vals)),
            'theta_ddot_range': (np.min(theta_ddot_vals), np.max(theta_ddot_vals)),
            'r_ddot_mean': np.mean(r_ddot_vals),
            'theta_ddot_mean': np.mean(theta_ddot_vals),
            'correlation': correlation,
            'approx_area': approx_area
        }
    
    def find_boundary_for_fixed_alpha(self, alpha_deg, r_range=(-30, 30), 
                                      theta_ddot_range=(-20, 20), resolution=500):
        """找到固定角度下的边界线"""
        alpha_rad = alpha_deg * np.pi / 180
        print(f"\n寻找 α = {alpha_deg}° 时的边界线...")
        
        r_vals = np.linspace(r_range[0], r_range[1], resolution)
        theta_vals = np.linspace(theta_ddot_range[0], theta_ddot_range[1], resolution)
        
        boundary_points = []
        
        # 对每个phi方向找到边界
        for phi_i in self.phi:
            print(f"  处理方向 φ = {phi_i:.2f} rad ({phi_i*180/np.pi:.0f}°)")
            
            for r_ddot in r_vals:
                # 定义方程: left_side = rhs
                def equation(theta_ddot):
                    return self.left_side(r_ddot, alpha_rad, theta_ddot, phi_i) - self.rhs
                
                # 在theta范围内寻找根
                theta_test = np.linspace(theta_ddot_range[0], theta_ddot_range[1], 1000)
                sign_changes = []
                
                for k in range(len(theta_test)-1):
                    if equation(theta_test[k]) * equation(theta_test[k+1]) <= 0:
                        # 使用二分法找根
                        a, b = theta_test[k], theta_test[k+1]
                        for _ in range(50):
                            c = (a + b) / 2
                            if abs(equation(c)) < 1e-8:
                                sign_changes.append(c)
                                break
                            if equation(a) * equation(c) < 0:
                                b = c
                            else:
                                a = c
                        else:
                            sign_changes.append((a + b) / 2)
                
                for theta_ddot in sign_changes:
                    boundary_points.append((r_ddot, theta_ddot, phi_i))
        
        print(f"找到 {len(boundary_points)} 个边界点")
        return np.array(boundary_points) if boundary_points else np.array([])
    
    def multi_alpha_analysis(self, alpha_list=None, r_range=(-30, 30), 
                             theta_ddot_range=(-20, 20), resolution=300):
        """
        分析多个角度下的可行域变化
        
        参数:
        alpha_list: 要分析的角度列表（度数），如果为None则自动生成
        """
        if alpha_list is None:
            # 默认分析0°、45°、90°、135°、180°、225°、270°、315°
            alpha_list = [0, 45, 90, 135, 180, 225, 270, 315]
        
        print(f"\n{'='*60}")
        print("多角度对比分析")
        print(f"{'='*60}")
        print(f"分析角度: {alpha_list}")
        
        results = {}
        
        for alpha_deg in alpha_list:
            print(f"\n--- 分析 α = {alpha_deg}° ---")
            feasible_points, _, _, _ = self.solve_for_fixed_alpha(
                alpha_deg, r_range, theta_ddot_range, resolution
            )
            
            if len(feasible_points) > 0:
                stats = self.analyze_fixed_alpha_results(
                    feasible_points, alpha_deg, r_range, theta_ddot_range
                )
                results[alpha_deg] = {
                    'stats': stats,
                    'points': feasible_points
                }
            else:
                print(f"  α = {alpha_deg}° 时无可行解")
                results[alpha_deg] = None
        
        # 生成对比报告
        self.generate_comparison_report(results, alpha_list)
        
        return results
    
    def generate_comparison_report(self, results, alpha_list):
        """生成多角度对比报告"""
        print(f"\n{'='*60}")
        print("多角度对比报告")
        print(f"{'='*60}")
        
        # 创建表格
        print(f"\n{'角度(°)':<10} {'可行点数':<12} {'r̈范围':<25} {'θ̈范围':<25} {'相关性强弱':<15}")
        print("-" * 90)
        
        for alpha_deg in alpha_list:
            if results[alpha_deg] is not None:
                stats = results[alpha_deg]['stats']
                r_range_str = f"[{stats['r_ddot_range'][0]:.2f}, {stats['r_ddot_range'][1]:.2f}]"
                theta_range_str = f"[{stats['theta_ddot_range'][0]:.2f}, {stats['theta_ddot_range'][1]:.2f}]"
                
                # 判断相关性 - 修复缩进问题
                if abs(stats['correlation']) > 0.7:
                    corr_str = "强相关"
                elif abs(stats['correlation']) > 0.3:
                    corr_str = "中等相关"
                else:
                    corr_str = "弱相关"
                
                print(f"{alpha_deg:<10} {stats['num_points']:<12} {r_range_str:<25} {theta_range_str:<25} {corr_str:<15}")
            else:
                print(f"{alpha_deg:<10} {'无可行解':<12} {'-':<25} {'-':<25} {'-':<15}")
        
        # 保存详细报告
        with open('alpha_analysis_report.txt', 'w') as f:
            f.write("多角度分析报告\n")
            f.write("="*60 + "\n\n")
            
            for alpha_deg in alpha_list:
                if results[alpha_deg] is not None:
                    stats = results[alpha_deg]['stats']
                    f.write(f"角度 α = {alpha_deg}°\n")
                    f.write(f"  - 可行点数: {stats['num_points']}\n")
                    f.write(f"  - r̈ 范围: [{stats['r_ddot_range'][0]:.4f}, {stats['r_ddot_range'][1]:.4f}]\n")
                    f.write(f"  - θ̈ 范围: [{stats['theta_ddot_range'][0]:.4f}, {stats['theta_ddot_range'][1]:.4f}]\n")
                    f.write(f"  - r̈ 平均值: {stats['r_ddot_mean']:.4f}\n")
                    f.write(f"  - θ̈ 平均值: {stats['theta_ddot_mean']:.4f}\n")
                    f.write(f"  - 相关系数: {stats['correlation']:.4f}\n")
                    f.write(f"  - 可行域面积: {stats['approx_area']:.2f}\n\n")
        
        print(f"\n详细报告已保存到 alpha_analysis_report.txt")

def main():
    print("="*60)
    print("高级求解器 - 支持固定角度求解模式")
    print("="*60)
    
    # 创建求解器
    solver = AdvancedSolver(
        m=15.680000000000003+26.238000000000003,    # 质量
        R=0.39597975,    # 半径
        J=0.81954133 + 0.2811737 + 4*0.00149103,    # 转动惯量
        mu=0.7,   # 摩擦系数
        g=9.81    # 重力加速度
    )
    
    print("\n请选择求解模式:")
    print("  1 - 固定单个角度，求解 (r̈, θ̈) 可行域")
    print("  2 - 多个角度对比分析")
    print("  3 - 交互式角度扫描")
    
    try:
        mode = int(input("\n请输入模式 (1/2/3) [默认: 1]: ") or "1")
    except:
        mode = 1
    
    if mode == 1:
        # 固定单个角度
        try:
            alpha_deg = float(input("请输入角度 α (度数) [默认: 45]: ") or "45")
        except:
            alpha_deg = 45.0
        
        # 可选：自定义搜索范围
        custom_range = input("是否自定义搜索范围？(y/n) [默认: n]: ").lower()
        if custom_range == 'y':
            try:
                r_min = float(input("r̈ 最小值 [默认: -30]: ") or "-30")
                r_max = float(input("r̈ 最大值 [默认: 30]: ") or "30")
                theta_min = float(input("θ̈ 最小值 [默认: -20]: ") or "-20")
                theta_max = float(input("θ̈ 最大值 [默认: 20]: ") or "20")
                r_range = (r_min, r_max)
                theta_ddot_range = (theta_min, theta_max)
            except:
                r_range = (-30, 30)
                theta_ddot_range = (-20, 20)
        else:
            r_range = (-30, 30)
            theta_ddot_range = (-20, 20)
        
        # 求解
        feasible_points, r_vals, theta_vals, constraint_values = solver.solve_for_fixed_alpha(
            alpha_deg, r_range, theta_ddot_range, resolution=500
        )
        
        if len(feasible_points) > 0:
            # 分析结果
            stats = solver.analyze_fixed_alpha_results(
                feasible_points, alpha_deg, r_range, theta_ddot_range
            )
            
            # 寻找边界点
            boundary_points = solver.find_boundary_for_fixed_alpha(
                alpha_deg, r_range, theta_ddot_range, resolution=500
            )
            
            # 保存结果
            np.savetxt(f'feasible_alpha_{alpha_deg}.csv', feasible_points, 
                      delimiter=',', header='r_ddot,theta_ddot', comments='')
            print(f"\n可行点已保存到 feasible_alpha_{alpha_deg}.csv")
            
            if len(boundary_points) > 0:
                np.savetxt(f'boundary_alpha_{alpha_deg}.csv', boundary_points, 
                          delimiter=',', header='r_ddot,theta_ddot,phi', comments='')
                print(f"边界点已保存到 boundary_alpha_{alpha_deg}.csv")
            
            # 输出边界方程近似
            print(f"\n{'='*60}")
            print("边界线近似方程")
            print(f"{'='*60}")
            print("提示：边界线由以下四个方程决定（对应四个φ方向）：")
            for i, phi_i in enumerate(solver.phi):
                phi_deg = phi_i * 180 / np.pi
                print(f"\nφ = {phi_deg:.0f}°:")
                print(f"  (m r̈ R cosα - J θ̈ sinφ)² + (m r̈ R sinα + J θ̈ cosφ)² = μ²m²g²R²")
            
        else:
            print("\n未找到可行解！建议：")
            print("  1. 尝试不同的角度值")
            print("  2. 增大搜索范围")
            print("  3. 调整系统参数（如摩擦系数）")
    
    elif mode == 2:
        # 多角度对比分析
        alpha_list_input = input("请输入角度列表（用逗号分隔，如：0,45,90,135）[默认: 0,45,90,135,180,225,270,315]: ")
        
        if alpha_list_input.strip():
            try:
                alpha_list = [float(a.strip()) for a in alpha_list_input.split(',')]
            except:
                alpha_list = [0, 45, 90, 135, 180, 225, 270, 315]
        else:
            alpha_list = [0, 45, 90, 135, 180, 225, 270, 315]
        
        results = solver.multi_alpha_analysis(
            alpha_list, 
            r_range=(-30, 30),
            theta_ddot_range=(-20, 20),
            resolution=300
        )
    
    elif mode == 3:
        # 交互式角度扫描
        print("\n交互式角度扫描模式")
        print("输入角度值，实时查看结果（输入 'q' 退出）")
        
        while True:
            try:
                user_input = input(f"\n请输入角度 α (度数) [当前参数: m={solver.m}, μ={solver.mu}]: ")
                if user_input.lower() == 'q':
                    break
                
                alpha_deg = float(user_input)
                
                # 快速求解
                feasible_points, _, _, _ = solver.solve_for_fixed_alpha(
                    alpha_deg, (-30, 30), (-20, 20), resolution=300
                )
                
                if len(feasible_points) > 0:
                    r_ddot_vals = feasible_points[:, 0]
                    theta_ddot_vals = feasible_points[:, 1]
                    
                    print(f"\n结果 (α = {alpha_deg}°):")
                    print(f"  可行点数: {len(feasible_points)}")
                    print(f"  r̈ 范围: [{np.min(r_ddot_vals):.2f}, {np.max(r_ddot_vals):.2f}]")
                    print(f"  θ̈ 范围: [{np.min(theta_ddot_vals):.2f}, {np.max(theta_ddot_vals):.2f}]")
                    
                    # 询问是否保存
                    save = input("是否保存结果？(y/n): ").lower()
                    if save == 'y':
                        np.savetxt(f'feasible_alpha_{alpha_deg}.csv', feasible_points, 
                                  delimiter=',', header='r_ddot,theta_ddot', comments='')
                        print(f"已保存到 feasible_alpha_{alpha_deg}.csv")
                else:
                    print(f"α = {alpha_deg}° 时无可行解")
                    
            except ValueError:
                print("请输入有效的数字！")
            except KeyboardInterrupt:
                break
    
    print("\n" + "="*60)
    print("计算完成！")
    print("="*60)

if __name__ == "__main__":
    main()