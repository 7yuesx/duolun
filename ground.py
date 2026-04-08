import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# 地形参数
width = 512    # X方向长度 (对应MuJoCo的ncol)
height = 64    # Y方向宽度 (对应MuJoCo的nrow，窄一些更像道路)
frequency = 0.12   # 正弦波频率 (控制减速带间距)
amplitude = 80     # 起伏幅度 (灰度值偏移，0-255)
center_gray = 128  # 基准灰度

# 创建网格 (注意：X方向是减速带延伸方向，Y方向是减速带排列方向)
x = np.linspace(0, 2 * np.pi / frequency, width)   # 减速带排列方向
y = np.linspace(0, 1, height)                      # 宽度方向，保持不变

X, Y = np.meshgrid(x, y)

# 只在X方向产生正弦波，Y方向不变 -> 形成条状减速带
Z = amplitude * np.sin(X) + center_gray
Z = np.clip(Z, 0, 255).astype(np.uint8)

# 保存为灰度图
img = Image.fromarray(Z, mode='L')
img.save("speed_bump_terrain.png")

# 可视化（不包含3D部分）
plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
plt.imshow(Z, cmap='gray', aspect='auto', origin='lower')
plt.colorbar(label='高度')
plt.title('减速带地形俯视图\n(条纹 = 减速带)')
plt.xlabel('X (运动方向)')
plt.ylabel('Y (宽度)')

plt.subplot(2, 2, 2)
# 显示中心线的剖面
plt.plot(Z[height//2, :], 'b-', linewidth=1.5)
plt.title('沿运动方向的剖面 (中心线)')
plt.xlabel('X 像素')
plt.ylabel('灰度值 (0-255)')
plt.grid(True, alpha=0.3)

plt.subplot(2, 2, 3)
# 显示多条剖面线
for i in range(0, height, height//4):
    plt.plot(Z[i, :], alpha=0.7, label=f'Y={i}')

plt.title('不同宽度位置的剖面')
plt.xlabel('X 像素')
plt.ylabel('灰度值 (0-255)')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(2, 2, 4)
# 显示单条减速带的形状
one_bump = Z[height//2, :int(width/frequency/2)]
plt.plot(one_bump, 'r-', linewidth=2)
plt.title('单个减速带剖面形状')
plt.xlabel('X 像素')
plt.ylabel('灰度值 (0-255)')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("terrain_visualization.png", dpi=150)
plt.show()

print("地形图已生成: speed_bump_terrain.png")
print(f"图像尺寸: {width}x{height} 像素")
print(f"减速带数量: ~{int(width * frequency / (2*np.pi))} 个")
print(f"灰度范围: {Z.min()} - {Z.max()}")
print(f"减速带高度: {amplitude*2/255 * 100:.1f}% 最大高度范围")