"""
Sankey Diagram Generator - Optimized for Large Datasets
รองรับข้อมูลขนาดใหญ่และมีตัวกรองข้อมูล
"""

import pandas as pd
import json
from pathlib import Path
import numpy as np

def create_sankey_from_excel(excel_file, output_file='sankey_output.html', top_n=20):
    """
    อ่านไฟล์ Excel และสร้าง Sankey Diagram เป็น HTML
    
    Parameters:
    -----------
    excel_file : str
        Path ไปยังไฟล์ Excel
    output_file : str
        ชื่อไฟล์ HTML ที่จะสร้าง
    top_n : int
        จำนวน top items ที่จะแสดง (default: 20)
    """
    
    # อ่านไฟล์ Excel
    print(f"📖 กำลังอ่านไฟล์: {excel_file}")
    df = pd.read_excel(excel_file)
    
    # ตรวจสอบชื่อคอลัมน์
    print("\n📋 คอลัมน์ที่พบในไฟล์:")
    print(df.columns.tolist())
    
    # ตรวจสอบข้อมูล
    print(f"\n📊 ข้อมูลทั้งหมด:")
    print(f"    - จำนวนแถว: {len(df):,} รายการ")
    print(f"    - มูลค่ารวม: {df['จำนวนเงิน (PxQ)'].sum():,.0f} บาท")
    
    # ===== จัดการข้อมูลขนาดใหญ่ =====
    
    # 1. รวมข้อมูลระดับฝ่าย (ลดความซับซ้อน)
    provider_receiver_sum = df.groupby(['ฝ่ายผู้ให้บริการ', 'ฝ่ายผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    provider_receiver_sum = provider_receiver_sum.sort_values('จำนวนเงิน (PxQ)', ascending=False)
    
    # 2. หา Top Providers และ Top Receivers ตามมูลค่า
    top_providers = df.groupby('ฝ่ายผู้ให้บริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(top_n).index.tolist()
    top_receivers = df.groupby('ฝ่ายผู้รับบริการ')['จำนวนเงิน (PxQ)'].sum().nlargest(top_n).index.tolist()
    
    # 3. กรองเฉพาะ Top Items
    filtered_df = provider_receiver_sum[
        (provider_receiver_sum['ฝ่ายผู้ให้บริการ'].isin(top_providers)) |
        (provider_receiver_sum['ฝ่ายผู้รับบริการ'].isin(top_receivers))
    ]
    
    # 4. รวมรายการเล็กๆ เป็น "อื่นๆ"
    threshold = filtered_df['จำนวนเงิน (PxQ)'].sum() * 0.01  # 1% ของยอดรวม
    main_items = filtered_df[filtered_df['จำนวนเงิน (PxQ)'] >= threshold].copy()
    other_items = filtered_df[filtered_df['จำนวนเงิน (PxQ)'] < threshold].copy()
    
    if len(other_items) > 0:
        # รวม items เล็กๆ ตาม provider
        for provider in other_items['ฝ่ายผู้ให้บริการ'].unique():
            provider_others = other_items[other_items['ฝ่ายผู้ให้บริการ'] == provider]
            if len(provider_others) > 0:
                other_sum = provider_others['จำนวนเงิน (PxQ)'].sum()
                main_items = pd.concat([main_items, pd.DataFrame({
                    'ฝ่ายผู้ให้บริการ': [provider],
                    'ฝ่ายผู้รับบริการ': ['หน่วยงานอื่นๆ'],
                    'จำนวนเงิน (PxQ)': [other_sum]
                })], ignore_index=True)
    
    # 5. จัดเตรียมข้อมูลสำหรับ JavaScript
    data_for_provider_view = []
    for _, row in main_items.iterrows():
        data_for_provider_view.append({
            'provider': row['ฝ่ายผู้ให้บริการ'],
            'receiver': row['ฝ่ายผู้รับบริการ'],
            'value': float(row['จำนวนเงิน (PxQ)'])
        })
        
    # <<< START: อัปเดตการจัดกลุ่มบริการตามโครงสร้างใหม่ >>>
    
    # 6. สำหรับ Service View - สร้าง Mapping จากกลุ่มบริการใหม่
    service_groups_map = {
        '1. Hard Infrastructure': [
            'DWDM (สื่อสัญญาณ)', 'Dark Fiber', 'ค่าใช้พื้นที่อาคารโทรคมนาคม', 
            'ค่าใช้ท่อร้อยสาย', 'เสาโทรคมนาคม'
        ],
        '2. International': [
            'Submarine Cable', 'ค่าใช้วงจรอินเทอร์เน็ตระหว่างประเทศ (IIG)', 
            'ค่าใช้วงจรเคเบิลใต้น้ำ'
        ],
        '3. Mobile': [
            'IPPhone', 'SIPTrunk', 'SMS', 'ค่าใช้โครงข่่าย Mobile', 'ค่าใช้โทรศัพท์ภายใน'
        ],
        '4. Fixed Line & Broadband': [
            'CPE Datacom', 'Noc', 'OLT', 'ค่า MA', 'ค่าติดตั้ง', 
            'ค่าติดตั้ง ส่วนเพิ่ม', 'ค่าติดตั้งอุปกรณ์ส่วนเพิ่ม', 'ค่าสำรวจ/ตรวจรับ',
            'ค่าใช้วงจรอินเทอร์เน็ตภายในประเทศ (IX)', 'IP Address', 'ISP',
            'ค่าใช้โครงข่าย Fixed Line', 'วงจร Broadband', 'วงจร Datacom'
        ],
        '5. Digital': [
            'Application & Software', 'Cloud', 'Cyber Security', 'IDC', 
            'NT BIG DATA', 'NT Form', 'NT Messaging', 'บริการ NT Cloud Call Center', 
            'บริการ NT Ultimate Connect', 'ออกใบรับรองอิเล็กทรอนิกส์ (NT CA)',
            'Conference', 'e-Tax'
        ],
        '7. ขาย ตลาด สนับสนุน': [
            'Adobe Creative Cloud for teams', 'Adobe Illustrator for teams', 
            'Adobe Lightroom w Classic for teams', 'Adobe Photoshop for teams',
            'Billing', 'CIP+', 'Data Warehouse', 'Debt/Debt Tracking', 'IM Web',
            'POS', 'SCOMS', 'Software Microsoft Office', 'Special Bill', 
            'Web Adjustor', 'e-Tax/e-Receipt', 
            'จัดทำ และบริหารสัญญา ประสานงานการพัฒนาการรับชำระค่าบริการ Bill Payment , DD/DC',
            'บริการ IT Helpdesk', 'บริการ Managed Service', 'บริการ NT Contact center 1888',
            'บริการ server', 'บริการจดทะเบียนโดเมนเนม แบบ .com / .net/ อื่นๆ (บาท/ครั้ง/ปี)',
            'บริการจดทะเบียนโดเมนเนม แบบ .th (บาท/ครั้ง/ปี)',
            'บริการติดตั้งเครือข่าย Intranet ในระดับ Site งาน',
            'บริการติดตั้งเครือข่าย Intranet ในระดับจุด LAN',
            'บริการพัฒนาระบบและสนับสนุนบริการ',
            'บริการพิมพ์ใบแจ้งค่าใช้บริการ บรรจุซองและส่งไปรษณีย์',
            'บริการระบบคอมพิวเตอร์',
            'บริการระบบงาน-ค่าวิทยากรในการอบรมหลักสูตรต่างๆ ที่เกี่ยวกับการใช้งานระบบงานภายใต้การดูแลของ ลคทท.',
            'บริการระบบงาน-ค่าใช้งานระบบ',
            'บริการระบบงาน-ค่าให้บริการข้อมูลตามความต้องการ (Batch) ผ่านแบบฟอร์ม CRM-004',
            'บริการระบบงาน-ค่าให้บริการคำปรึกษาการใช้งานระบบงาน อาทิ CRM, EAFS, CCDS',
            'บริการระบบงาน-ค่าให้บริการปรับปรุงข้อมูลตามความต้องการ',
            'บริการระบบงาน-ค่าให้บริการสนับสนุนการเรียกดู / เรียกใช้ข้อมูลผ่าน Web Service ที่ให้บริการผ่านระบบ ESB',
            'พิมพ์ใบแจ้งค่าใช้บริการ แผ่นพับ และส่งไปรษณีย์', 'ระบบ Web ทั่วไป',
            'ระบบงาน IT (Application)', 'ระบบงานทางด้าน FI ERP', 'ระบบงานทางด้าน HRM',
            'รับชำระค่าบริการ/ออกใบกำกับภาษี (NT eService)', 
            'ออกแบบและพัฒนาใบแจ้งค่าใช้บริการและหนังสือแจ้งลูกค้า',
            'เครื่องเช่าคอมพิวเตอร์', 'เว็บไซต์ CIMC (Unmatch, Mismatch, ปิดพอร์ตAuto)',
            'โครงสร้างพื้นฐาน', 'จัดซื้อจัดจ้าง', 'Contact Center', 'ค่าตอบแทนการขาย',
            'ค่าบริการการตลาด', 'ค่าบริหารโครงการ', 'HR', 'ค่าใช้พื้นที่สำนักงาน รวมค่าสาธารณูปโภค',
            'ค่าใช้พื้นที่ห้องจัดเลี้ยง', 'ค่าใช้ยานพาหนะ', 'บริการด้านกฎหมาย'
        ]
    }
    
    # สร้าง Reverse Mapping เพื่อความเร็ว: { 'service_name': 'group_name', ... }
    service_to_group_mapping = {}
    for group, services in service_groups_map.items():
        for service in services:
            service_to_group_mapping[service] = group
            
    # ใช้ .map() เพื่อจับคู่กลุ่มบริการ (เร็วกว่า loop มาก)
    df['service_group'] = df['บริการ'].map(service_to_group_mapping)
    
    # หากมีบริการที่ไม่เข้าพวก ให้จัดเป็น 'Others'
    df['service_group'].fillna('8. Others', inplace=True)

    # <<< END: สิ้นสุดการอัปเดต >>>

    # รวมข้อมูล service view
    service_view_data = df.groupby(['service_group', 'ฝ่ายผู้รับบริการ'])['จำนวนเงิน (PxQ)'].sum().reset_index()
    service_view_data = service_view_data[service_view_data['จำนวนเงิน (PxQ)'] > 0]
    service_view_data = service_view_data.nlargest(50, 'จำนวนเงิน (PxQ)')
    
    data_for_service_view = []
    for _, row in service_view_data.iterrows():
        data_for_service_view.append({
            'service': row['service_group'],
            'receiver': row['ฝ่ายผู้รับบริการ'],
            'value': float(row['จำนวนเงิน (PxQ)'])
        })
    
    # คำนวณสรุปข้อมูล
    total_value = df['จำนวนเงิน (PxQ)'].sum()
    unique_receivers = df['ฝ่ายผู้รับบริการ'].nunique()
    unique_providers = df['ฝ่ายผู้ให้บริการ'].nunique()
    unique_services = df['บริการ'].nunique()
    
    print(f"\n📊 สรุปข้อมูลสำหรับแสดงผล:")
    print(f"    - แสดงผู้ให้บริการ Top {len(top_providers)} จาก {unique_providers} หน่วยงาน")
    print(f"    - แสดงผู้รับบริการ Top {len(top_receivers)} จาก {unique_receivers} หน่วยงาน")
    print(f"    - จำนวน Links ที่แสดง: {len(main_items)} รายการ")
    
    # สร้าง HTML content (ส่วนนี้เหมือนเดิม ไม่ต้องแก้ไข)
    html_content = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sankey Diagram - Transfer Price Analysis</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3-sankey/0.12.3/d3-sankey.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Sarabun', 'Segoe UI', Tahoma, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 1600px;
            margin: 0 auto;
        }}
        
        h1 {{
            text-align: center;
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 32px;
            font-weight: bold;
        }}
        
        .subtitle {{
            text-align: center;
            color: #718096;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        
        .controls {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        
        .controls button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .controls button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .controls button.active {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        #chart {{
            width: 100%;
            height: 800px;
            position: relative;
            background: #fafafa;
            border-radius: 10px;
            padding: 20px;
        }}
        
        .node rect {{
            cursor: pointer;
            fill-opacity: .95;
            shape-rendering: crispEdges;
            stroke-width: 0;
            transition: fill-opacity 0.3s;
        }}
        
        .node rect:hover {{
            fill-opacity: 1;
        }}
        
        .node text {{
            pointer-events: none;
            font-size: 11px;
            font-weight: 500;
        }}
        
        .link {{
            fill: none;
            stroke-opacity: 0.3;
            transition: stroke-opacity 0.3s;
        }}
        
        .link:hover {{
            stroke-opacity: 0.6;
        }}
        
        .tooltip {{
            position: absolute;
            padding: 12px;
            font-size: 13px;
            background: rgba(0, 0, 0, 0.95);
            color: white;
            border-radius: 8px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            z-index: 1000;
            max-width: 300px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
            padding: 25px;
            background: linear-gradient(135deg, #f6f8fb 0%, #e9ecef 100%);
            border-radius: 15px;
        }}
        
        .summary-item {{
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .summary-label {{
            color: #718096;
            font-size: 12px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .summary-value {{
            color: #2d3748;
            font-size: 24px;
            font-weight: bold;
        }}
        
        .loading {{
            text-align: center;
            padding: 40px;
            color: #718096;
        }}
        
        .error {{
            background: #fed7d7;
            color: #c53030;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        
        .info-box {{
            background: #e6fffa;
            border-left: 4px solid #38b2ac;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .filter-info {{
            background: #fef5e7;
            border-left: 4px solid #f39c12;
            padding: 12px;
            margin: 15px 0;
            border-radius: 5px;
            font-size: 13px;
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Transfer Price Sankey Diagram</h1>
        <div class="subtitle">วิเคราะห์การไหลของบริการและค่าใช้จ่ายระหว่างหน่วยงาน</div>
        
        <div class="filter-info">
            ⚠️ <strong>หมายเหตุ:</strong> แสดงเฉพาะ Top {top_n} หน่วยงานที่มีมูลค่าสูงสุด จากทั้งหมด {unique_receivers} หน่วยงาน 
            เพื่อให้แสดงผลได้อย่างมีประสิทธิภาพ
        </div>
        
        <div class="controls">
            <button onclick="updateView('provider')" class="active">🏢 หน่วยงานผู้ให้บริการ</button>
            <button onclick="updateView('service')">📦 ประเภทบริการ</button>
            <button onclick="updateView('top_flow')">🔝 Top {top_n} Flows</button>
        </div>
        
        <div id="chart">
            <div class="loading">กำลังโหลดข้อมูล...</div>
        </div>
        <div class="tooltip"></div>
        
        <div class="summary">
            <div class="summary-item">
                <div class="summary-label">มูลค่ารวมทั้งหมด</div>
                <div class="summary-value">{total_value:,.0f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">ผู้ให้บริการ</div>
                <div class="summary-value">{unique_providers}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">ผู้รับบริการ</div>
                <div class="summary-value">{unique_receivers}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">ประเภทบริการ</div>
                <div class="summary-value">{unique_services}</div>
            </div>
        </div>
    </div>

    <script>
        // ข้อมูลสำหรับ Provider View
        const providerViewData = {json.dumps(data_for_provider_view, ensure_ascii=False)};
        
        // ข้อมูลสำหรับ Service View  
        const serviceViewData = {json.dumps(data_for_service_view, ensure_ascii=False)};
        
        let currentView = 'provider';
        
        function createSankey(viewType) {{
            console.log('Creating Sankey for view:', viewType);
            
            // Clear chart
            d3.select("#chart").selectAll("*").remove();
            
            let nodes = [];
            let links = [];
            let nodeMap = {{}};
            
            try {{
                if (viewType === 'provider') {{
                    // Provider → Receiver View
                    let nodeIndex = 0;
                    
                    // สร้าง unique nodes
                    providerViewData.forEach(d => {{
                        if (!nodeMap[d.provider]) {{
                            nodeMap[d.provider] = nodeIndex++;
                            nodes.push({{ name: d.provider, type: 'provider' }});
                        }}
                        if (!nodeMap[d.receiver]) {{
                            nodeMap[d.receiver] = nodeIndex++;
                            nodes.push({{ name: d.receiver, type: 'receiver' }});
                        }}
                    }});
                    
                    // สร้าง links
                    providerViewData.forEach(d => {{
                        links.push({{
                            source: nodeMap[d.provider],
                            target: nodeMap[d.receiver],
                            value: d.value,
                            provider: d.provider,
                            receiver: d.receiver
                        }});
                    }});
                    
                }} else if (viewType === 'service') {{
                    // Service → Receiver View
                    let nodeIndex = 0;
                    
                    // สร้าง unique nodes
                    serviceViewData.forEach(d => {{
                        if (!nodeMap[d.service]) {{
                            nodeMap[d.service] = nodeIndex++;
                            nodes.push({{ name: d.service, type: 'service' }});
                        }}
                        if (!nodeMap[d.receiver]) {{
                            nodeMap[d.receiver] = nodeIndex++;
                            nodes.push({{ name: d.receiver, type: 'receiver' }});
                        }}
                    }});
                    
                    // สร้าง links
                    serviceViewData.forEach(d => {{
                        links.push({{
                            source: nodeMap[d.service],
                            target: nodeMap[d.receiver],
                            value: d.value,
                            service: d.service,
                            receiver: d.receiver
                        }});
                    }});
                    
                }} else if (viewType === 'top_flow') {{
                    // Top 30 Flows
                    let nodeIndex = 0;
                    
                    // เรียงลำดับและเลือก top 30
                    let topFlows = [...providerViewData].sort((a, b) => b.value - a.value).slice(0, 30);
                    
                    topFlows.forEach(d => {{
                        if (!nodeMap[d.provider]) {{
                            nodeMap[d.provider] = nodeIndex++;
                            nodes.push({{ name: d.provider, type: 'provider' }});
                        }}
                        if (!nodeMap[d.receiver]) {{
                            nodeMap[d.receiver] = nodeIndex++;
                            nodes.push({{ name: d.receiver, type: 'receiver' }});
                        }}
                    }});
                    
                    topFlows.forEach(d => {{
                        links.push({{
                            source: nodeMap[d.provider],
                            target: nodeMap[d.receiver],
                            value: d.value,
                            provider: d.provider,
                            receiver: d.receiver
                        }});
                    }});
                }}
                
                console.log('Nodes:', nodes.length, 'Links:', links.length);
                
                if (nodes.length === 0 || links.length === 0) {{
                    throw new Error('ไม่มีข้อมูลสำหรับการแสดงผล');
                }}
                
                // สร้าง Sankey diagram
                const margin = {{ top: 10, right: 200, bottom: 10, left: 200 }};
                const width = document.getElementById('chart').offsetWidth - margin.left - margin.right;
                const height = 760 - margin.top - margin.bottom;
                
                const svg = d3.select("#chart")
                    .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform", `translate(${{margin.left}},${{margin.top}})`);
                
                // สร้าง sankey layout
                const sankey = d3.sankey()
                    .nodeId(d => d.index)
                    .nodeWidth(20)
                    .nodePadding(10)
                    .extent([[0, 0], [width, height]]);
                
                // Apply sankey algorithm
                const graph = sankey({{
                    nodes: nodes.map(d => Object.assign({{}}, d)),
                    links: links.map(d => Object.assign({{}}, d))
                }});
                
                console.log('Graph generated:', graph);
                
                // Color scale
                const color = d3.scaleOrdinal()
                    .domain(['provider', 'service', 'receiver'])
                    .range(['#4299e1', '#48bb78', '#ed8936']);
                
                const nodeColor = d3.scaleOrdinal(d3.schemeSet3);
                
                // Tooltip
                const tooltip = d3.select(".tooltip");
                
                // Draw links
                const link = svg.append("g")
                    .selectAll(".link")
                    .data(graph.links)
                    .enter().append("path")
                    .attr("class", "link")
                    .attr("d", d3.sankeyLinkHorizontal())
                    .style("stroke", d => nodeColor(d.source.name))
                    .style("stroke-width", d => Math.max(1, d.width))
                    .on("mouseover", function(event, d) {{
                        tooltip.style("opacity", 1)
                            .html(`
                                <strong>${{d.source.name}}</strong> → <strong>${{d.target.name}}</strong><br/>
                                <span style="color: #ffd700;">💰 มูลค่า: ${{d.value.toLocaleString()}} บาท</span>
                            `)
                            .style("left", (event.pageX + 10) + "px")
                            .style("top", (event.pageY - 28) + "px");
                    }})
                    .on("mouseout", function() {{
                        tooltip.style("opacity", 0);
                    }});
                
                // Draw nodes
                const node = svg.append("g")
                    .selectAll(".node")
                    .data(graph.nodes)
                    .enter().append("g")
                    .attr("class", "node");
                
                node.append("rect")
                    .attr("x", d => d.x0)
                    .attr("y", d => d.y0)
                    .attr("height", d => Math.max(1, d.y1 - d.y0))
                    .attr("width", d => d.x1 - d.x0)
                    .style("fill", d => nodeColor(d.name))
                    .on("mouseover", function(event, d) {{
                        const incoming = d.targetLinks ? d.targetLinks.reduce((sum, l) => sum + l.value, 0) : 0;
                        const outgoing = d.sourceLinks ? d.sourceLinks.reduce((sum, l) => sum + l.value, 0) : 0;
                        
                        let html = `<strong>${{d.name}}</strong><br/>`;
                        if (incoming > 0) html += `📥 รับเข้า: ${{incoming.toLocaleString()}} บาท<br/>`;
                        if (outgoing > 0) html += `📤 ส่งออก: ${{outgoing.toLocaleString()}} บาท`;
                        
                        tooltip.style("opacity", 1)
                            .html(html)
                            .style("left", (event.pageX + 10) + "px")
                            .style("top", (event.pageY - 28) + "px");
                    }})
                    .on("mouseout", function() {{
                        tooltip.style("opacity", 0);
                    }});
                
                // Add labels
                node.append("text")
                    .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
                    .attr("y", d => (d.y1 + d.y0) / 2)
                    .attr("dy", "0.35em")
                    .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
                    .text(d => {{
                        // ตัดข้อความยาว
                        const maxLength = 30;
                        return d.name.length > maxLength ? 
                            d.name.substring(0, maxLength) + "..." : d.name;
                    }})
                    .style("font-size", "11px")
                    .style("fill", "#2d3748");
                    
            }} catch (error) {{
                console.error('Error creating Sankey:', error);
                d3.select("#chart")
                    .append("div")
                    .attr("class", "error")
                    .html(`⚠️ เกิดข้อผิดพลาด: ${{error.message}}`);
            }}
        }}
        
        function updateView(viewType) {{
            currentView = viewType;
            
            // Update button states
            document.querySelectorAll('.controls button').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            createSankey(viewType);
        }}
        
        // Initialize with provider view
        window.addEventListener('DOMContentLoaded', function() {{
            createSankey('provider');
        }});
    </script>
</body>
</html>'''
    
    # บันทึกไฟล์ HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ สร้าง Sankey Diagram เสร็จสิ้น!")
    print(f"📁 ไฟล์ถูกบันทึกที่: {output_file}")
    print(f"🌐 เปิดไฟล์นี้ในเบราว์เซอร์เพื่อดูผลลัพธ์")
    
    # แนะนำเพิ่มเติมสำหรับข้อมูลขนาดใหญ่
    if len(df) > 1000:
        print(f"\n💡 เนื่องจากข้อมูลมีขนาด {len(df):,} รายการ:")
        print(f"    - ระบบจะแสดงเฉพาะ Top {top_n} หน่วยงาน")
        print(f"    - รายการเล็กๆ จะถูกรวมเป็น 'หน่วยงานอื่นๆ'")
        print(f"    - หากต้องการดู Top อื่นๆ แก้ไข parameter: top_n")
    
    return output_file


# ==========================================
# Main Function (ส่วนนี้เหมือนเดิม)
# ==========================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("🎯 Sankey Diagram Generator - Large Dataset Edition")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
        
        # ตรวจสอบไฟล์
        if not Path(excel_file).exists():
            print(f"❌ ไม่พบไฟล์: {excel_file}")
            sys.exit(1)
        
        # D3.js method
        top_n = input("จำนวน Top หน่วยงานที่จะแสดง (default=20): ").strip()
        top_n = int(top_n) if top_n else 20
        create_sankey_from_excel(excel_file, top_n=top_n)
    else:
        print("\n📌 วิธีใช้งาน:")
        print("    python your_script_name.py your_file.xlsx")
