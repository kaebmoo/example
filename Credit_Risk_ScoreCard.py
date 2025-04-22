# Import required libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import scorecardpy as sc
import seaborn as sns
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def compare_models(X_train, X_test, y_train, y_test, feature_names):
    """เปรียบเทียบประสิทธิภาพของโมเดลต่างๆ"""
    models = {
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'Random Forest': RandomForestClassifier(
            n_estimators=200, 
            max_depth=5,
            random_state=42
        ),
        'XGBoost': XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
    }
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    results = {}
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Train model
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        y_prob = model.predict_proba(X_test_scaled)[:, 1]
        
        # Get feature importance
        if name == 'Logistic Regression':
            importance = pd.DataFrame({
                'feature': feature_names,
                'importance': abs(model.coef_[0])
            })
        else:
            importance = pd.DataFrame({
                'feature': feature_names,
                'importance': model.feature_importances_
            })
        
        importance = importance.sort_values('importance', ascending=False)
        
        # Store results
        results[name] = {
            'auc': roc_auc_score(y_test, y_prob),
            'report': classification_report(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'model': model,
            'probabilities': y_prob,
            'feature_importance': importance
        }
        
        # Print results
        print(f"\n{name} Results:")
        print(f"AUC Score: {results[name]['auc']:.4f}")
        print("\nClassification Report:")
        print(results[name]['report'])
        print("\nConfusion Matrix:")
        print(results[name]['confusion_matrix'])
        print("\nTop 5 Important Features:")
        print(results[name]['feature_importance'].head())
    
    return results

def plot_model_comparison(results, X_test, y_test):
    """แสดงกราฟเปรียบเทียบโมเดล"""
    # 1. ROC Curves
    plt.figure(figsize=(10, 6))
    for name, result in results.items():
        fpr, tpr, _ = roc_curve(y_test, result['probabilities'])
        plt.plot(fpr, tpr, label=f'{name} (AUC = {result["auc"]:.3f})')
    
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves Comparison')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # 2. Feature Importance Comparison
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    
    for i, (name, result) in enumerate(results.items()):
        importance = result['feature_importance'].head(10)
        sns.barplot(data=importance, x='importance', y='feature', ax=axes[i])
        axes[i].set_title(f'{name} Feature Importance')
    
    plt.tight_layout()
    plt.show()
    
    # 3. Model Performance Comparison
    metrics = pd.DataFrame({
        'Model': list(results.keys()),
        'AUC': [result['auc'] for result in results.values()]
    })
    
    plt.figure(figsize=(8, 5))
    sns.barplot(data=metrics, x='Model', y='AUC')
    plt.title('Model AUC Comparison')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def analyze_score_ranges(test_scores):
    """วิเคราะห์ช่วงคะแนนและความเสี่ยง"""
    # สร้างช่วงคะแนน
    test_scores['score_range'] = pd.qcut(test_scores['score'], q=5, 
                                       labels=['Very High Risk', 'High Risk', 
                                              'Medium Risk', 'Low Risk', 
                                              'Very Low Risk'])
    
    # วิเคราะห์อัตราการผิดนัดชำระในแต่ละช่วงคะแนน
    risk_analysis = test_scores.groupby('score_range').agg({
        'SeriousDlqin2yrs': ['count', 'mean'],
        'score': ['min', 'max', 'mean']
    }).round(2)
    
    print("\nRisk Analysis by Score Range:")
    print(risk_analysis)
    
    return risk_analysis

def plot_feature_importance(bins):
    """แสดงความสำคัญของตัวแปรจาก Information Value"""
    feature_iv = {}
    for var in bins.keys():
        total_iv = bins[var]['bin_iv'].sum()
        feature_iv[var] = total_iv
    
    iv_df = pd.DataFrame.from_dict(feature_iv, orient='index', columns=['IV'])
    iv_df = iv_df.sort_values('IV', ascending=False)
    
    print("\nFeature Importance by Information Value:")
    print(iv_df)
    
    # Plot feature importance
    plt.figure(figsize=(12, 6))
    sns.barplot(data=iv_df.reset_index(), x='index', y='IV')
    plt.title('Feature Importance (Information Value)')
    plt.xlabel('Features')
    plt.ylabel('Information Value')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
    
    return iv_df

def plot_score_distributions(test_scores):
    """แสดงการกระจายของคะแนนและ ROC curve"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Score Distribution
    sns.histplot(data=test_scores, x='score', hue='SeriousDlqin2yrs', 
                bins=50, ax=ax1)
    ax1.set_title('Distribution of Credit Scores by Risk Group')
    ax1.set_xlabel('Score')
    ax1.set_ylabel('Count')
    
    # ROC Curve
    fpr, tpr, _ = roc_curve(test_scores['SeriousDlqin2yrs'], 
                           test_scores['score'])
    auc = roc_auc_score(test_scores['SeriousDlqin2yrs'], 
                        test_scores['score'])
    
    ax2.plot(fpr, tpr, label=f'AUC = {auc:.3f}')
    ax2.plot([0, 1], [0, 1], 'k--')
    ax2.set_title('ROC Curve')
    ax2.set_xlabel('False Positive Rate')
    ax2.set_ylabel('True Positive Rate')
    ax2.legend()
    
    plt.tight_layout()
    plt.show()

def print_scorecard_rules(card):
    """แสดงรายละเอียดของ scorecard rules"""
    print("\nScorecard Rules:")
    
    # ตรวจสอบและแสดงค่าพื้นฐาน
    if 'basepoints' in card:
        print(f"Base Points: {card['basepoints']}")
    
    # แสดงรายละเอียดของแต่ละตัวแปร
    total_rules = []
    for var in card.keys():
        if isinstance(card[var], pd.DataFrame):
            print(f"\nVariable: {var}")
            print("Binning Rules:")
            rules = card[var].copy()
            # ปรับการแสดงผลตามคอลัมน์ที่มีอยู่จริง
            print(rules.to_string(index=False))
            
            # เก็บข้อมูลสำหรับสรุป
            total_rules.append({
                'variable': var,
                'points_min': rules['points'].min() if 'points' in rules.columns else 0,
                'points_max': rules['points'].max() if 'points' in rules.columns else 0
            })
    
    # แสดงสรุป
    print("\nScore Summary:")
    summary_df = pd.DataFrame(total_rules)
    if not summary_df.empty:
        print("Points range for each variable:")
        for _, row in summary_df.iterrows():
            print(f"{row['variable']}: {row['points_min']} to {row['points_max']} points")

def create_scorecard():
    """สร้าง scorecard และเปรียบเทียบโมเดล"""
    # 1. โหลดข้อมูล
    print("Loading data...")
    data = pd.read_csv('./Credit data.csv')
    
    # 2. เตรียมชื่อคอลัมน์
    target = 'SeriousDlqin2yrs'
    
    # 3. สร้าง information value
    print("\nCalculating Information Value...")
    iv = sc.iv(data, y=target)
    print("\nInformation Values:")
    print(iv)
    
    # 4. ทำ Binning
    print("\nPerforming variable binning...")
    bins = sc.woebin(data, y=target)
    
    # 5. แบ่งข้อมูล train/test
    train, test = train_test_split(data, test_size=0.3, random_state=42)
    
    # 6. แปลงข้อมูลด้วย WOE
    train_woe = sc.woebin_ply(train, bins)
    test_woe = sc.woebin_ply(test, bins)
    
    # 7. เตรียมข้อมูลสำหรับโมเดล
    y_train = train_woe[target]
    X_train = train_woe.drop([target], axis=1)
    y_test = test_woe[target]
    X_test = test_woe.drop([target], axis=1)
    
    # 8. เปรียบเทียบโมเดล
    print("\nComparing different models...")
    model_results = compare_models(X_train, X_test, y_train, y_test, X_train.columns)
    plot_model_comparison(model_results, X_test, y_test)
    
    # 9. สร้าง scorecard จาก LogisticRegression
    print("\nCreating scorecard with Logistic Regression...")
    lr = model_results['Logistic Regression']['model']  # ใช้โมเดลที่ train แล้วจาก compare_models
    card = sc.scorecard(bins=bins, model=lr, xcolumns=X_train.columns)
    
    # 10. คำนวณ scores
    print("\nCalculating credit scores...")
    train_scores = sc.scorecard_ply(train, card, only_total_score=False)
    test_scores = sc.scorecard_ply(test, card, only_total_score=False)
    
    # เพิ่ม target column
    train_scores[target] = train[target]
    test_scores[target] = test[target]
    
    # 11. ประเมินผล scorecard
    print("\nScorecard Performance:")
    train_perf = sc.perf_eva(train_scores[target], train_scores['score'])
    test_perf = sc.perf_eva(test_scores[target], test_scores['score'])
    
    # 12. เก็บผลการประเมิน scorecard ไว้ใน results
    scorecard_results = {
        'train_performance': train_perf,
        'test_performance': test_perf,
        'score_distribution': {
            'train': train_scores['score'].describe(),
            'test': test_scores['score'].describe()
        }
    }
    
    return bins, card, train_scores, test_scores, model_results, scorecard_results

def main():
    """ฟังก์ชันหลักสำหรับรันการวิเคราะห์ทั้งหมด"""
    # สร้าง scorecard และคำนวณ scores
    bins, card, train_scores, test_scores, model_results, scorecard_results = create_scorecard()
    
    # แสดงผลการวิเคราะห์
    
    # 1. แสดงการเปรียบเทียบโมเดล
    print("\nModel Comparison Summary:")
    for name, result in model_results.items():
        print(f"\n{name}:")
        print(f"AUC Score: {result['auc']:.4f}")
        print("\nTop 5 Important Features:")
        print(result['feature_importance'].head())
    
    # 2. แสดงผลการวิเคราะห์ความเสี่ยง
    risk_analysis = analyze_score_ranges(test_scores)
    
    # 3. แสดงความสำคัญของตัวแปร
    feature_importance = plot_feature_importance(bins)
    
    # 4. แสดงการกระจายของคะแนน
    plot_score_distributions(test_scores)
    
    # 5. แสดง scorecard rules
    print_scorecard_rules(card)
    
    # 6. แสดงผลการประเมิน scorecard
    print("\nScorecard Performance Summary:")
    print("\nScore Distribution (Test Set):")
    print(scorecard_results['score_distribution']['test'])

if __name__ == "__main__":
    main()