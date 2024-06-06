import pandas as pd

# Load the data
customer_profile_active = pd.read_csv('./tools/customer_profile_active.csv')
customer_profile_inactive = pd.read_csv('./tools/customer_profile_inactive.csv')
payment = pd.read_csv('./tools/payment.csv')
billing = pd.read_csv('./tools/billing.csv')

# Merge Customer Profile Active and Inactive on 'ba_id'
merged_customers = customer_profile_active.merge(customer_profile_inactive, on='ba_id', how='left', suffixes=('_active', '_inactive'))

# Merge the result with Payment data on 'ba_id'
merged_customers_payments = merged_customers.merge(payment, left_on='ba_id', right_on='ACCOUNT_NO', how='left')

# Merge the result with Billing data on 'ba_id'
final_merged_data = merged_customers_payments.merge(billing, left_on='ba_id', right_on='ACCOUNT_NO', how='left')

print(final_merged_data.columns)
# Filter the final data to include only active customers
final_filtered_data = final_merged_data[final_merged_data['status_active'] == 'Active']

# Display the final merged data
print(final_filtered_data.head())
print(customer_profile_active)