"""
Multi-layer Sankey Diagram with Plotly
แสดงการไหลแบบหลายระดับ: สายงาน → ฝ่าย → บริการ → ฝ่ายผู้รับ → สายงานผู้รับ
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import numpy as np

def create_multilayer_sankey(excel_file, output_file='multilayer_sankey.html'):
    """
    สร้าง Multi-layer Sankey Diagram ด้วย Plotly
    แสดงทุกระดับ: สายงาน → ฝ่าย → บริการ → ฝ่ายผู้รับ → สายงานผู้รับ
    """
    
    print("=" * 60)
    print("📊 Multi-layer Sankey Diagram Generator")
    print("=" * 60)
    
    # อ่านไฟล์
    print(f"\n📖 กำลังอ่านไฟล์: {excel_file}")
    df = pd.read_excel(excel_file)
    
    # แสดงข้อมูลสรุป
    print("\n📋 สรุปข้อมูล:")
    print(f"   - จำนวนแถว: {len(df):,} รายการ")
    print(f"   - มูลค่ารวม: {df['จำนวนเงิน (PxQ)'].sum():,.0f} บาท")
    print(f"   - บริการ: {df['บริการ'].nunique()} ประเภท")
    print(f"   - บริการย่อย: {df['บริการย่อย'].nunique()} รายการ")
    print(f"   - สายงานผู้ให้บริการ: {df['สายงานผู้ให้บริการ'].nunique()} สายงาน")
    print(f"   - ฝ่ายผู้ให้บริการ: {df['ฝ่ายผู้ให้บริการ'].nunique()} ฝ่าย")
    print(f"   - ฝ่ายผู้รับบริการ: {df['ฝ่ายผู้รับบริการ'].nunique()} ฝ่าย")
    print(f"   - สายงานผู้รับบริการ: {df['สายงานผู้รับบริการ'].nunique()} สายงาน")
    
    # ให้ผู้ใช้เลือกการแสดงผล
    print("\n🎯 เลือกรูปแบบการแสดงผล:")
    print("1. Full Flow: สายงานให้ → ฝ่ายให้ → บริการ → ฝ่ายรับ → สายงานรับ")
    print("2. Department Focus: ฝ่ายให้ → บริการ → ฝ่ายรับ")
    print("3. Service Focus: บริการ → ฝ่ายรับ (grouped by service)")
    print("4. High Level: สายงานให้ → สายงานรับ")
    print("5. Custom: เลือกเอง")
    
    choice = input("\nเลือก (1-5, default=2): ").strip() or "2"
    
    if choice == "1":
        fig = create_full_flow_sankey(df)
    elif choice == "2":
        fig = create_department_sankey(df)
    elif choice == "3":
        fig = create_service_focus_sankey(df)
    elif choice == "4":
        fig = create_high_level_sankey(df)
    else:
        fig = create_custom_sankey(df)
    
    # บันทึกไฟล์
    fig.write_html(output_file)
    print(f"\n✅ บันทึกไฟล์สำเร็จ: {output_file}")
    print("🌐 เปิดไฟล์ใน browser เพื่อดูผลลัพธ์")
    
    # แสดงกราฟ
    fig.show()
    
    return output_file


def create_full_flow_sankey(df):
    """
    Full Flow: สายงานให้ → ฝ่ายให้ → บริการ → ฝ่ายรับ → สายงานรับ
    """
    print("\n🔄 กำลังสร้าง Full Flow Sankey...")
    
    all_nodes = []
    all_links = []
    node_dict = {}
    node_counter = 0
    
    # Layer 1: สายงานผู้ให้บริการ (unique with prefix)
    provider_lines = df['สายงานผู้ให้บริการ'].unique()
    for line in provider_lines:
        node_name = f"[ให้] {line}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        node_counter += 1
    
    # Layer 2: ฝ่ายผู้ให้บริการ
    provider_depts = df['ฝ่ายผู้ให้บริการ'].unique()
    for dept in provider_depts:
        node_name = f"ฝ่าย: {dept[:30]}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        node_counter += 1
    
    # Layer 3: บริการ (grouped)
    services = df['บริการ'].unique()
    # จำกัดจำนวนบริการถ้ามากเกินไป
    if len(services) > 30:
        # เอาเฉพาะ top 30 services by value
        top_services = df.groupby('บริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(30).index.tolist()
        services = top_services
        # รวมบริการอื่นๆ
        df.loc[~df['บริการ'].isin(services), 'บริการ'] = 'บริการอื่นๆ'
        services = df['บริการ'].unique()
    
    for service in services:
        node_name = f"📦 {service[:25]}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        node_counter += 1
    
    # Layer 4: ฝ่ายผู้รับบริการ (top 50)
    receiver_depts = df.groupby('ฝ่ายผู้รับบริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(50).index.tolist()
    df.loc[~df['ฝ่ายผู้รับบริการ'].isin(receiver_depts), 'ฝ่ายผู้รับบริการ'] = 'ฝ่ายอื่นๆ'
    receiver_depts = df['ฝ่ายผู้รับบริการ'].unique()
    
    for dept in receiver_depts:
        node_name = f"รับ: {dept[:30]}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        node_counter += 1
    
    # Layer 5: สายงานผู้รับบริการ
    receiver_lines = df['สายงานผู้รับบริการ'].unique()
    for line in receiver_lines:
        node_name = f"[รับ] {line}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        node_counter += 1
    
    # สร้าง Links
    # Link 1: สายงานให้ → ฝ่ายให้
    link1 = df.groupby(['สายงานผู้ให้บริการ', 'ฝ่ายผู้ให้บริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in link1.iterrows():
        all_links.append({
            'source': node_dict[f"[ให้] {row['สายงานผู้ให้บริการ']}"],
            'target': node_dict[f"ฝ่าย: {row['ฝ่ายผู้ให้บริการ'][:30]}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # Link 2: ฝ่ายให้ → บริการ
    link2 = df.groupby(['ฝ่ายผู้ให้บริการ', 'บริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in link2.iterrows():
        all_links.append({
            'source': node_dict[f"ฝ่าย: {row['ฝ่ายผู้ให้บริการ'][:30]}"],
            'target': node_dict[f"📦 {row['บริการ'][:25]}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # Link 3: บริการ → ฝ่ายรับ
    link3 = df.groupby(['บริการ', 'ฝ่ายผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in link3.iterrows():
        all_links.append({
            'source': node_dict[f"📦 {row['บริการ'][:25]}"],
            'target': node_dict[f"รับ: {row['ฝ่ายผู้รับบริการ'][:30]}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # Link 4: ฝ่ายรับ → สายงานรับ
    link4 = df.groupby(['ฝ่ายผู้รับบริการ', 'สายงานผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in link4.iterrows():
        all_links.append({
            'source': node_dict[f"รับ: {row['ฝ่ายผู้รับบริการ'][:30]}"],
            'target': node_dict[f"[รับ] {row['สายงานผู้รับบริการ']}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # สร้าง Plotly Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=px.colors.qualitative.Plotly * 10,  # repeat colors
            hovertemplate='%{label}<br>Total: %{value:,.0f} บาท<extra></extra>'
        ),
        link=dict(
            source=[link['source'] for link in all_links],
            target=[link['target'] for link in all_links],
            value=[link['value'] for link in all_links],
            hovertemplate='%{source.label} → %{target.label}<br>Value: %{value:,.0f} บาท<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title="Full Flow Sankey: สายงาน → ฝ่าย → บริการ → ฝ่ายรับ → สายงานรับ",
        font_size=10,
        height=900,
        margin=dict(t=50, l=20, r=20, b=20)
    )
    
    return fig


def create_department_sankey(df):
    """
    Department Focus: ฝ่ายให้ → บริการ → ฝ่ายรับ
    """
    print("\n🔄 กำลังสร้าง Department Focus Sankey...")
    
    all_nodes = []
    all_links = []
    node_dict = {}
    node_counter = 0
    
    # กรองเฉพาะ top departments และ services
    top_provider_depts = df.groupby('ฝ่ายผู้ให้บริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(30).index.tolist()
    top_services = df.groupby('บริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(40).index.tolist()
    top_receiver_depts = df.groupby('ฝ่ายผู้รับบริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(40).index.tolist()
    
    # Filter dataframe
    filtered_df = df[
        (df['ฝ่ายผู้ให้บริการ'].isin(top_provider_depts)) &
        (df['บริการ'].isin(top_services)) &
        (df['ฝ่ายผู้รับบริการ'].isin(top_receiver_depts))
    ].copy()
    
    # Layer 1: ฝ่ายผู้ให้บริการ
    for dept in filtered_df['ฝ่ายผู้ให้บริการ'].unique():
        node_name = f"🏢 {dept[:40]}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        node_counter += 1
    
    # Layer 2: บริการ
    for service in filtered_df['บริการ'].unique():
        node_name = f"📦 {service[:35]}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        node_counter += 1
    
    # Layer 3: ฝ่ายผู้รับบริการ
    for dept in filtered_df['ฝ่ายผู้รับบริการ'].unique():
        node_name = f"📥 {dept[:40]}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        node_counter += 1
    
    # สร้าง Links
    # Link 1: ฝ่ายให้ → บริการ
    link1 = filtered_df.groupby(['ฝ่ายผู้ให้บริการ', 'บริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in link1.iterrows():
        all_links.append({
            'source': node_dict[f"🏢 {row['ฝ่ายผู้ให้บริการ'][:40]}"],
            'target': node_dict[f"📦 {row['บริการ'][:35]}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # Link 2: บริการ → ฝ่ายรับ
    link2 = filtered_df.groupby(['บริการ', 'ฝ่ายผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in link2.iterrows():
        all_links.append({
            'source': node_dict[f"📦 {row['บริการ'][:35]}"],
            'target': node_dict[f"📥 {row['ฝ่ายผู้รับบริการ'][:40]}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # สร้าง color palette
    colors = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel + px.colors.qualitative.Bold
    node_colors = []
    for i, node in enumerate(all_nodes):
        if node.startswith('🏢'):
            node_colors.append('#3498db')  # Blue for providers
        elif node.startswith('📦'):
            node_colors.append('#2ecc71')  # Green for services
        else:
            node_colors.append('#e74c3c')  # Red for receivers
    
    # สร้าง Plotly Sankey
    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=10,
            thickness=15,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=node_colors,
            hovertemplate='%{label}<br>Total: %{value:,.0f} บาท<extra></extra>'
        ),
        link=dict(
            source=[link['source'] for link in all_links],
            target=[link['target'] for link in all_links],
            value=[link['value'] for link in all_links],
            color='rgba(0,0,0,0.2)',
            hovertemplate='%{source.label} → %{target.label}<br>Value: %{value:,.0f} บาท<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title={
            'text': "Department & Service Flow Analysis<br><sub>ฝ่ายผู้ให้บริการ → บริการ → ฝ่ายผู้รับบริการ</sub>",
            'x': 0.5,
            'xanchor': 'center'
        },
        font_size=11,
        height=1000,
        margin=dict(t=80, l=20, r=20, b=20),
        paper_bgcolor='#f8f9fa',
        plot_bgcolor='white'
    )
    
    return fig


def create_service_focus_sankey(df):
    """
    Service Focus: บริการ → ฝ่ายรับ (grouped by service category)
    """
    print("\n🔄 กำลังสร้าง Service Focus Sankey...")
    
    # จัดกลุ่มบริการ
    service_categories = {
        'Cloud & Virtual': ['Cloud', 'Virtual', 'VM', 'VPS', 'Container'],
        'Network & Connectivity': ['Network', 'LAN', 'WAN', 'Internet', 'MPLS', 'VPN'],
        'Data Center': ['Colocation', 'Co-location', 'Data Center', 'DC', 'Rack'],
        'Transmission': ['DWDM', 'สื่อสัญญาณ', 'Transmission', 'Fiber'],
        'Security': ['Security', 'Firewall', 'WAF', 'DDoS', 'SOC'],
        'Storage & Backup': ['Storage', 'Backup', 'DR', 'Disaster', 'Archive'],
        'Application': ['Application', 'Software', 'License', 'ERP', 'CRM'],
        'Professional Services': ['Consult', 'Support', 'Manage', 'Monitor', 'Outsource']
    }
    
    # เพิ่มคอลัมน์ service_category
    df['service_category'] = 'Others'
    for category, keywords in service_categories.items():
        for keyword in keywords:
            mask = df['บริการ'].str.contains(keyword, case=False, na=False)
            df.loc[mask, 'service_category'] = category
    
    all_nodes = []
    all_links = []
    node_dict = {}
    node_counter = 0
    
    # Layer 1: Service Categories
    for category in df['service_category'].unique():
        node_dict[category] = node_counter
        all_nodes.append(f"🔹 {category}")
        node_counter += 1
    
    # Layer 2: Services (top 50)
    top_services = df.groupby('บริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(50).index.tolist()
    filtered_df = df[df['บริการ'].isin(top_services)].copy()
    
    for service in filtered_df['บริการ'].unique():
        node_name = f"📦 {service[:40]}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        node_counter += 1
    
    # Layer 3: Top Receiver Departments
    top_receivers = filtered_df.groupby('ฝ่ายผู้รับบริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(50).index.tolist()
    for dept in top_receivers:
        node_name = f"🏛️ {dept[:40]}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        node_counter += 1
    
    # Links
    # Category → Service
    link1 = filtered_df.groupby(['service_category', 'บริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in link1.iterrows():
        all_links.append({
            'source': node_dict[row['service_category']],
            'target': node_dict[f"📦 {row['บริการ'][:40]}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # Service → Department
    filtered_df = filtered_df[filtered_df['ฝ่ายผู้รับบริการ'].isin(top_receivers)]
    link2 = filtered_df.groupby(['บริการ', 'ฝ่ายผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in link2.iterrows():
        all_links.append({
            'source': node_dict[f"📦 {row['บริการ'][:40]}"],
            'target': node_dict[f"🏛️ {row['ฝ่ายผู้รับบริการ'][:40]}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # Create figure
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=px.colors.qualitative.Vivid * 10,
            hovertemplate='%{label}<br>Total: %{value:,.0f} บาท<extra></extra>'
        ),
        link=dict(
            source=[link['source'] for link in all_links],
            target=[link['target'] for link in all_links],
            value=[link['value'] for link in all_links],
            color='rgba(0,0,0,0.15)',
            hovertemplate='%{source.label} → %{target.label}<br>Value: %{value:,.0f} บาท<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title="Service Category Analysis",
        font_size=11,
        height=900,
        margin=dict(t=50, l=20, r=20, b=20)
    )
    
    return fig


def create_high_level_sankey(df):
    """
    High Level: สายงานให้ → สายงานรับ
    """
    print("\n🔄 กำลังสร้าง High Level Sankey...")
    
    # รวมข้อมูลระดับสายงาน
    flow_data = df.groupby(['สายงานผู้ให้บริการ', 'สายงานผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    flow_data = flow_data.sort_values('จำนวนเงิน (PxQ)', ascending=False)
    
    # สร้าง unique nodes
    providers = flow_data['สายงานผู้ให้บริการ'].unique()
    receivers = flow_data['สายงานผู้รับบริการ'].unique()
    
    all_nodes = []
    node_dict = {}
    node_counter = 0
    
    # Add provider nodes
    for provider in providers:
        node_name = f"[ผู้ให้] {provider}"
        node_dict[provider] = node_counter
        all_nodes.append(node_name)
        node_counter += 1
    
    # Add receiver nodes (avoid duplicates)
    for receiver in receivers:
        if receiver not in providers:
            node_name = f"[ผู้รับ] {receiver}"
            node_dict[receiver] = node_counter
            all_nodes.append(node_name)
            node_counter += 1
        else:
            # If it's both provider and receiver, add with different key
            node_dict[f"recv_{receiver}"] = node_counter
            all_nodes.append(f"[ผู้รับ] {receiver}")
            node_counter += 1
    
    # Create links
    all_links = []
    for _, row in flow_data.iterrows():
        provider = row['สายงานผู้ให้บริการ']
        receiver = row['สายงานผู้รับบริการ']
        
        # Check if receiver is also a provider
        if receiver in providers:
            target_key = f"recv_{receiver}"
        else:
            target_key = receiver
            
        all_links.append({
            'source': node_dict[provider],
            'target': node_dict[target_key],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # Create colors
    colors = []
    for node in all_nodes:
        if '[ผู้ให้]' in node:
            colors.append('#3498db')  # Blue
        else:
            colors.append('#e74c3c')  # Red
    
    # Create figure
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=30,
            line=dict(color="black", width=1),
            label=all_nodes,
            color=colors,
            hovertemplate='%{label}<br>Total: %{value:,.0f} บาท<extra></extra>'
        ),
        link=dict(
            source=[link['source'] for link in all_links],
            target=[link['target'] for link in all_links],
            value=[link['value'] for link in all_links],
            color='rgba(0,0,0,0.2)',
            hovertemplate='%{source.label} → %{target.label}<br>Value: %{value:,.0f} บาท<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title={
            'text': "High Level Flow: สายงานผู้ให้บริการ → สายงานผู้รับบริการ",
            'x': 0.5,
            'xanchor': 'center'
        },
        font=dict(size=12),
        height=700,
        margin=dict(t=80, l=50, r=50, b=50)
    )
    
    return fig


def create_custom_sankey(df):
    """
    Custom: ให้ผู้ใช้เลือกเอง
    """
    print("\n🎨 Custom Sankey Configuration")
    print("\nเลือกคอลัมน์ที่ต้องการแสดง (เรียงตามลำดับ):")
    
    available_cols = [
        'สายงานผู้ให้บริการ',
        'ฝ่ายผู้ให้บริการ', 
        'บริการ',
        'บริการย่อย',
        'ฝ่ายผู้รับบริการ',
        'สายงานผู้รับบริการ'
    ]
    
    print("\nคอลัมน์ที่มี:")
    for i, col in enumerate(available_cols, 1):
        print(f"{i}. {col}")
    
    selected = input("\nใส่หมายเลขคอลัมน์ที่ต้องการ (คั่นด้วย comma เช่น 2,3,5): ").strip()
    
    if not selected:
        selected = "2,3,5"  # Default
    
    selected_indices = [int(x.strip())-1 for x in selected.split(',')]
    selected_cols = [available_cols[i] for i in selected_indices]
    
    print(f"\n✅ เลือก: {' → '.join(selected_cols)}")
    
    # Ask for top N
    top_n = input("แสดง Top กี่รายการ (default=30): ").strip()
    top_n = int(top_n) if top_n else 30
    
    # Create custom sankey based on selection
    return create_dynamic_sankey(df, selected_cols, top_n)


def create_dynamic_sankey(df, columns, top_n=30):
    """
    สร้าง Sankey แบบ dynamic ตาม columns ที่เลือก
    """
    all_nodes = []
    all_links = []
    node_dict = {}
    node_counter = 0
    
    # Process each column
    for i, col in enumerate(columns):
        # Get top values for this column
        if 'บริการย่อย' in col:
            top_values = df.groupby(col)['จำนวนเงิน (PxQ)'].sum().nlargest(top_n*2).index.tolist()
        else:
            top_values = df.groupby(col)['จำนวนเงิน (PxQ)'].sum().nlargest(top_n).index.tolist()
        
        # Add nodes
        for value in top_values:
            node_name = f"[L{i+1}] {str(value)[:40]}"
            if node_name not in node_dict:
                node_dict[node_name] = node_counter
                all_nodes.append(node_name)
                node_counter += 1
    
    # Create links between consecutive columns
    for i in range(len(columns) - 1):
        source_col = columns[i]
        target_col = columns[i + 1]
        
        # Get top values
        source_values = df.groupby(source_col)['จำนวนเงิน (PxQ)'].sum().nlargest(top_n).index.tolist()
        target_values = df.groupby(target_col)['จำนวนเงิน (PxQ)'].sum().nlargest(top_n).index.tolist()
        
        # Filter data
        filtered = df[
            (df[source_col].isin(source_values)) & 
            (df[target_col].isin(target_values))
        ]
        
        # Group and create links
        link_data = filtered.groupby([source_col, target_col])['จำนวนเงิน (PxQ)'].sum().reset_index()
        
        for _, row in link_data.iterrows():
            source_name = f"[L{i+1}] {str(row[source_col])[:40]}"
            target_name = f"[L{i+2}] {str(row[target_col])[:40]}"
            
            if source_name in node_dict and target_name in node_dict:
                all_links.append({
                    'source': node_dict[source_name],
                    'target': node_dict[target_name],
                    'value': row['จำนวนเงิน (PxQ)']
                })
    
    # Create figure
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=px.colors.qualitative.Alphabet * 10,
            hovertemplate='%{label}<br>Total: %{value:,.0f} บาท<extra></extra>'
        ),
        link=dict(
            source=[link['source'] for link in all_links],
            target=[link['target'] for link in all_links],
            value=[link['value'] for link in all_links],
            hovertemplate='%{source.label} → %{target.label}<br>Value: %{value:,.0f} บาท<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title=f"Custom Sankey: {' → '.join(columns)}",
        font_size=11,
        height=800,
        margin=dict(t=50, l=20, r=20, b=20)
    )
    
    return fig


# ==========================================
# Utility Functions
# ==========================================

def analyze_data_structure(excel_file):
    """
    วิเคราะห์โครงสร้างข้อมูลและแนะนำการแสดงผล
    """
    df = pd.read_excel(excel_file)
    
    print("\n" + "=" * 60)
    print("📊 Data Structure Analysis")
    print("=" * 60)
    
    # Basic info
    print(f"\n📋 ข้อมูลพื้นฐาน:")
    print(f"   - จำนวนแถว: {len(df):,}")
    print(f"   - จำนวนคอลัมน์: {len(df.columns)}")
    print(f"   - มูลค่ารวม: {df['จำนวนเงิน (PxQ)'].sum():,.0f} บาท")
    
    # Unique counts
    print(f"\n🔢 จำนวน Unique Values:")
    for col in df.columns:
        if col not in ['ราคาต่อหน่วย (P)', 'ปริมาณการใช้ (Q)', 'จำนวนเงิน (PxQ)', 'หน่วยนับ']:
            print(f"   - {col}: {df[col].nunique()}")
    
    # Top values by column
    print(f"\n🏆 Top 3 by Value:")
    for col in ['สายงานผู้ให้บริการ', 'ฝ่ายผู้ให้บริการ', 'บริการ', 'ฝ่ายผู้รับบริการ']:
        top = df.groupby(col)['จำนวนเงิน (PxQ)'].sum().nlargest(3)
        print(f"\n   {col}:")
        for name, value in top.items():
            print(f"      - {name[:50]}: {value:,.0f} บาท")
    
    # Recommendations
    print(f"\n💡 คำแนะนำ:")
    
    if df['บริการ'].nunique() > 50:
        print("   ⚠️ บริการมีมากกว่า 50 ประเภท - ควรจัดกลุ่มหรือแสดง Top N")
    
    if df['ฝ่ายผู้รับบริการ'].nunique() > 100:
        print("   ⚠️ ฝ่ายผู้รับบริการมีมากกว่า 100 ฝ่าย - ควรกรองเฉพาะ Top 50")
    
    if len(df) > 2000:
        print("   ⚠️ ข้อมูลมีมากกว่า 2000 แถว - ควรรวมข้อมูลก่อนแสดงผล")
    
    print("\n   ✅ แนะนำใช้ Option 2: Department Focus")
    print("   ✅ หรือ Option 4: High Level สำหรับภาพรวม")
    

# ==========================================
# Main Execution
# ==========================================

if __name__ == "__main__":
    import sys
    
    try:
        import plotly
    except ImportError:
        print("❌ กรุณาติดตั้ง plotly ก่อน:")
        print("   pip install plotly pandas openpyxl")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
        
        if not Path(excel_file).exists():
            print(f"❌ ไม่พบไฟล์: {excel_file}")
            sys.exit(1)
        
        # Analyze data first
        analyze = input("\n📊 ต้องการวิเคราะห์ข้อมูลก่อนไหม? (y/N): ").strip().lower()
        if analyze == 'y':
            analyze_data_structure(excel_file)
            input("\nกด Enter เพื่อดำเนินการต่อ...")
        
        # Create sankey
        create_multilayer_sankey(excel_file)
    else:
        print("\n📌 วิธีใช้งาน:")
        print("   python script.py your_excel_file.xlsx")
        print("\n💡 Features:")
        print("   - Multi-layer Sankey (5 ระดับ)")
        print("   - Department Focus View") 
        print("   - Service Category Analysis")
        print("   - High Level Overview")
        print("   - Custom Configuration")