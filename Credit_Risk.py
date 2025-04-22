import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler, PowerTransformer
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, roc_curve, precision_recall_curve
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE, ADASYN
from imblearn.under_sampling import TomekLinks
from imblearn.combine import SMOTETomek, SMOTEENN
from imblearn.pipeline import Pipeline as ImbPipeline

def check_missing_values(data):
    """ตรวจสอบและแสดงข้อมูล missing values"""
    missing = data.isnull().sum()
    missing_percent = (missing / len(data)) * 100
    missing_info = pd.DataFrame({
        'Missing Values': missing,
        'Percent Missing': missing_percent
    })
    print("\nMissing Value Analysis:")
    print(missing_info[missing_info['Missing Values'] > 0])
    return missing_info

def create_advanced_features(data):
    """เพิ่ม Feature Engineering ที่ซับซ้อนขึ้น"""
    data = data.copy()
    
    # 1. จัดการ missing values ก่อน feature engineering
    imputer = SimpleImputer(strategy='median')
    numerical_columns = data.select_dtypes(include=['float64', 'int64']).columns
    data[numerical_columns] = imputer.fit_transform(data[numerical_columns])
    
    # 2. Risk Scores
    data['risk_score'] = (
        data['RevolvingUtilizationOfUnsecuredLines'] * 0.3 +
        data['NumberOfTime30-59DaysPastDueNotWorse'] * 0.2 +
        data['NumberOfTime60-89DaysPastDueNotWorse'] * 0.2 +
        data['NumberOfTimes90DaysLate'] * 0.3
    )
    
    # 3. Interaction Features
    data['debt_per_income'] = data['DebtRatio'] * data['MonthlyIncome']
    data['util_per_income'] = data['RevolvingUtilizationOfUnsecuredLines'] * data['MonthlyIncome']
    
    # 4. Ratio Features
    data['income_per_credit_line'] = data['MonthlyIncome'] / (data['NumberOfOpenCreditLinesAndLoans'] + 1)
    data['debt_per_credit_line'] = data['DebtRatio'] / (data['NumberOfOpenCreditLinesAndLoans'] + 1)
    
    # 5. Complex Features
    data['delinquency_ratio'] = (
        (data['NumberOfTime30-59DaysPastDueNotWorse'] + 
         data['NumberOfTime60-89DaysPastDueNotWorse'] * 2 + 
         data['NumberOfTimes90DaysLate'] * 3) / 
        (data['age'] * data['NumberOfOpenCreditLinesAndLoans'] + 1)
    )
    
    # 6. Binning Features
    data['age_group'] = pd.qcut(data['age'], q=5, labels=['VeryYoung', 'Young', 'Middle', 'Senior', 'Elderly'])
    data['income_group'] = pd.qcut(data['MonthlyIncome'], q=5, labels=['VeryLow', 'Low', 'Medium', 'High', 'VeryHigh'])
    
    # 7. Log Transforms for Skewed Features
    for col in ['MonthlyIncome', 'DebtRatio', 'RevolvingUtilizationOfUnsecuredLines']:
        data[f'log_{col}'] = np.log1p(data[col])
    
    return data

def prepare_features(data):
    """เตรียม features และจัดการ missing values"""
    # 1. แยก features และ target
    X = data.drop('SeriousDlqin2yrs', axis=1)
    y = data['SeriousDlqin2yrs']
    
    # 2. แยก numerical และ categorical columns
    categorical_cols = X.select_dtypes(include=['object', 'category']).columns
    numerical_cols = X.select_dtypes(include=['float64', 'int64']).columns
    
    # 3. สร้าง pipeline สำหรับ preprocessing
    preprocessor = ImbPipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # 4. Encode categorical variables
    le = LabelEncoder()
    for col in categorical_cols:
        X[col] = le.fit_transform(X[col])
    
    return X, y

def find_optimal_threshold(y_true, y_prob, criterion='balanced'):
    """หา Threshold ที่เหมาะสมตามเกณฑ์ที่กำหนด"""
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    
    if criterion == 'balanced':
        precision, recall, pr_thresholds = precision_recall_curve(y_true, y_prob)
        # ป้องกันการหารด้วย 0
        denominator = (precision + recall)
        denominator[denominator == 0] = 1e-10  # ใส่ค่าเล็กๆ แทนการหารด้วย 0
        f1_scores = 2 * (precision * recall) / denominator
        optimal_idx = np.argmax(f1_scores[:-1])  # ตัด point สุดท้ายออก
        return pr_thresholds[optimal_idx]
    
    elif criterion == 'cost_sensitive':
        costs = (1 - tpr) * 5 + fpr
        return thresholds[np.argmin(costs)]
    
    elif criterion == 'high_precision':
        precision, recall, pr_thresholds = precision_recall_curve(y_true, y_prob)
        # ปรับการคำนวณให้ถูกต้องตามขนาดของ arrays
        precision = precision[:-1]  # ตัด point สุดท้ายออกเพื่อให้ขนาดตรงกับ pr_thresholds
        recall = recall[:-1]
        suitable_precision_mask = precision >= 0.5
        
        if suitable_precision_mask.any():
            max_recall_idx = np.argmax(recall[suitable_precision_mask])
            selected_thresholds = pr_thresholds[suitable_precision_mask]
            if len(selected_thresholds) > max_recall_idx:
                return selected_thresholds[max_recall_idx]
    
    return 0.5

def evaluate_model(model, X_test, y_test):
    """ประเมินโมเดลด้วย threshold ต่างๆ"""
    y_prob = model.predict_proba(X_test)[:, 1]
    
    # ทดสอบแต่ละ threshold และเก็บผลลัพธ์
    thresholds = {
        'Default (0.5)': 0.5,
        'Balanced': find_optimal_threshold(y_test, y_prob, 'balanced'),
        'Cost Sensitive': find_optimal_threshold(y_test, y_prob, 'cost_sensitive')
    }
    
    # ลองหา high precision threshold ถ้าเป็นไปได้
    high_precision_threshold = find_optimal_threshold(y_test, y_prob, 'high_precision')
    if high_precision_threshold != 0.5:  # ถ้าหาค่าที่เหมาะสมได้
        thresholds['High Precision'] = high_precision_threshold
    
    # แสดงผลสำหรับแต่ละ threshold
    for name, threshold in thresholds.items():
        print(f"\n{name} Threshold ({threshold:.3f}):")
        y_pred = (y_prob >= threshold).astype(int)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        # คำนวณและแสดง metrics เพิ่มเติม
        conf_matrix = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = conf_matrix.ravel()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        print("\nAdditional Metrics:")
        print(f"Precision (Positive Predictive Value): {precision:.3f}")
        print(f"Recall (Sensitivity): {recall:.3f}")
        print(f"Specificity: {specificity:.3f}")
        print(f"False Positive Rate: {1 - specificity:.3f}")
        print(f"False Negative Rate: {1 - recall:.3f}")
        
def main():
    # 1. โหลดข้อมูล
    print("Loading data...")
    data = pd.read_csv('/Users/seal/Downloads/Credit data.csv')
    
    # 2. ตรวจสอบ missing values
    missing_info = check_missing_values(data)
    
    # 3. Feature Engineering
    print("\nPerforming feature engineering...")
    data = create_advanced_features(data)
    
    # 4. เตรียม features และ target
    print("\nPreparing features...")
    X, y = prepare_features(data)
    
    # 5. แบ่งข้อมูล
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # 6. สร้างและ train โมเดล
    print("\nTraining model...")
    model = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42)
    
    # 7. ใช้ SMOTE หลังจาก scaling
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    
    # 8. Train model
    model.fit(X_train_resampled, y_train_resampled)
    
    # 9. ประเมินผล
    print("\nEvaluating model...")
    evaluate_model(model, X_test, y_test)

if __name__ == "__main__":
    main()