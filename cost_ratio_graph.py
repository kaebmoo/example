from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

# Define the range for Utilization and Ratio
utilization = np.linspace(0.01, 1.0, 100)  # Avoid division by zero
ratios = np.arange(1, 20)

# Create a plot
plt.figure(figsize=(12, 8))

# Plot cost curves for each Ratio
for ratio in ratios:
    cost = 22.56 / (utilization * (1 + ratio))
    plt.plot(utilization * 100, cost, label=f'Ratio = {ratio}')

# Plot settings
plt.title('Cost vs Utilization for Different Ratios')
plt.xlabel('Utilization (%)')
plt.ylabel('Cost')
plt.legend(title='Ratio')
plt.grid(True)
plt.tight_layout()

plt.show()

# Create a meshgrid for Utilization and Ratio
U, R = np.meshgrid(utilization, ratios)
C = 22.56 / (U * (1 + R))

# Create 3D plot
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Surface plot
surf = ax.plot_surface(U * 100, R, C, cmap='viridis', edgecolor='none')

# Labels and title
ax.set_title('3D Surface Plot of Cost vs Utilization and Ratio')
ax.set_xlabel('Utilization (%)')
ax.set_ylabel('Ratio')
ax.set_zlabel('Cost')

# Add color bar
fig.colorbar(surf, shrink=0.5, aspect=10)

plt.tight_layout()
plt.show()
