# นำเข้าไลบรารีที่จำเป็น
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report

# โหลดข้อมูลตัวอย่าง (เช่น Iris dataset)
data = load_iris()
X = data.data
y = data.target

# ปรับขนาดข้อมูลให้มีค่าเฉลี่ยเป็น 0 และความแปรปรวนเป็น 1
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# สร้าง PCA และปรับข้อมูลให้มีมิติใหม่
pca = PCA(n_components=2)  # ลดมิติข้อมูลเหลือ 2 มิติ
X_pca = pca.fit_transform(X_scaled)

# แบ่งข้อมูลเป็นชุดฝึกอบรมและชุดทดสอบ
X_train, X_test, y_train, y_test = train_test_split(X_pca, y, test_size=0.3, random_state=42)

# สร้างโมเดลการจำแนกประเภทด้วย K-Nearest Neighbors
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)

# ทำนายผลลัพธ์
y_pred = knn.predict(X_test)

# วัดประสิทธิภาพของโมเดล
accuracy = accuracy_score(y_test, y_pred)
class_report = classification_report(y_test, y_pred)

print(f"Accuracy: {accuracy}")
print("Classification Report:")
print(class_report)
