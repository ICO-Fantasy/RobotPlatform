import matplotlib.pyplot as plt
import numpy as np


def biased_sampling(n, alpha=2, beta=5):
    """
    使用 Beta 分布生成偏向 180 度的采样点。
    :param n: 生成的采样点数量
    :param alpha: Beta 分布的 alpha 参数，用来调整分布形状
    :param beta: Beta 分布的 beta 参数，用来调整分布形状
    :return: 生成的采样点列表
    """
    # 生成符合 Beta 分布的样本，范围为 [0, 1]
    samples = np.random.beta(alpha, beta, n)

    # 将范围 [0, 1] 转换为 [0, 180] 度的角度
    angles = samples * 180

    return angles


# 生成 1000 个符合偏向 180 度的角度
angles = biased_sampling(1000, alpha=5, beta=2)

# 使用概率密度采样，而不是均匀采样
num_samples = 6
# 从生成的角度数据中随机选择 num_samples 个点，概率密度决定采样概率
sampled_angles = np.random.choice(angles, num_samples, replace=False)

# 绘制所有角度的分布
plt.scatter(angles, np.zeros_like(angles), color="blue", alpha=0.5, label="Generated Angles")

# 绘制采样点
plt.scatter(
    sampled_angles, np.zeros_like(sampled_angles), color="red", marker="x", label="Sampled Angles"
)

# 只显示角度值，不显示 y 轴
plt.yticks([])
plt.xlabel("Angle (degrees)")
plt.title("Biased Sampling with More Points Near 180 Degrees")
plt.legend()
plt.show()
