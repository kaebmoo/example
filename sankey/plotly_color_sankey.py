"""
Complete Sankey Diagram Generator - Working Version
รวมทุก features และทำงานได้จริง
"""

import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

def create_complete_sankey(excel_file, output_file='complete_sankey.html'):
    """
    Main function - สร้าง Sankey พร้อม menu เลือก
    """
    print("=" * 60)
    print("🎨 Complete Sankey Diagram Generator")
    print("=" * 60)
    
    # อ่านไฟล์
    print(f"\n📖 กำลังอ่านไฟล์: {excel_file}")
    df = pd.read_excel(excel_file)
    
    # จัดกลุ่มบริการ
    service_groups = {
        'Cloud & Big Data': ['Cloud', 'NT BIG DATA', 'Data Warehouse'],
        'Security': ['Cyber Security'],
        'Network & Internet': ['DWDM', 'Dark Fiber', 'ISP', 'IX', 'IIG', 'เคเบิลใต้น้ำ', 
                               'Broadband', 'Datacom', 'CPE Datacom', 'IP Address'],
        'Communication': ['Conference', 'Contact Center', 'IPPhone', 'SIPTrunk', 
                         'SMS', 'NT Messaging', 'โทรศัพท์ภายใน', '1888'],
        'Infrastructure': ['IDC', 'เสาโทรคมนาคม', 'ท่อร้อยสาย', 'อาคาร', 'โครงข่าย', 
                          'Fixed Line', 'Mobile', 'โครงสร้างพื้นฐาน'],
        'Software & Apps': ['Adobe', 'Microsoft Office', 'Application', 'Software',
                           'NT Form', 'IM Web', 'e-Tax', 'Web', 'SCOMS'],
        'IT Services': ['Helpdesk', 'Managed Service', 'NOC', 'server'],
        'Billing & Finance': ['Billing', 'Special Bill', 'Debt', 'Bill Payment', 
                             'e-Service', 'ใบแจ้งค่า', 'ใบกำกับภาษี'],
        'Professional Services': ['MA', 'ติดตั้ง', 'บริหารโครงการ', 'กฎหมาย', 
                                 'วิทยากร', 'พัฒนาระบบ', 'สัญญา']
    }
    
    # เพิ่ม service_group column
    df['service_group'] = 'Others'
    for group, keywords in service_groups.items():
        for keyword in keywords:
            mask = df['บริการ'].str.contains(keyword, case=False, na=False)
            df.loc[mask, 'service_group'] = group
    
    # Color schemes
    color_schemes = {
        'service': {
            'Cloud & Big Data': '#8b5cf6',
            'Security': '#ef4444',
            'Network & Internet': '#06b6d4',
            'Communication': '#10b981',
            'Infrastructure': '#f97316',
            'Software & Apps': '#ec4899',
            'IT Services': '#6366f1',
            'Billing & Finance': '#eab308',
            'Professional Services': '#64748b',
            'Others': '#9ca3af'
        }
    }
    
    # วิเคราะห์ dual roles
    providers = set(df['ฝ่ายผู้ให้บริการ'].unique())
    receivers = set(df['ฝ่ายผู้รับบริการ'].unique())
    dual_role_depts = providers & receivers
    
    print(f"\n📊 สรุปข้อมูล:")
    print(f"   - จำนวนแถว: {len(df):,} รายการ")
    print(f"   - มูลค่ารวม: {df['จำนวนเงิน (PxQ)'].sum():,.0f} บาท")
    print(f"   - ฝ่ายผู้ให้บริการ: {len(providers)} ฝ่าย")
    print(f"   - ฝ่ายผู้รับบริการ: {len(receivers)} ฝ่าย")
    print(f"   - หน่วยงาน Dual Role: {len(dual_role_depts)} ฝ่าย")
    
    print("\n🎯 เลือกรูปแบบการแสดงผล:")
    print("1. Department View: ฝ่ายให้ → กลุ่มบริการ → ฝ่ายรับ")
    print("2. Service Detail: ฝ่ายให้ → บริการทั้งหมด → ฝ่ายรับ")
    print("3. High Level: สายงานให้ → สายงานรับ")
    print("4. Dual Role: หน่วยงานที่ทั้งให้และรับบริการ")
    print("5. Service Network: ผู้ให้ → บริการ → ผู้รับ (ที่เป็นผู้ให้ด้วย) → บริการที่ให้ต่อ")
    
    choice = input("\nเลือก (1-5, default=1): ").strip() or "1"
    
    # สร้างกราฟตามที่เลือก
    if choice == "1":
        fig = create_department_view(df, service_groups, color_schemes, dual_role_depts)
    elif choice == "2":
        fig = create_service_detail_view(df, color_schemes, dual_role_depts)
    elif choice == "3":
        fig = create_high_level_view(df, dual_role_depts)
    elif choice == "4":
        fig = create_dual_role_view(df, service_groups, color_schemes, dual_role_depts)
    else:
        fig = create_service_network_view(df, service_groups, color_schemes, dual_role_depts)
    
    # บันทึกไฟล์
    if fig:
        fig.write_html(output_file)
        print(f"\n✅ สร้างไฟล์สำเร็จ: {output_file}")
        print("🌐 เปิดไฟล์ใน browser เพื่อดูผลลัพธ์")
    
    return output_file

def hex_to_rgba(hex_color, alpha):
    """แปลง hex เป็น rgba"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {alpha})'

def create_department_view(df, service_groups, color_schemes, dual_role_depts):
    """View 1: ฝ่าย → กลุ่มบริการ → ฝ่าย"""
    print("\n🔄 กำลังสร้าง Department View...")
    
    # Filter top items
    top_providers = df.groupby('ฝ่ายผู้ให้บริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(25).index
    top_receivers = df.groupby('ฝ่ายผู้รับบริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(40).index
    
    filtered_df = df[
        df['ฝ่ายผู้ให้บริการ'].isin(top_providers) & 
        df['ฝ่ายผู้รับบริการ'].isin(top_receivers)
    ].copy()
    
    # สร้าง nodes
    all_nodes = []
    all_colors = []
    node_dict = {}
    node_counter = 0
    
    # Layer 1: Providers
    for provider in filtered_df['ฝ่ายผู้ให้บริการ'].unique():
        node_name = f"[ให้] {provider[:35]}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        all_colors.append('#2563eb')
        node_counter += 1
    
    # Layer 2: Service Groups
    for group in filtered_df['service_group'].unique():
        node_name = f"📦 {group}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        all_colors.append(color_schemes['service'].get(group, '#9ca3af'))
        node_counter += 1
    
    # Layer 3: Receivers
    for receiver in filtered_df['ฝ่ายผู้รับบริการ'].unique():
        node_name = f"[รับ] {receiver[:35]}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        color = '#9333ea' if receiver in dual_role_depts else '#10b981'
        all_colors.append(color)
        node_counter += 1
    
    # สร้าง links
    all_links = []
    
    # Provider -> Service Group
    link1 = filtered_df.groupby(['ฝ่ายผู้ให้บริการ', 'service_group'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in link1.iterrows():
        all_links.append({
            'source': node_dict[f"[ให้] {row['ฝ่ายผู้ให้บริการ'][:35]}"],
            'target': node_dict[f"📦 {row['service_group']}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # Service Group -> Receiver
    link2 = filtered_df.groupby(['service_group', 'ฝ่ายผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in link2.iterrows():
        all_links.append({
            'source': node_dict[f"📦 {row['service_group']}"],
            'target': node_dict[f"[รับ] {row['ฝ่ายผู้รับบริการ'][:35]}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # สร้าง figure
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="white", width=1),
            label=all_nodes,
            color=all_colors,
            hovertemplate='%{label}<br>มูลค่า: %{value:,.0f} บาท<extra></extra>'
        ),
        link=dict(
            source=[link['source'] for link in all_links],
            target=[link['target'] for link in all_links],
            value=[link['value'] for link in all_links],
            color=['rgba(0,0,0,0.2)' for _ in all_links],
            hovertemplate='%{source.label} → %{target.label}<br>มูลค่า: %{value:,.0f} บาท<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title="Department View: ฝ่ายผู้ให้ → กลุ่มบริการ → ฝ่ายผู้รับ<br><sub>🔵 ผู้ให้ | 🎨 บริการ | 🟢 ผู้รับ | 🟣 Dual Role</sub>",
        font=dict(size=11),
        height=900,
        margin=dict(t=100, l=30, r=30, b=30)
    )
    
    return fig

def create_service_detail_view(df, color_schemes, dual_role_depts):
    """View 2: แสดงบริการทั้งหมด"""
    print("\n🔄 กำลังสร้าง Service Detail View...")
    
    # Filter top items
    top_providers = df.groupby('ฝ่ายผู้ให้บริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(20).index
    top_services = df.groupby('บริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(30).index
    top_receivers = df.groupby('ฝ่ายผู้รับบริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(30).index
    
    filtered_df = df[
        df['ฝ่ายผู้ให้บริการ'].isin(top_providers) & 
        df['บริการ'].isin(top_services) &
        df['ฝ่ายผู้รับบริการ'].isin(top_receivers)
    ].copy()
    
    # สร้าง nodes
    all_nodes = []
    all_colors = []
    node_dict = {}
    node_counter = 0
    
    # Providers
    for provider in filtered_df['ฝ่ายผู้ให้บริการ'].unique():
        node_name = f"[ให้] {provider[:30]}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        all_colors.append('#3b82f6')
        node_counter += 1
    
    # Services
    for service in filtered_df['บริการ'].unique():
        node_name = f"📦 {service[:30]}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        service_group = filtered_df[filtered_df['บริการ'] == service]['service_group'].iloc[0]
        all_colors.append(color_schemes['service'].get(service_group, '#9ca3af'))
        node_counter += 1
    
    # Receivers
    for receiver in filtered_df['ฝ่ายผู้รับบริการ'].unique():
        node_name = f"[รับ] {receiver[:30]}"
        node_dict[node_name] = node_counter
        all_nodes.append(node_name)
        color = '#9333ea' if receiver in dual_role_depts else '#10b981'
        all_colors.append(color)
        node_counter += 1
    
    # Links
    all_links = []
    
    # Provider -> Service
    link1 = filtered_df.groupby(['ฝ่ายผู้ให้บริการ', 'บริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in link1.iterrows():
        all_links.append({
            'source': node_dict[f"[ให้] {row['ฝ่ายผู้ให้บริการ'][:30]}"],
            'target': node_dict[f"📦 {row['บริการ'][:30]}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # Service -> Receiver
    link2 = filtered_df.groupby(['บริการ', 'ฝ่ายผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in link2.iterrows():
        all_links.append({
            'source': node_dict[f"📦 {row['บริการ'][:30]}"],
            'target': node_dict[f"[รับ] {row['ฝ่ายผู้รับบริการ'][:30]}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=10,
            thickness=15,
            line=dict(color="white", width=0.5),
            label=all_nodes,
            color=all_colors
        ),
        link=dict(
            source=[link['source'] for link in all_links],
            target=[link['target'] for link in all_links],
            value=[link['value'] for link in all_links],
            color=['rgba(0,0,0,0.15)' for _ in all_links]
        )
    )])
    
    fig.update_layout(
        title="Service Detail View: บริการทั้งหมด",
        height=900
    )
    
    return fig

def create_high_level_view(df, dual_role_depts):
    """View 3: สายงาน → สายงาน"""
    print("\n🔄 กำลังสร้าง High Level View...")
    
    flow_data = df.groupby(['สายงานผู้ให้บริการ', 'สายงานผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    flow_data = flow_data[flow_data['จำนวนเงิน (PxQ)'] > 0]
    
    all_nodes = []
    all_colors = []
    node_dict = {}
    node_counter = 0
    
    # Providers
    for provider in flow_data['สายงานผู้ให้บริการ'].unique():
        node_name = f"[ให้] {provider}"
        node_dict[f"p_{provider}"] = node_counter
        all_nodes.append(node_name)
        all_colors.append('#2563eb')
        node_counter += 1
    
    # Receivers
    for receiver in flow_data['สายงานผู้รับบริการ'].unique():
        node_name = f"[รับ] {receiver}"
        node_dict[f"r_{receiver}"] = node_counter
        all_nodes.append(node_name)
        all_colors.append('#10b981')
        node_counter += 1
    
    # Links
    all_links = []
    for _, row in flow_data.iterrows():
        all_links.append({
            'source': node_dict[f"p_{row['สายงานผู้ให้บริการ']}"],
            'target': node_dict[f"r_{row['สายงานผู้รับบริการ']}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=30,
            line=dict(color="white", width=2),
            label=all_nodes,
            color=all_colors
        ),
        link=dict(
            source=[link['source'] for link in all_links],
            target=[link['target'] for link in all_links],
            value=[link['value'] for link in all_links],
            color=['rgba(0,0,0,0.2)' for _ in all_links]
        )
    )])
    
    fig.update_layout(
        title="High Level View: สายงาน → สายงาน",
        height=700
    )
    
    return fig

def create_dual_role_view(df, service_groups, color_schemes, dual_role_depts):
    """View 4: Dual Role Departments"""
    print("\n🔄 กำลังสร้าง Dual Role View...")
    
    if not dual_role_depts:
        print("❌ ไม่มีหน่วยงาน Dual Role")
        return None
    
    # Filter for dual role
    dual_df = df[
        (df['ฝ่ายผู้ให้บริการ'].isin(dual_role_depts)) |
        (df['ฝ่ายผู้รับบริการ'].isin(dual_role_depts))
    ].copy()
    
    all_nodes = []
    all_colors = []
    node_dict = {}
    node_counter = 0
    
    # As Providers
    for dept in dual_role_depts:
        if dept in dual_df['ฝ่ายผู้ให้บริการ'].values:
            node_name = f"[ให้] {dept[:30]}"
            node_dict[f"p_{dept}"] = node_counter
            all_nodes.append(node_name)
            all_colors.append('#3b82f6')
            node_counter += 1
    
    # Services
    for group in dual_df['service_group'].unique():
        node_name = f"📦 {group}"
        node_dict[group] = node_counter
        all_nodes.append(node_name)
        all_colors.append(color_schemes['service'].get(group, '#9ca3af'))
        node_counter += 1
    
    # As Receivers
    for dept in dual_role_depts:
        if dept in dual_df['ฝ่ายผู้รับบริการ'].values:
            node_name = f"[รับ] {dept[:30]}"
            node_dict[f"r_{dept}"] = node_counter
            all_nodes.append(node_name)
            all_colors.append('#9333ea')
            node_counter += 1
    
    # Links
    all_links = []
    
    # Provider -> Service
    link1 = dual_df[dual_df['ฝ่ายผู้ให้บริการ'].isin(dual_role_depts)].groupby(
        ['ฝ่ายผู้ให้บริการ', 'service_group'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    
    for _, row in link1.iterrows():
        if f"p_{row['ฝ่ายผู้ให้บริการ']}" in node_dict:
            all_links.append({
                'source': node_dict[f"p_{row['ฝ่ายผู้ให้บริการ']}"],
                'target': node_dict[row['service_group']],
                'value': row['จำนวนเงิน (PxQ)']
            })
    
    # Service -> Receiver
    link2 = dual_df[dual_df['ฝ่ายผู้รับบริการ'].isin(dual_role_depts)].groupby(
        ['service_group', 'ฝ่ายผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    
    for _, row in link2.iterrows():
        if f"r_{row['ฝ่ายผู้รับบริการ']}" in node_dict:
            all_links.append({
                'source': node_dict[row['service_group']],
                'target': node_dict[f"r_{row['ฝ่ายผู้รับบริการ']}"],
                'value': row['จำนวนเงิน (PxQ)']
            })
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="white", width=1),
            label=all_nodes,
            color=all_colors
        ),
        link=dict(
            source=[link['source'] for link in all_links],
            target=[link['target'] for link in all_links],
            value=[link['value'] for link in all_links],
            color=['rgba(147, 51, 234, 0.2)' for _ in all_links]
        )
    )])
    
    fig.update_layout(
        title="Dual Role Departments<br><sub>หน่วยงานที่เป็นทั้งผู้ให้และผู้รับบริการ</sub>",
        height=800
    )
    
    return fig

def create_service_network_view(df, service_groups, color_schemes, dual_role_depts):
    """View 5: Service Network"""
    print("\n🔄 กำลังสร้าง Service Network View...")
    
    # Focus on top flows
    top_flows = df.nlargest(100, 'จำนวนเงิน (PxQ)')
    
    all_nodes = []
    all_colors = []
    node_dict = {}
    node_counter = 0
    
    # Layer 1: Providers
    providers = top_flows['ฝ่ายผู้ให้บริการ'].unique()[:15]
    for provider in providers:
        node_name = f"[P] {provider[:25]}"
        node_dict[f"p_{provider}"] = node_counter
        all_nodes.append(node_name)
        all_colors.append('#2563eb')
        node_counter += 1
    
    # Layer 2: Services from providers
    services = top_flows['บริการ'].unique()[:20]
    for service in services:
        node_name = f"[S] {service[:25]}"
        node_dict[f"s_{service}"] = node_counter
        all_nodes.append(node_name)
        service_group = top_flows[top_flows['บริการ'] == service]['service_group'].iloc[0]
        all_colors.append(color_schemes['service'].get(service_group, '#9ca3af'))
        node_counter += 1
    
    # Layer 3: Receivers
    receivers = top_flows['ฝ่ายผู้รับบริการ'].unique()[:20]
    for receiver in receivers:
        node_name = f"[R] {receiver[:25]}"
        node_dict[f"r_{receiver}"] = node_counter
        all_nodes.append(node_name)
        color = '#9333ea' if receiver in dual_role_depts else '#10b981'
        all_colors.append(color)
        node_counter += 1
    
    # Layer 4: Services from dual role receivers
    dual_receivers = [r for r in receivers if r in dual_role_depts]
    if dual_receivers:
        dual_services = df[df['ฝ่ายผู้ให้บริการ'].isin(dual_receivers)]['บริการ'].unique()[:10]
        for service in dual_services:
            node_name = f"[S2] {service[:25]}"
            if f"s2_{service}" not in node_dict:
                node_dict[f"s2_{service}"] = node_counter
                all_nodes.append(node_name)
                all_colors.append('#fbbf24')
                node_counter += 1
    
    # Links
    all_links = []
    
    # P -> S
    for _, row in top_flows.iterrows():
        if f"p_{row['ฝ่ายผู้ให้บริการ']}" in node_dict and f"s_{row['บริการ']}" in node_dict:
            all_links.append({
                'source': node_dict[f"p_{row['ฝ่ายผู้ให้บริการ']}"],
                'target': node_dict[f"s_{row['บริการ']}"],
                'value': row['จำนวนเงิน (PxQ)']
            })
    
    # S -> R
    for _, row in top_flows.iterrows():
        if f"s_{row['บริการ']}" in node_dict and f"r_{row['ฝ่ายผู้รับบริการ']}" in node_dict:
            all_links.append({
                'source': node_dict[f"s_{row['บริการ']}"],
                'target': node_dict[f"r_{row['ฝ่ายผู้รับบริการ']}"],
                'value': row['จำนวนเงิน (PxQ)']
            })
    
    # R -> S2 (for dual role)
    if dual_receivers:
        for receiver in dual_receivers:
            receiver_services = df[df['ฝ่ายผู้ให้บริการ'] == receiver].groupby('บริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(5)
            for service, value in receiver_services.items():
                if f"r_{receiver}" in node_dict and f"s2_{service}" in node_dict:
                    all_links.append({
                        'source': node_dict[f"r_{receiver}"],
                        'target': node_dict[f"s2_{service}"],
                        'value': value
                    })
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=18,
            line=dict(color="white", width=1),
            label=all_nodes,
            color=all_colors
        ),
        link=dict(
            source=[link['source'] for link in all_links],
            target=[link['target'] for link in all_links],
            value=[link['value'] for link in all_links],
            color=['rgba(0,0,0,0.15)' for _ in all_links]
        )
    )])
    
    fig.update_layout(
        title="Service Network View<br><sub>เครือข่ายบริการหลายชั้น</sub>",
        height=900
    )
    
    return fig

# Main
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
        if not Path(excel_file).exists():
            print(f"❌ ไม่พบไฟล์: {excel_file}")
            sys.exit(1)
        
        create_complete_sankey(excel_file)
    else:
        print("\n📌 วิธีใช้: python script.py your_excel_file.xlsx")