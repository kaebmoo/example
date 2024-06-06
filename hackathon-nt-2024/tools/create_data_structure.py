import pandas as pd

# Create a dictionary with the columns
data = {
    "New_name": [],
    "install_date": [],
    "product": [],
    "package": [],
    "package_startdate": [],
    "package_enddate": [],
    "status": [],
    "ba_id": [],
    "customer_type_name": [],
    "acc_type_update": [],
    "service_location_code": [],
    "service_location_name": [],
    "Location_name_disp": [],
    "Type": [],
    "ORG_DEP_ABBR": [],
    "ORG05": [],
    "ORG05_ABBR": [],
    "ORG04": [],
    "ORG04_ABBR": [],
    "ORG03": [],
    "ORG03_ABBR": [],
    "package_group_name_th": [],
    "package_info_name": [],
    "start_date_sale_package": [],
    "end_date_sale_package": [],
    "package_price": []
}

columns = [
    "install_date",
    "inactive_date",
    "disconnect_reason",
    "product",
    "package",
    "package_startdate",
    "package_enddate",
    "status",
    "ba_id",
    "customer_type_name",
    "acc_type_update",
    "service_location_code",
    "service_location_name",
    "Location_name_disp",
    "Type",
    "ORG_DEP_ABBR",
    "ORG05",
    "ORG05_ABBR",
    "ORG04",
    "ORG04_ABBR",
    "ORG03",
    "ORG03_ABBR",
    "package_group_name_th",
    "package_info_name",
    "start_date_sale_package",
    "end_date_sale_package",
    "package_price"
]

columns_payment = [
    "RECEIPT_NO",
    "SERVICED_NUMBER",
    "PAYMENT_DATE",
    "RECEIPT_TYPE",
    "ACCOUNT_NO",
    "EXTERNAL_ID",
    "NETWORK_CODE",
    "INVOICE_DATE",
    "INVOICE_NO",
    "BILL_MONTH",
    "TOTAL_AMT",
    "DISCOUNT_AMT",
    "PAY_TYPE",
    "payment_type"
]

# Define the column names
columns_billing = [
    "[SERVICE_LOCATION CODE]",
    "ACCOUNT_NO",
    "TEL_NO",
    "CUSTOMER_REF",
    "ACCOUNT_TYPE",
    "ACTIVE_DATE",
    "INACTIVE_DATE",
    "GOVERMENT_CODE",
    "BANK_CODE",
    "[SERVICE_LOCATION NAME]",
    "HOME_LOCATION_CODE",
    "RC",
    "[METER USAGE]",
    "[METER CHARGE]",
    "[LD CHARGE]",
    "NRC",
    "[DEBIT ADJUSTMENT]",
    "B1P3",
    "DISCOUNT",
    "AMOUNT_DUE",
    "VAT",
    "TOTAL_DUE",
    "[BILL MONTH]",
    "[INVOICE NUM]",
    "[BILL PERIOD]",
    "[PRODUCT DESC]",
    "SPECIAL_BILL"
]

# Create a DataFrame
df = pd.DataFrame(data)
# Save the DataFrame to a CSV file
file_path = '/Users/seal/Documents/GitHub/hackathon-nt-2024/tools/customer_profile_active.csv'
df.to_csv(file_path, index=False)


# Create an empty DataFrame
df = pd.DataFrame(columns=columns)
df_payment = pd.DataFrame(columns=columns_payment)

# Create the CSV file even with an empty DataFrame
df[columns].to_csv("/Users/seal/Documents/GitHub/hackathon-nt-2024/tools/customer_profile_inactive.csv", index=False)
df_payment.to_csv("/Users/seal/Documents/GitHub/hackathon-nt-2024/tools/payment.csv", index=False)



# Create an empty DataFrame
df_billing = pd.DataFrame(columns=columns_billing)

# ... (fill the DataFrame with data)

# Write to CSV file
df_billing.to_csv("/Users/seal/Documents/GitHub/hackathon-nt-2024/tools/billing.csv", index=False)

