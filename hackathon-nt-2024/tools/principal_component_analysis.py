 # นำเข้าไลบรารีที่จำเป็น
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# โหลดข้อมูลตัวอย่าง (เช่น Iris dataset)
data = load_iris()
print(data)
X = data.data
y = data.target
print(X)
print(y)


# ปรับขนาดข้อมูลให้มีค่าเฉลี่ยเป็น 0 และความแปรปรวนเป็น 1
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# สร้าง PCA และปรับข้อมูลให้มีมิติใหม่
pca = PCA(n_components=2)  # ลดมิติข้อมูลเหลือ 2 มิติ
X_pca = pca.fit_transform(X_scaled)

# แสดงผลลัพธ์ของ PCA
print("อธิบายความแปรปรวนของ PCA: ", pca.explained_variance_ratio_)
print("อธิบายความแปรปรวนสะสม: ", np.cumsum(pca.explained_variance_ratio_))

# สร้างกราฟแสดงผลลัพธ์ PCA
plt.figure(figsize=(8, 6))
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap='viridis', edgecolor='k', s=150)
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('PCA of Iris Dataset')
plt.colorbar()
plt.show()
