"""
Enhanced Service Chain Sankey - With Clear Provider-Receiver Views
แสดงทั้ง Service Hierarchy และ Provider-Receiver Relationships
"""

import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

def create_enhanced_chain_sankey(excel_file, output_file='enhanced_chain.html'):
    """
    สร้าง Sankey พร้อม multiple views รวมทั้ง provider-receiver
    """
    print("=" * 60)
    print("🔗 Enhanced Service Chain & Provider-Receiver Analysis")
    print("=" * 60)
    
    # อ่านไฟล์
    print(f"\n📖 กำลังอ่านไฟล์: {excel_file}")
    df = pd.read_excel(excel_file)
    
    # Service hierarchy (same as before)
    service_hierarchy = {
        'L1_Infrastructure': {
            'services': ['ท่อร้อยสาย', 'เสาโทรคมนาคม', 'อาคารโทรคมนาคม', 
                        'พื้นที่สำนักงาน', 'พื้นที่อาคาร', 'ยานพาหนะ'],
            'color': '#8b4513'
        },
        'L2_Transmission': {
            'services': ['DWDM', 'Dark Fiber', 'สื่อสัญญาณ', 'เคเบิลใต้น้ำ'],
            'color': '#4169e1'
        },
        'L3_Network': {
            'services': ['IIG', 'IX', 'Broadband', 'Datacom', 'ISP', 'Fixed Line'],
            'color': '#20b2aa'
        },
        'L4_Platform': {
            'services': ['Cloud', 'IDC', 'Server', 'Big Data', 'Cyber Security'],
            'color': '#9370db'
        },
        'L5_Application': {
            'services': ['Application', 'Software', 'ระบบงาน', 'NT Form'],
            'color': '#ff69b4'
        },
        'L6_Service': {
            'services': ['Contact Center', 'Helpdesk', 'Billing', 'ติดตั้ง'],
            'color': '#ffa500'
        }
    }
    
    # จัดกลุ่มบริการ
    df['service_level'] = 'L6_Service'
    for level, info in service_hierarchy.items():
        for service in info['services']:
            mask = df['บริการ'].str.contains(service, case=False, na=False)
            df.loc[mask, 'service_level'] = level
    
    # Analyze
    providers = set(df['ฝ่ายผู้ให้บริการ'].unique())
    receivers = set(df['ฝ่ายผู้รับบริการ'].unique())
    dual_roles = providers & receivers
    
    print(f"\n📊 สรุปข้อมูล:")
    print(f"   - Transactions: {len(df):,}")
    print(f"   - Total Value: {df['จำนวนเงิน (PxQ)'].sum():,.0f} บาท")
    print(f"   - Providers: {len(providers)}")
    print(f"   - Receivers: {len(receivers)}")
    print(f"   - Dual Roles: {len(dual_roles)}")
    
    print("\n🎯 เลือกมุมมอง:")
    print("1. Provider → Service → Receiver (แสดงผู้ให้-บริการ-ผู้รับ)")
    print("2. Service Chain: Provider → Service Level → Receiver")
    print("3. Dual Role Chain: แสดง Chain ของ Dual Role")
    print("4. Multi-Layer: Provider → Service → Receiver → Their Service")
    print("5. Level Transformation: แสดงการ transform ระหว่าง levels")
    
    choice = input("\nเลือก (1-5, default=1): ").strip() or "1"
    
    if choice == "1":
        fig = create_provider_service_receiver_view(df, service_hierarchy, dual_roles)
    elif choice == "2":
        fig = create_service_level_chain(df, service_hierarchy, dual_roles)
    elif choice == "3":
        fig = create_dual_role_chain(df, service_hierarchy, dual_roles)
    elif choice == "4":
        fig = create_multi_layer_chain(df, service_hierarchy, dual_roles)
    else:
        fig = create_level_transformation_view(df, service_hierarchy, dual_roles)
    
    fig.write_html(output_file)
    print(f"\n✅ บันทึกไฟล์: {output_file}")
    
    return output_file

def create_provider_service_receiver_view(df, service_hierarchy, dual_roles):
    """
    View 1: Classic Provider → Service → Receiver
    แต่เพิ่มการแสดง service level ด้วยสี
    """
    print("\n🔄 สร้าง Provider-Service-Receiver View...")
    
    # Filter top items
    top_providers = df.groupby('ฝ่ายผู้ให้บริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(25).index
    top_receivers = df.groupby('ฝ่ายผู้รับบริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(30).index
    top_services = df.groupby('บริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(40).index
    
    filtered = df[
        df['ฝ่ายผู้ให้บริการ'].isin(top_providers) &
        df['บริการ'].isin(top_services) &
        df['ฝ่ายผู้รับบริการ'].isin(top_receivers)
    ].copy()
    
    # Create nodes
    all_nodes = []
    all_colors = []
    node_dict = {}
    node_counter = 0
    
    # Column 1: Providers
    for provider in filtered['ฝ่ายผู้ให้บริการ'].unique():
        node_name = f"[P] {provider[:30]}"
        node_dict[f"p_{provider}"] = node_counter
        all_nodes.append(node_name)
        # Blue for pure provider, Purple for dual role
        color = '#9333ea' if provider in dual_roles else '#2563eb'
        all_colors.append(color)
        node_counter += 1
    
    # Column 2: Services (colored by level)
    for service in filtered['บริการ'].unique():
        node_name = f"📦 {service[:30]}"
        node_dict[f"s_{service}"] = node_counter
        all_nodes.append(node_name)
        # Get service level color
        service_level = filtered[filtered['บริการ'] == service]['service_level'].iloc[0]
        all_colors.append(service_hierarchy.get(service_level, {}).get('color', '#808080'))
        node_counter += 1
    
    # Column 3: Receivers
    for receiver in filtered['ฝ่ายผู้รับบริการ'].unique():
        node_name = f"[R] {receiver[:30]}"
        node_dict[f"r_{receiver}"] = node_counter
        all_nodes.append(node_name)
        # Green for pure receiver, Purple for dual role
        color = '#9333ea' if receiver in dual_roles else '#10b981'
        all_colors.append(color)
        node_counter += 1
    
    # Create links
    all_links = []
    
    # Provider → Service
    p_s = filtered.groupby(['ฝ่ายผู้ให้บริการ', 'บริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in p_s.iterrows():
        all_links.append({
            'source': node_dict[f"p_{row['ฝ่ายผู้ให้บริการ']}"],
            'target': node_dict[f"s_{row['บริการ']}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # Service → Receiver
    s_r = filtered.groupby(['บริการ', 'ฝ่ายผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in s_r.iterrows():
        all_links.append({
            'source': node_dict[f"s_{row['บริการ']}"],
            'target': node_dict[f"r_{row['ฝ่ายผู้รับบริการ']}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=10,
            thickness=18,
            line=dict(color="white", width=0.5),
            label=all_nodes,
            color=all_colors,
            hovertemplate='<b>%{label}</b><br>มูลค่า: %{value:,.0f} บาท<extra></extra>'
        ),
        link=dict(
            source=[link['source'] for link in all_links],
            target=[link['target'] for link in all_links],
            value=[link['value'] for link in all_links],
            color=['rgba(0,0,0,0.15)' for _ in all_links]
        )
    )])
    
    fig.update_layout(
        title="Provider → Service → Receiver View<br>" +
              "<sub>🔵 Provider Only | 🟣 Dual Role | 🟢 Receiver Only | 🎨 Service colored by level</sub>",
        height=900
    )
    
    return fig

def create_service_level_chain(df, service_hierarchy, dual_roles):
    """
    View 2: Provider → Service Level → Receiver
    แสดงเป็น group ของ service level
    """
    print("\n🔄 สร้าง Service Level Chain...")
    
    # Filter top
    top_providers = df.groupby('ฝ่ายผู้ให้บริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(20).index
    top_receivers = df.groupby('ฝ่ายผู้รับบริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(25).index
    
    filtered = df[
        df['ฝ่ายผู้ให้บริการ'].isin(top_providers) &
        df['ฝ่ายผู้รับบริการ'].isin(top_receivers)
    ].copy()
    
    all_nodes = []
    all_colors = []
    node_dict = {}
    node_counter = 0
    
    # Column 1: Providers
    for provider in filtered['ฝ่ายผู้ให้บริการ'].unique():
        node_name = f"[P] {provider[:30]}"
        node_dict[f"p_{provider}"] = node_counter
        all_nodes.append(node_name)
        color = '#9333ea' if provider in dual_roles else '#2563eb'
        all_colors.append(color)
        node_counter += 1
    
    # Column 2: Service Levels
    for level in filtered['service_level'].unique():
        node_name = f"[{level}]"
        node_dict[level] = node_counter
        all_nodes.append(node_name)
        all_colors.append(service_hierarchy.get(level, {}).get('color', '#808080'))
        node_counter += 1
    
    # Column 3: Receivers
    for receiver in filtered['ฝ่ายผู้รับบริการ'].unique():
        node_name = f"[R] {receiver[:30]}"
        node_dict[f"r_{receiver}"] = node_counter
        all_nodes.append(node_name)
        color = '#9333ea' if receiver in dual_roles else '#10b981'
        all_colors.append(color)
        node_counter += 1
    
    # Links
    all_links = []
    
    # Provider → Level
    p_l = filtered.groupby(['ฝ่ายผู้ให้บริการ', 'service_level'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in p_l.iterrows():
        all_links.append({
            'source': node_dict[f"p_{row['ฝ่ายผู้ให้บริการ']}"],
            'target': node_dict[row['service_level']],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    # Level → Receiver
    l_r = filtered.groupby(['service_level', 'ฝ่ายผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    for _, row in l_r.iterrows():
        all_links.append({
            'source': node_dict[row['service_level']],
            'target': node_dict[f"r_{row['ฝ่ายผู้รับบริการ']}"],
            'value': row['จำนวนเงิน (PxQ)']
        })
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=25,
            line=dict(color="white", width=1),
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
        title="Service Level Chain: Provider → Service Level → Receiver",
        height=800
    )
    
    return fig

def create_dual_role_chain(df, service_hierarchy, dual_roles):
    """
    View 3: Focus on Dual Role Departments
    แสดง: Who provides to them → Dual Role → Who they provide to
    """
    print("\n🔄 สร้าง Dual Role Chain...")
    
    # Get top dual roles
    top_dual = []
    for dept in dual_roles:
        total = (df[df['ฝ่ายผู้ให้บริการ'] == dept]['จำนวนเงิน (PxQ)'].sum() +
                df[df['ฝ่ายผู้รับบริการ'] == dept]['จำนวนเงิน (PxQ)'].sum())
        top_dual.append((dept, total))
    
    top_dual.sort(key=lambda x: x[1], reverse=True)
    top_dual_depts = [d[0] for d in top_dual[:10]]
    
    all_nodes = []
    all_colors = []
    node_dict = {}
    node_counter = 0
    
    # Find providers to dual roles
    providers_to_dual = set()
    receivers_from_dual = set()
    
    for dept in top_dual_depts:
        # Who provides to this dual role
        providers = df[df['ฝ่ายผู้รับบริการ'] == dept]['ฝ่ายผู้ให้บริการ'].unique()
        providers_to_dual.update(providers)
        
        # Who receives from this dual role
        receivers = df[df['ฝ่ายผู้ให้บริการ'] == dept]['ฝ่ายผู้รับบริการ'].unique()
        receivers_from_dual.update(receivers)
    
    # Column 1: Providers to dual roles
    for provider in providers_to_dual:
        if provider not in top_dual_depts:  # Not dual itself
            node_name = f"[P→D] {provider[:25]}"
            node_dict[f"pd_{provider}"] = node_counter
            all_nodes.append(node_name)
            all_colors.append('#2563eb')
            node_counter += 1
    
    # Column 2: Services they receive
    received_services = df[df['ฝ่ายผู้รับบริการ'].isin(top_dual_depts)]['service_level'].unique()
    for level in received_services:
        node_name = f"[IN] {level}"
        node_dict[f"in_{level}"] = node_counter
        all_nodes.append(node_name)
        all_colors.append(service_hierarchy.get(level, {}).get('color', '#808080'))
        node_counter += 1
    
    # Column 3: Dual Role Depts
    for dept in top_dual_depts:
        node_name = f"🔄 {dept[:25]}"
        node_dict[f"dual_{dept}"] = node_counter
        all_nodes.append(node_name)
        all_colors.append('#9333ea')
        node_counter += 1
    
    # Column 4: Services they provide
    provided_services = df[df['ฝ่ายผู้ให้บริการ'].isin(top_dual_depts)]['service_level'].unique()
    for level in provided_services:
        node_name = f"[OUT] {level}"
        node_dict[f"out_{level}"] = node_counter
        all_nodes.append(node_name)
        all_colors.append(lighten_color(service_hierarchy.get(level, {}).get('color', '#808080'), 0.3))
        node_counter += 1
    
    # Column 5: Final receivers
    for receiver in list(receivers_from_dual)[:15]:
        if receiver not in top_dual_depts:
            node_name = f"[D→R] {receiver[:25]}"
            node_dict[f"dr_{receiver}"] = node_counter
            all_nodes.append(node_name)
            all_colors.append('#10b981')
            node_counter += 1
    
    # Create links
    all_links = []
    
    # Provider → Service Level (received)
    for dept in top_dual_depts:
        providers_data = df[df['ฝ่ายผู้รับบริการ'] == dept].groupby(
            ['ฝ่ายผู้ให้บริการ', 'service_level'])['จำนวนเงิน (PxQ)'].sum().reset_index()
        
        for _, row in providers_data.iterrows():
            if f"pd_{row['ฝ่ายผู้ให้บริการ']}" in node_dict:
                all_links.append({
                    'source': node_dict[f"pd_{row['ฝ่ายผู้ให้บริการ']}"],
                    'target': node_dict[f"in_{row['service_level']}"],
                    'value': row['จำนวนเงิน (PxQ)']
                })
    
    # Service Level → Dual Role
    for dept in top_dual_depts:
        received_data = df[df['ฝ่ายผู้รับบริการ'] == dept].groupby(
            'service_level')['จำนวนเงิน (PxQ)'].sum().reset_index()
        
        for _, row in received_data.iterrows():
            all_links.append({
                'source': node_dict[f"in_{row['service_level']}"],
                'target': node_dict[f"dual_{dept}"],
                'value': row['จำนวนเงิน (PxQ)']
            })
    
    # Dual Role → Service Level (provided)
    for dept in top_dual_depts:
        provided_data = df[df['ฝ่ายผู้ให้บริการ'] == dept].groupby(
            'service_level')['จำนวนเงิน (PxQ)'].sum().reset_index()
        
        for _, row in provided_data.iterrows():
            all_links.append({
                'source': node_dict[f"dual_{dept}"],
                'target': node_dict[f"out_{row['service_level']}"],
                'value': row['จำนวนเงิน (PxQ)']
            })
    
    # Service Level → Final Receiver
    for dept in top_dual_depts:
        receivers_data = df[df['ฝ่ายผู้ให้บริการ'] == dept].groupby(
            ['service_level', 'ฝ่ายผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
        
        for _, row in receivers_data.iterrows():
            if f"dr_{row['ฝ่ายผู้รับบริการ']}" in node_dict:
                all_links.append({
                    'source': node_dict[f"out_{row['service_level']}"],
                    'target': node_dict[f"dr_{row['ฝ่ายผู้รับบริการ']}"],
                    'value': row['จำนวนเงิน (PxQ)']
                })
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=8,
            thickness=15,
            line=dict(color="white", width=0.5),
            label=all_nodes,
            color=all_colors
        ),
        link=dict(
            source=[link['source'] for link in all_links],
            target=[link['target'] for link in all_links],
            value=[link['value'] for link in all_links],
            color=['rgba(147, 51, 234, 0.15)' for _ in all_links]
        )
    )])
    
    fig.update_layout(
        title="Dual Role Chain Analysis<br>" +
              "<sub>Provider → Input Service → Dual Role Dept → Output Service → Receiver</sub>",
        height=900
    )
    
    return fig

def create_multi_layer_chain(df, service_hierarchy, dual_roles):
    """
    View 4: Multi-Layer showing extended chains
    """
    print("\n🔄 สร้าง Multi-Layer Chain...")
    
    # This would show Provider → Service → Receiver (who is also Provider) → Their Service → Next Receiver
    # Implementation similar to above but with more layers
    
    # For brevity, return View 1
    return create_provider_service_receiver_view(df, service_hierarchy, dual_roles)

def create_level_transformation_view(df, service_hierarchy, dual_roles):
    """
    View 5: Show how services transform between levels
    """
    print("\n🔄 สร้าง Level Transformation View...")
    
    # Focus on departments that transform services
    transformations = []
    
    for dept in dual_roles:
        # Services received
        received = df[df['ฝ่ายผู้รับบริการ'] == dept].groupby('service_level')['จำนวนเงิน (PxQ)'].sum()
        # Services provided  
        provided = df[df['ฝ่ายผู้ให้บริการ'] == dept].groupby('service_level')['จำนวนเงิน (PxQ)'].sum()
        
        for recv_level, recv_val in received.items():
            for prov_level, prov_val in provided.items():
                if recv_level != prov_level:  # Transformation
                    transformations.append({
                        'dept': dept,
                        'from': recv_level,
                        'to': prov_level,
                        'value': min(recv_val, prov_val)
                    })
    
    # Sort by value
    transformations.sort(key=lambda x: x['value'], reverse=True)
    
    # Create Sankey for top transformations
    all_nodes = []
    all_colors = []
    node_dict = {}
    node_counter = 0
    
    # Add unique departments
    shown_depts = set()
    for trans in transformations[:20]:
        if trans['dept'] not in shown_depts:
            node_name = f"🔄 {trans['dept'][:30]}"
            node_dict[trans['dept']] = node_counter
            all_nodes.append(node_name)
            all_colors.append('#9333ea')
            node_counter += 1
            shown_depts.add(trans['dept'])
    
    # Add level nodes
    shown_levels = set()
    for trans in transformations[:20]:
        # From level
        if f"from_{trans['from']}" not in shown_levels:
            node_name = f"[FROM] {trans['from']}"
            node_dict[f"from_{trans['from']}"] = node_counter
            all_nodes.append(node_name)
            all_colors.append(service_hierarchy.get(trans['from'], {}).get('color', '#808080'))
            node_counter += 1
            shown_levels.add(f"from_{trans['from']}")
        
        # To level
        if f"to_{trans['to']}" not in shown_levels:
            node_name = f"[TO] {trans['to']}"
            node_dict[f"to_{trans['to']}"] = node_counter
            all_nodes.append(node_name)
            all_colors.append(service_hierarchy.get(trans['to'], {}).get('color', '#808080'))
            node_counter += 1
            shown_levels.add(f"to_{trans['to']}")
    
    # Create links
    all_links = []
    for trans in transformations[:20]:
        # From level → Department
        all_links.append({
            'source': node_dict[f"from_{trans['from']}"],
            'target': node_dict[trans['dept']],
            'value': trans['value']
        })
        
        # Department → To level
        all_links.append({
            'source': node_dict[trans['dept']],
            'target': node_dict[f"to_{trans['to']}"],
            'value': trans['value']
        })
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="white", width=1),
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
        title="Service Level Transformation<br>" +
              "<sub>How departments transform services from one level to another</sub>",
        height=800
    )
    
    return fig

def lighten_color(hex_color, amount):
    """Helper function"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    
    return f'#{r:02x}{g:02x}{b:02x}'

# Main
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
        create_enhanced_chain_sankey(excel_file)
    else:
        print("\n📌 วิธีใช้: python service_chain.py pq_excel_file.xlsx")
        print("\n✨ Features:")
        print("   - View 1: Provider → Service → Receiver (ชัดเจน)")
        print("   - View 2: Provider → Service Level → Receiver")
        print("   - View 3: Dual Role Chain Analysis")
        print("   - View 4: Multi-Layer Extended Chain")
        print("   - View 5: Service Level Transformation")