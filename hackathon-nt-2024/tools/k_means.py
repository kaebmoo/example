# การหาค่า k ที่เหมาะสม

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler

# โหลดข้อมูล Iris dataset
data = load_iris()
X = data.data

# ปรับขนาดข้อมูลให้มีค่าเฉลี่ยเป็น 0 และความแปรปรวนเป็น 1
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


#  Elbow method
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# คำนวณค่า distortion สำหรับ k ตั้งแต่ 1 ถึง 10
distortions = []
K = range(1, 11)

for k in K:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X_scaled)
    distortions.append(kmeans.inertia_)

# สร้างกราฟ Elbow
plt.figure(figsize=(10, 6))
plt.plot(K, distortions, 'bx-')
plt.xlabel('Number of clusters (k)')
plt.ylabel('Distortion')
plt.title('The Elbow Method showing the optimal k')
plt.show()
'''
กราฟ Elbow ที่ได้จะช่วยให้เราหาค่า kk ที่เหมาะสมได้ โดยดูจากจุดที่ค่าความบิดเบี้ยว (distortion) 
เริ่มลดลงอย่างช้าๆ หรือเป็นจุดที่เกิดการ "หักศอก" (elbow point)
'''

from sklearn.metrics import silhouette_score

# คำนวณค่า silhouette score สำหรับ k ตั้งแต่ 2 ถึง 10
silhouette_scores = []

for k in range(2, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X_scaled)
    score = silhouette_score(X_scaled, kmeans.labels_)
    silhouette_scores.append(score)

# สร้างกราฟ Silhouette Score
plt.figure(figsize=(10, 6))
plt.plot(range(2, 11), silhouette_scores, 'bx-')
plt.xlabel('Number of clusters (k)')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Score for optimal k')
plt.show()

'''
กราฟ Silhouette Score ที่ได้จะช่วยให้เราหาค่า kk ที่เหมาะสมได้ โดยค่าที่มี Silhouette Score สูงที่สุดจะเป็นค่าที่เหมาะสมสำหรับ k
'''

from sklearn.cluster import KMeans

# กำหนดจำนวนกลุ่ม (k) ที่ต้องการ
k = 3
kmeans = KMeans(n_clusters=k, random_state=42)
kmeans.fit(X_scaled)

# เพิ่มผลลัพธ์การทำ KMeans ลงใน DataFrame
labels = kmeans.labels_
data_with_labels = pd.DataFrame(X_scaled, columns=data.feature_names)
data_with_labels['Cluster'] = labels
print(data_with_labels)

from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# ใช้ PCA เพื่อลดมิติข้อมูลเหลือ 2 มิติ
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# เพิ่มผลลัพธ์ PCA ลงใน DataFrame
data_with_labels['PCA1'] = X_pca[:, 0]
data_with_labels['PCA2'] = X_pca[:, 1]

# สร้างกราฟแสดงผลลัพธ์ KMeans clustering
plt.figure(figsize=(10, 6))
for cluster in range(k):
    cluster_data = data_with_labels[data_with_labels['Cluster'] == cluster]
    plt.scatter(cluster_data['PCA1'], cluster_data['PCA2'], label=f'Cluster {cluster}')

# แสดงจุดศูนย์กลาง (Centroids)
centroids = kmeans.cluster_centers_
centroids_pca = pca.transform(centroids)
plt.scatter(centroids_pca[:, 0], centroids_pca[:, 1], s=300, c='red', label='Centroids', marker='X')

plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('KMeans Clustering of Iris Dataset (2D PCA Projection)')
plt.legend()
plt.show()
