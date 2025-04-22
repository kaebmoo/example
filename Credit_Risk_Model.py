# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, roc_curve
from sklearn.impute import SimpleImputer
import scorecardpy as sc
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)


def visualize_distributions(df):
    """
    Visualize distributions of variables in multiple plots
    """
    print("\nVisualizing Data Distributions")
    print("-" * 50)
    
    # 1. Target Variable Distribution
    plt.figure(figsize=(10, 5))
    sns.countplot(data=df, x='SeriousDlqin2yrs')
    plt.title('Distribution of Target Variable (SeriousDlqin2yrs)')
    plt.show()
    
    # 2. Continuous Variables
    continuous_vars = ['RevolvingUtilizationOfUnsecuredLines', 'age', 'DebtRatio', 'MonthlyIncome']
    plt.figure(figsize=(15, 10))
    for i, col in enumerate(continuous_vars, 1):
        plt.subplot(2, 2, i)
        sns.histplot(data=df, x=col, bins=30)
        plt.title(f'Distribution of {col}')
    plt.tight_layout()
    plt.show()
    
    # 3. Integer Variables (Counts)
    count_vars = ['NumberOfTime30-59DaysPastDueNotWorse', 'NumberOfOpenCreditLinesAndLoans',
                 'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines',
                 'NumberOfTime60-89DaysPastDueNotWorse', 'NumberOfDependents']
    plt.figure(figsize=(15, 10))
    for i, col in enumerate(count_vars, 1):
        plt.subplot(2, 3, i)
        sns.countplot(data=df, x=col)
        plt.title(f'Distribution of {col}')
        plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    # 4. Box plots for continuous variables by target
    plt.figure(figsize=(15, 10))
    for i, col in enumerate(continuous_vars, 1):
        plt.subplot(2, 2, i)
        sns.boxplot(data=df, x='SeriousDlqin2yrs', y=col)
        plt.title(f'{col} by Target')
    plt.tight_layout()
    plt.show()

def analyze_correlations(df):
    """
    Analyze and visualize correlations between variables
    """
    print("\nAnalyzing Correlations")
    print("-" * 50)
    
    # Calculate correlations
    corr = df.corr()
    
    # Plot correlation heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0)
    plt.title('Correlation Matrix')
    plt.show()
    
    # Print strongest correlations with target
    target_corr = corr['SeriousDlqin2yrs'].sort_values(ascending=False)
    print("\nCorrelations with Target Variable:")
    print(target_corr)

def analyze_risk_patterns(df):
    """
    Analyze risk patterns in different variable ranges
    """
    print("\nAnalyzing Risk Patterns")
    print("-" * 50)
    
    # Calculate default rates by age groups
    df['age_group'] = pd.qcut(df['age'], q=5)
    age_risk = df.groupby('age_group')['SeriousDlqin2yrs'].agg(['mean', 'count'])
    print("\nDefault Rates by Age Group:")
    print(age_risk)
    
    # Calculate default rates by income groups
    df['income_group'] = pd.qcut(df['MonthlyIncome'].fillna(df['MonthlyIncome'].median()), q=5)
    income_risk = df.groupby('income_group')['SeriousDlqin2yrs'].agg(['mean', 'count'])
    print("\nDefault Rates by Income Group:")
    print(income_risk)
    
    # Plot default rates
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    age_risk['mean'].plot(kind='bar', ax=ax1)
    ax1.set_title('Default Rate by Age Group')
    ax1.set_ylabel('Default Rate')
    
    income_risk['mean'].plot(kind='bar', ax=ax2)
    ax2.set_title('Default Rate by Income Group')
    ax2.set_ylabel('Default Rate')
    
    plt.tight_layout()
    plt.show()

def load_and_explore_data():
    """
    Load and explore data with comprehensive analysis
    """
    # Load data
    print("Loading and Exploring Data")
    print("-" * 50)
    df = pd.read_csv('Credit data.csv')
    
    # Basic information
    print("\nData Shape:", df.shape)
    print("\nData Types:")
    print(df.dtypes)
    
    # Missing values analysis
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    print("\nMissing Values Analysis:")
    missing_df = pd.DataFrame({
        'Missing Values': missing,
        'Percentage': missing_pct
    }).sort_values('Percentage', ascending=False)
    print(missing_df[missing_df['Missing Values'] > 0])
    
    # Basic statistics
    print("\nBasic Statistics:")
    print(df.describe())
    
    # Visualize distributions
    visualize_distributions(df)
    
    # Analyze correlations
    analyze_correlations(df)
    
    # Analyze risk patterns
    analyze_risk_patterns(df)
    
    return df

def handle_missing_and_outliers(df):
    """
    Handle missing values and outliers
    """
    print("\n2. Missing Value Handling and Outlier Treatment")
    print("-" * 50)
    
    # Handle missing values
    df['MonthlyIncome'] = df['MonthlyIncome'].fillna(df['MonthlyIncome'].median())
    df['NumberOfDependents'] = df['NumberOfDependents'].fillna(0)
    
    # Outlier analysis and treatment using IQR method
    for col in df.select_dtypes(include=['float64', 'int64']).columns:
        if col != 'SeriousDlqin2yrs':
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            upper = Q3 + 1.5 * IQR
            lower = Q1 - 1.5 * IQR
            
            print(f"\nOutliers in {col}:")
            print(f"Number of outliers: {len(df[(df[col] > upper) | (df[col] < lower)])}")
            
            # Cap outliers
            df[col] = df[col].clip(lower=lower, upper=upper)
    
    return df

def create_scorecard_features(df):
    """
    Create scorecard features including WOE transformation
    """
    print("\n3. Feature Engineering and WOE Transformation")
    print("-" * 50)
    
    # ลบคอลัมน์ที่สร้างจาก risk patterns analysis
    if 'age_group' in df.columns:
        df = df.drop(['age_group', 'income_group'], axis=1)
    
    # สร้าง special binning rules สำหรับตัวแปรต่างๆ
    breaks_adj = {
        'age': [0, 25, 35, 45, 55, 65, np.inf],
        'MonthlyIncome': [0, 2500, 5000, 7500, 10000, 15000, np.inf],
        'DebtRatio': [0, 0.25, 0.5, 0.75, 1, 2, np.inf],
        'RevolvingUtilizationOfUnsecuredLines': [0, 0.25, 0.5, 0.75, 1, 2, np.inf],
        'NumberOfOpenCreditLinesAndLoans': [0, 1, 2, 3, 5, 10, np.inf],
        'NumberOfTimes90DaysLate': [0, 1, 2, 3, 5, np.inf],
        'NumberOfTime60-89DaysPastDueNotWorse': [0, 1, 2, 3, 5, np.inf],
        'NumberOfTime30-59DaysPastDueNotWorse': [0, 1, 2, 3, 5, np.inf],
        'NumberRealEstateLoansOrLines': [0, 1, 2, 3, 5, np.inf],
        'NumberOfDependents': [0, 1, 2, 3, 5, np.inf]
    }
    
    # Calculate Information Value
    iv = sc.iv(df, y="SeriousDlqin2yrs")
    print("\nInformation Values:")
    print(iv)
    
    # Perform WOE binning with special bins
    bins = sc.woebin(df, y="SeriousDlqin2yrs", breaks_list=breaks_adj)
    
    # Split data
    train, test = train_test_split(df, test_size=0.3, random_state=42)
    
    # WOE transformation
    train_woe = sc.woebin_ply(train, bins)
    test_woe = sc.woebin_ply(test, bins)
    
    # Print WOE summary
    print("\nWOE Binning Summary:")
    for var in bins.keys():
        print(f"\nVariable: {var}")
        print(bins[var][['bin', 'count', 'count_distr', 'woe', 'bin_iv']])
    
    return bins, train_woe, test_woe

def train_and_evaluate_models(train_woe, test_woe):
    """
    Train and evaluate Logistic Regression, Random Forest, and XGBoost models
    """
    print("\n4. Model Training and Evaluation")
    print("-" * 50)
    
    # Prepare data
    target = 'SeriousDlqin2yrs'
    X_train = train_woe.drop(target, axis=1)
    y_train = train_woe[target]
    X_test = test_woe.drop(target, axis=1)
    y_test = test_woe[target]
    
    # Handle missing values
    imputer = SimpleImputer(strategy='median')
    
    X_train_imputed = pd.DataFrame(
        imputer.fit_transform(X_train),
        columns=X_train.columns,
        index=X_train.index
    )
    
    X_test_imputed = pd.DataFrame(
        imputer.transform(X_test),
        columns=X_test.columns,
        index=X_test.index
    )
    
    # Initialize models
    models = {
        'Logistic Regression': LogisticRegression(penalty='l2', # Type of penalization l1 = lasso, l2 = ridge
                                     tol=0.0001, # Tolerance for parameters
                                     C=1.0, # Penalty constant, see below
                                     fit_intercept=True, # Use constant?
                                     class_weight='balanced', # Weights, see below
                                     random_state=35976632, # Random seed
                                     max_iter=100, # Maximum iterations
                                     verbose=1, # Show process. 1 is yes.
                                     solver = 'saga',
                                     warm_start=False # Train anew or start from previous weights. For repeated training.
                                     ),
        'Random Forest': RandomForestClassifier(
            n_estimators=1000, # Number of trees to train
            criterion='gini', # How to train the trees. Also supports entropy.
            max_depth=None, # Max depth of the trees. Not necessary to change.
            min_samples_split=2, # Minimum samples to create a split.
            min_samples_leaf=0.001, # Minimum samples in a leaf. Accepts fractions for %. This is 0.1% of sample.
            min_weight_fraction_leaf=0.0, # Same as above, but uses the class weights.
            max_features='log2', # Maximum number of features per split (not tree!) by default is sqrt(vars)
            max_leaf_nodes=None, # Maximum number of nodes.
            min_impurity_decrease=0.0001, # Minimum impurity decrease. This is 10^-3.
            bootstrap=True, # If sample with repetition. For large samples (>100.000) set to false.
            oob_score=True,  # If report accuracy with non-selected cases.
            n_jobs=-1, # Parallel processing. Set to -1 for all cores. Watch your RAM!!
            random_state=35976632, # Seed
            verbose=1, # If to give info during training. Set to 0 for silent training.
            warm_start=False, # If train over previously trained tree.
            class_weight='balanced'
        ),
        'XGBoost': XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='auc',
            objective='binary:logistic'
        )
    }
    
    # Train and evaluate each model
    results = {}
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Train model
        if name == 'XGBoost':
            model.fit(
                X_train_imputed, 
                y_train,
                eval_set=[(X_test_imputed, y_test)],
                verbose=False
            )
        else:
            model.fit(X_train_imputed, y_train)
        
        # Get predictions
        y_pred_proba = model.predict_proba(X_test_imputed)[:, 1]
        y_pred = (y_pred_proba >= 0.5).astype(int)
        
        # Store results
        results[name] = {
            'model': model,
            'predictions': y_pred,
            'probabilities': y_pred_proba,
            'auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        # Print evaluation metrics
        print(f"\n{name} Results:")
        print(f"AUC Score: {results[name]['auc']:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        # Feature importance
        if name == 'Logistic Regression':
            importance = pd.DataFrame({
                'feature': X_train.columns,
                'importance': np.abs(model.coef_[0])
            })
        else:
            importance = pd.DataFrame({
                'feature': X_train.columns,
                'importance': model.feature_importances_
            })
        importance = importance.sort_values('importance', ascending=False)
        
        print("\nTop 10 Important Features:")
        print(importance.head(10))
    
    # Plot ROC curves
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
    
    # Plot feature importance comparison
    plt.figure(figsize=(15, 5))
    for i, (name, result) in enumerate(results.items(), 1):
        plt.subplot(1, 3, i)
        
        importance = results[name].get('importance', pd.DataFrame({
            'feature': X_train.columns,
            'importance': result['model'].feature_importances_ if name != 'Logistic Regression' 
                        else np.abs(result['model'].coef_[0])
        })).sort_values('importance', ascending=False).head(10)
        
        plt.barh(range(len(importance)), importance['importance'])
        plt.yticks(range(len(importance)), importance['feature'])
        plt.title(f'{name} Feature Importance')
    
    plt.tight_layout()
    plt.show()
    
    return (results['Logistic Regression']['model'], 
            results['Random Forest']['model'], 
            results['XGBoost']['model'])

def create_final_scorecard(df, bins, lr):
    """
    Create final scorecard using Logistic Regression
    """
    print("\n5. Final Scorecard Creation")
    print("-" * 50)
    
    # ตรวจสอบว่าคอลัมน์ไหนถูกใช้ในการ train model
    print("\nFeatures used in model:")
    features_with_woe = lr.feature_names_in_  # คอลัมน์ที่ใช้ใน model
    original_features = [feat.replace('_woe', '') for feat in features_with_woe]
    print(original_features)
    
    # Create scorecard
    card = sc.scorecard(
        bins=bins,
        model=lr,
        xcolumns=features_with_woe  # ใช้คอลัมน์ที่มี _woe ตามที่ใช้ train model
    )
    
    # Display scorecard rules
    print("\nScorecard Rules:")
    print(f"Base Points: {card['basepoints']}\n")
    
    for var in card.keys():
        if isinstance(card[var], pd.DataFrame):
            print(f"\nVariable: {var}")
            rules_df = card[var][['bin', 'points']]
            rules_df = rules_df.sort_values('points', ascending=False)
            print("Binning Rules:")
            print(rules_df.to_string(index=False))
            
            # คำนวณผลกระทบต่อคะแนน
            points_range = rules_df['points'].max() - rules_df['points'].min()
            print(f"\nPoints Range: {points_range}")
            print(f"Minimum Points: {rules_df['points'].min()}")
            print(f"Maximum Points: {rules_df['points'].max()}")
    
    return card

def main():
    # 1. Load and explore data
    df = load_and_explore_data()
    
    # 2. Handle missing values and outliers
    df_cleaned = handle_missing_and_outliers(df)
    
    # 3. Create scorecard features
    bins, train_woe, test_woe = create_scorecard_features(df_cleaned)
    
    # 4. Train and evaluate models
    lr_model, rf_model, xgb_model = train_and_evaluate_models(train_woe, test_woe)
    
    # 5. Create final scorecard ด้วย Logistic Regression
    print("\nCreating final scorecard with Logistic Regression model...")
    # เก็บชื่อคอลัมน์ที่ใช้ใน model
    feature_names = train_woe.drop('SeriousDlqin2yrs', axis=1).columns
    card = create_final_scorecard(df_cleaned, bins, lr_model)
    
    # แสดง summary ของ scorecard
    print("\nScorecard Summary:")
    print(f"Number of features: {len(feature_names)}")
    print("\nFeatures used:")
    for i, feat in enumerate(feature_names, 1):
        print(f"{i}. {feat}")
    
    return df_cleaned, bins, card, lr_model, rf_model, xgb_model

if __name__ == "__main__":
    df_cleaned, bins, card, lr_model, rf_model, xgb_model = main()