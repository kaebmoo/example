import pandas as pd
import json
from pathlib import Path
import sys
import webbrowser
import numpy as np

def prepare_dashboard_data(df):
    """
    เตรียมข้อมูลทั้งหมดให้อยู่ในรูปแบบ JSON ที่เหมาะสมสำหรับแดชบอร์ด D3.js
    """
    # แปลงค่า NaN เป็น string "Unknown" เพื่อป้องกันปัญหา
    df = df.fillna({
        'provider_line': 'Unknown',
        'provider_dept': 'Unknown', 
        'receiver_line': 'Unknown',
        'receiver_dept': 'Unknown',
        'service': 'Unknown Service'
    })
    
    # 1. สร้าง Lists ที่ไม่ซ้ำกันสำหรับใช้สร้าง Filter
    filters_data = {
        "provider_lines": sorted([str(x) for x in df['provider_line'].unique().tolist()]),
        "provider_depts": sorted([str(x) for x in df['provider_dept'].unique().tolist()]),
        "receiver_lines": sorted([str(x) for x in df['receiver_line'].unique().tolist()]),
        "receiver_depts": sorted([str(x) for x in df['receiver_dept'].unique().tolist()]),
    }

    # 2. สร้างข้อมูลความสัมพันธ์ระหว่างสายงานและฝ่ายสำหรับ Dynamic Filter
    line_dept_map = {
        "provider": {},
        "receiver": {}
    }
    
    # แปลงเป็น dict ด้วยการ loop เพื่อจัดการ serialization
    provider_map = df.groupby('provider_line')['provider_dept'].unique()
    for line, depts in provider_map.items():
        line_dept_map["provider"][str(line)] = [str(d) for d in depts.tolist()]
    
    receiver_map = df.groupby('receiver_line')['receiver_dept'].unique()
    for line, depts in receiver_map.items():
        line_dept_map["receiver"][str(line)] = [str(d) for d in depts.tolist()]

    # 3. เตรียมข้อมูลธุรกรรมทั้งหมดสำหรับ D3.js
    transactions_data = []
    for _, row in df.iterrows():
        transactions_data.append({
            'provider_line': str(row['provider_line']),
            'provider_dept': str(row['provider_dept']),
            'receiver_line': str(row['receiver_line']),
            'receiver_dept': str(row['receiver_dept']),
            'service': str(row['service']),
            'amount': float(row['amount']) if not pd.isna(row['amount']) else 0
        })

    # 4. สร้างข้อมูล Hierarchy สำหรับ Edge Bundling ล่วงหน้าใน Python
    all_lines = set(df['provider_line'].unique()) | set(df['receiver_line'].unique())
    
    line_to_depts = {}
    for line in all_lines:
        line_str = str(line)
        depts_p = set(df[df['provider_line'] == line]['provider_dept'].unique())
        depts_r = set(df[df['receiver_line'] == line]['receiver_dept'].unique())
        all_depts = depts_p | depts_r
        # แปลงเป็น string และ sort
        line_to_depts[line_str] = sorted([str(d) for d in all_depts])

    bundling_hierarchy = {
        "name": "root",
        "children": [
            {
                "name": line,
                "children": [{"name": dept} for dept in depts]
            }
            for line, depts in sorted(line_to_depts.items()) if depts
        ]
    }

    # 5. รวมข้อมูลทั้งหมดเป็น JSON object เดียว
    return {
        "filters": filters_data,
        "line_dept_map": line_dept_map,
        "transactions": transactions_data,
        "bundling_hierarchy": bundling_hierarchy
    }

def generate_interactive_dashboard_html(data, output_file):
    """
    สร้างไฟล์ HTML ที่เป็นแดชบอร์ดแบบครบวงจร
    """
    # ใช้ json.dumps แบบ safe เพื่อจัดการกับ characters พิเศษ
    json_data = json.dumps(data, ensure_ascii=False, indent=None)
    
    html_template = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Interactive Transfer Price Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        :root {{
            --bg-color: #f0f2f5;
            --panel-bg: #ffffff;
            --text-color: #333;
            --primary-color: #007bff;
            --border-color: #dee2e6;
            --shadow: 0 4px 8px rgba(0,0,0,0.05);
        }}
        body {{
            font-family: 'Sarabun', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            background-color: var(--bg-color);
            color: var(--text-color);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}
        .sidebar {{
            width: 320px;
            padding: 20px;
            background-color: var(--panel-bg);
            box-shadow: var(--shadow);
            overflow-y: auto;
            border-right: 1px solid var(--border-color);
            z-index: 10;
        }}
        .sidebar h2 {{
            font-size: 1.2rem;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .sidebar .filter-group, .sidebar .vis-group {{
            margin-bottom: 25px;
        }}
        .sidebar label {{
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }}
        .sidebar select, .sidebar button {{
            width: 100%;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background-color: #fff;
            font-size: 0.9rem;
        }}
        .sidebar button {{
            background-color: #e9ecef;
            cursor: pointer;
            text-align: left;
            margin-top: 5px;
            transition: background-color 0.2s;
        }}
        .sidebar button.active {{
            background-color: var(--primary-color);
            color: white;
            font-weight: bold;
            border-color: var(--primary-color);
        }}
        .sidebar button:hover:not(.active) {{
            background-color: #ced4da;
        }}
        .main-content {{
            flex-grow: 1;
            padding: 20px;
            display: flex;
            flex-direction: column;
            position: relative;
        }}
        #chart-container {{
            flex-grow: 1;
            background-color: var(--panel-bg);
            box-shadow: var(--shadow);
            border-radius: 8px;
            position: relative;
            padding: 20px;
        }}
        svg {{
            width: 100%;
            height: 100%;
        }}
        .loading-overlay {{
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(255,255,255,0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 1.2rem;
            color: #555;
            z-index: 10;
            border-radius: 8px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .stat-card {{
            text-align: center;
            padding: 10px;
            background: white;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }}
        .stat-card h4 {{
            margin: 0 0 5px 0;
            font-size: 0.8rem;
            color: #666;
        }}
        .stat-card .value {{
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary-color);
        }}
        /* D3 specific styles */
        .node text {{ 
            font: 10px sans-serif; 
            text-shadow: 0 1px 0 #fff, 0 -1px 0 #fff, 1px 0 0 #fff, -1px 0 0 #fff;
        }}
        .link {{ 
            fill: none; 
            stroke: #999;
            stroke-opacity: 0.6;
        }}
        .chord-ribbon {{ 
            fill-opacity: 0.7; 
        }}
        .tooltip {{
            position: absolute;
            text-align: left;
            padding: 8px;
            font-size: 12px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            pointer-events: none;
            z-index: 100;
        }}
    </style>
</head>
<body>
    <aside class="sidebar">
        <h2>📊 Dashboard Controls</h2>
        
        <div class="vis-group">
            <label>Visualization Type</label>
            <button id="btn-chord" class="vis-btn active">Chord Diagram</button>
            <button id="btn-force" class="vis-btn">Force-Directed Graph</button>
            <button id="btn-tree" class="vis-btn">Tidy Tree</button>
            <button id="btn-radialtree" class="vis-btn">Radial Tree</button>
            <button id="btn-bundling" class="vis-btn">Edge Bundling</button>
        </div>

        <div class="filter-group">
            <h3>🔍 Filters</h3>
            <label for="filter-provider-line">สายงานผู้ให้บริการ</label>
            <select id="filter-provider-line"></select>

            <label for="filter-provider-dept">ฝ่ายผู้ให้บริการ</label>
            <select id="filter-provider-dept"></select>

            <label for="filter-receiver-line">สายงานผู้รับบริการ</label>
            <select id="filter-receiver-line"></select>

            <label for="filter-receiver-dept">ฝ่ายผู้รับบริการ</label>
            <select id="filter-receiver-dept"></select>
            
            <button id="reset-filters" style="margin-top: 15px; background-color: #dc3545; color: white;">
                🔄 Reset Filters
            </button>
        </div>
    </aside>

    <main class="main-content">
        <div id="stats-container" class="stats"></div>
        <div id="chart-container">
            <div class="loading-overlay">Loading...</div>
        </div>
    </main>

    <script>
        const fullData = {json_data};
        let currentVis = 'chord';
        let tooltip = null;

        // Initialize tooltip
        function initTooltip() {{
            tooltip = d3.select("body").append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);
        }}

        // --- Statistics Display ---
        function updateStats(data) {{
            const totalAmount = d3.sum(data, d => d.amount);
            const uniqueProviders = new Set(data.map(d => d.provider_dept)).size;
            const uniqueReceivers = new Set(data.map(d => d.receiver_dept)).size;
            const uniqueServices = new Set(data.map(d => d.service)).size;
            
            const statsHtml = `
                <div class="stat-card">
                    <h4>Total Records</h4>
                    <div class="value">${{data.length.toLocaleString()}}</div>
                </div>
                <div class="stat-card">
                    <h4>Total Amount</h4>
                    <div class="value">${{totalAmount.toLocaleString('th-TH', {{maximumFractionDigits: 0}})}} ฿</div>
                </div>
                <div class="stat-card">
                    <h4>Providers</h4>
                    <div class="value">${{uniqueProviders}}</div>
                </div>
                <div class="stat-card">
                    <h4>Receivers</h4>
                    <div class="value">${{uniqueReceivers}}</div>
                </div>
                <div class="stat-card">
                    <h4>Services</h4>
                    <div class="value">${{uniqueServices}}</div>
                </div>
            `;
            
            document.getElementById('stats-container').innerHTML = statsHtml;
        }}

        // --- D3 Visualization Functions ---
        
        function renderChord(container, data) {{
            try {{
                // Aggregate data by provider and receiver departments
                const df_agg = d3.rollup(data, v => d3.sum(v, d => d.amount), d => d.provider_dept, d => d.receiver_dept);
                const all_depts = Array.from(new Set(data.flatMap(d => [d.provider_dept, d.receiver_dept]))).sort();
                
                if (all_depts.length === 0) {{
                    throw new Error("No departments to display.");
                }}
                
                const dept_map = new Map(all_depts.map((d, i) => [d, i]));
                const matrix_size = all_depts.length;
                const matrix = Array.from({{length: matrix_size}}, () => Array(matrix_size).fill(0));
                
                df_agg.forEach((receivers, provider) => {{
                    receivers.forEach((amount, receiver) => {{
                        const p_idx = dept_map.get(provider);
                        const r_idx = dept_map.get(receiver);
                        if (p_idx !== undefined && r_idx !== undefined) {{
                            matrix[p_idx][r_idx] = amount;
                        }}
                    }});
                }});
                
                const width = container.clientWidth - 40;
                const height = container.clientHeight - 40;
                const outerRadius = Math.min(width, height) * 0.5 - 150;
                const innerRadius = outerRadius - 20;
                
                const svg = d3.select(container).html("").append("svg")
                    .attr("viewBox", [-width / 2, -height / 2, width, height]);

                const chord = d3.chordDirected()
                    .padAngle(0.04)
                    .sortSubgroups(d3.descending);
                    
                const arc = d3.arc()
                    .innerRadius(innerRadius)
                    .outerRadius(outerRadius);
                    
                const ribbon = d3.ribbon()
                    .radius(innerRadius);
                    
                const color = d3.scaleOrdinal(all_depts, d3.schemeTableau10);

                const chords = chord(matrix);
                
                // Groups
                const group = svg.append("g").selectAll("g")
                    .data(chords.groups)
                    .join("g");
                    
                group.append("path")
                    .attr("fill", d => color(all_depts[d.index]))
                    .attr("d", arc)
                    .on("mouseover", function(event, d) {{
                        tooltip.transition().duration(200).style("opacity", .9);
                        const total_out = d3.sum(matrix[d.index]);
                        const total_in = d3.sum(matrix, row => row[d.index]);
                        tooltip.html(`<strong>${{all_depts[d.index]}}</strong><br/>
                            Outgoing: ${{total_out.toLocaleString('th-TH', {{maximumFractionDigits:0}})}} ฿<br/>
                            Incoming: ${{total_in.toLocaleString('th-TH', {{maximumFractionDigits:0}})}} ฿`)
                            .style("left", (event.pageX + 10) + "px")
                            .style("top", (event.pageY - 28) + "px");
                    }})
                    .on("mouseout", function() {{
                        tooltip.transition().duration(500).style("opacity", 0);
                    }});
                    
                // Labels
                group.append("text")
                    .each(d => {{ d.angle = (d.startAngle + d.endAngle) / 2; }})
                    .attr("dy", ".35em")
                    .attr("transform", d => `
                        rotate(${{d.angle * 180 / Math.PI - 90}})
                        translate(${{outerRadius + 5}})
                        ${{d.angle > Math.PI ? "rotate(180)" : ""}}
                    `)
                    .attr("text-anchor", d => d.angle > Math.PI ? "end" : null)
                    .text(d => {{
                        const name = all_depts[d.index];
                        return name.length > 25 ? name.substring(0, 23) + '...' : name;
                    }})
                    .style("font-size", "10px");

                // Ribbons
                svg.append("g")
                    .attr("fill-opacity", 0.7)
                    .selectAll("path")
                    .data(chords)
                    .join("path")
                    .attr("d", ribbon)
                    .attr("fill", d => color(all_depts[d.source.index]))
                    .attr("stroke", "white")
                    .on("mouseover", function(event, d) {{
                        tooltip.transition().duration(200).style("opacity", .9);
                        tooltip.html(`${{all_depts[d.source.index]}} → ${{all_depts[d.target.index]}}<br/>
                            Amount: ${{d.source.value.toLocaleString('th-TH', {{maximumFractionDigits:0}})}} ฿`)
                            .style("left", (event.pageX + 10) + "px")
                            .style("top", (event.pageY - 28) + "px");
                    }})
                    .on("mouseout", function() {{
                        tooltip.transition().duration(500).style("opacity", 0);
                    }});
                    
            }} catch (error) {{
                console.error("Error in renderChord:", error);
                throw error;
            }}
        }}
        
        function renderTree(container, data, isRadial = false) {{
            try {{
                // Create hierarchy from data
                const hierarchy = {{"name": "Organization", "children": []}};
                const lineMap = new Map();
                
                data.forEach(d => {{
                    if (!lineMap.has(d.provider_line)) {{
                        lineMap.set(d.provider_line, new Map());
                    }}
                    const deptMap = lineMap.get(d.provider_line);
                    
                    if (!deptMap.has(d.provider_dept)) {{
                        deptMap.set(d.provider_dept, new Map());
                    }}
                    const serviceMap = deptMap.get(d.provider_dept);
                    
                    if (!serviceMap.has(d.service)) {{
                        serviceMap.set(d.service, 0);
                    }}
                    serviceMap.set(d.service, serviceMap.get(d.service) + d.amount);
                }});
                
                lineMap.forEach((deptMap, lineName) => {{
                    const lineNode = {{"name": lineName, "children": []}};
                    deptMap.forEach((serviceMap, deptName) => {{
                        const deptNode = {{"name": deptName, "children": []}};
                        serviceMap.forEach((amount, serviceName) => {{
                            deptNode.children.push({{"name": serviceName, "value": amount}});
                        }});
                        if (deptNode.children.length > 0) {{
                            lineNode.children.push(deptNode);
                        }}
                    }});
                    if (lineNode.children.length > 0) {{
                        hierarchy.children.push(lineNode);
                    }}
                }});
                
                if (hierarchy.children.length === 0) {{
                    throw new Error("Not enough data to build a tree.");
                }}
                
                const width = container.clientWidth - 40;
                const height = container.clientHeight - 40;
                const svg = d3.select(container).html("").append("svg");

                const root = d3.hierarchy(hierarchy)
                    .sum(d => d.value || 0)
                    .sort((a, b) => b.value - a.value);
                
                let g, linkGenerator;
                const layout = isRadial 
                    ? d3.tree().size([2 * Math.PI, Math.min(width, height) / 2 - 150])
                    : d3.tree().size([height - 40, width - 300]);
                    
                layout(root);

                if (isRadial) {{
                    svg.attr("viewBox", [-width / 2, -height / 2, width, height]);
                    g = svg.append("g");
                    linkGenerator = d3.linkRadial().angle(d => d.x).radius(d => d.y);
                }} else {{
                    svg.attr("viewBox", [0, 0, width, height]);
                    g = svg.append("g").attr("transform", `translate(150, 20)`);
                    linkGenerator = d3.linkHorizontal().x(d => d.y).y(d => d.x);
                }}
                
                // Links
                g.append("g")
                    .attr("fill", "none")
                    .attr("stroke", "#555")
                    .attr("stroke-opacity", 0.4)
                    .attr("stroke-width", 1.5)
                    .selectAll("path")
                    .data(root.links())
                    .join("path")
                    .attr("d", linkGenerator);

                // Nodes
                const node = g.append("g")
                    .selectAll("g")
                    .data(root.descendants())
                    .join("g")
                    .attr("transform", d => {{
                        if (isRadial) {{
                            return `rotate(${{d.x * 180 / Math.PI - 90}}) translate(${{d.y}},0)`;
                        }} else {{
                            return `translate(${{d.y}},${{d.x}})`;
                        }}
                    }});
                
                node.append("circle")
                    .attr("fill", d => d.children ? "#555" : "#999")
                    .attr("r", d => d.children ? 4 : 3);
                    
                node.append("text")
                    .attr("dy", "0.31em")
                    .attr("x", d => {{
                        if (isRadial) {{
                            return d.x < Math.PI === !d.children ? 6 : -6;
                        }} else {{
                            return d.children ? -8 : 8;
                        }}
                    }})
                    .attr("text-anchor", d => {{
                        if (isRadial) {{
                            return d.x < Math.PI === !d.children ? "start" : "end";
                        }} else {{
                            return d.children ? "end" : "start";
                        }}
                    }})
                    .attr("transform", d => isRadial && d.x >= Math.PI ? "rotate(180)" : null)
                    .text(d => d.data.name)
                    .style("font-size", "10px");
                    
            }} catch (error) {{
                console.error("Error in renderTree:", error);
                throw error;
            }}
        }}

        function renderForce(container, data) {{
            try {{
                const links_data = d3.rollup(data, v => d3.sum(v, d => d.amount), d => d.provider_dept, d => d.receiver_dept);
                const nodes = Array.from(new Set(data.flatMap(d => [d.provider_dept, d.receiver_dept]))).map(id => ({{id}}));
                
                if (nodes.length === 0) {{
                    throw new Error("No departments to display.");
                }}
                
                const links = [];
                links_data.forEach((targets, source) => {{
                    targets.forEach((value, target) => {{
                        links.push({{source, target, value}});
                    }});
                }});
                
                const width = container.clientWidth - 40;
                const height = container.clientHeight - 40;
                const svg = d3.select(container).html("").append("svg")
                    .attr("viewBox", [0, 0, width, height]);

                const simulation = d3.forceSimulation(nodes)
                    .force("link", d3.forceLink(links).id(d => d.id).distance(100))
                    .force("charge", d3.forceManyBody().strength(-300))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .force("collision", d3.forceCollide().radius(30));

                const link = svg.append("g")
                    .attr("stroke", "#999")
                    .attr("stroke-opacity", 0.6)
                    .selectAll("line")
                    .data(links)
                    .join("line")
                    .attr("stroke-width", d => Math.sqrt(d.value / 10000) + 0.5);

                const color = d3.scaleOrdinal(d3.schemeCategory10);
                
                const node = svg.append("g")
                    .selectAll("g")
                    .data(nodes)
                    .join("g")
                    .call(drag(simulation));
                
                node.append("circle")
                    .attr("r", 8)
                    .attr("fill", d => color(d.id.substring(0, 10)))
                    .attr("stroke", "#fff")
                    .attr("stroke-width", 1.5);
                
                node.append("text")
                    .text(d => d.id.length > 20 ? d.id.substring(0, 18) + "..." : d.id)
                    .attr("x", 12)
                    .attr("y", 3)
                    .style("font-size", "10px");
                
                node.on("mouseover", function(event, d) {{
                    tooltip.transition().duration(200).style("opacity", .9);
                    tooltip.html(`<strong>${{d.id}}</strong>`)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 28) + "px");
                }})
                .on("mouseout", function() {{
                    tooltip.transition().duration(500).style("opacity", 0);
                }});

                simulation.on("tick", () => {{
                    link.attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                    
                    node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
                }});

                function drag(simulation) {{
                    return d3.drag()
                        .on("start", (event, d) => {{
                            if (!event.active) simulation.alphaTarget(0.3).restart();
                            d.fx = d.x;
                            d.fy = d.y;
                        }})
                        .on("drag", (event, d) => {{
                            d.fx = event.x;
                            d.fy = event.y;
                        }})
                        .on("end", (event, d) => {{
                            if (!event.active) simulation.alphaTarget(0);
                            d.fx = null;
                            d.fy = null;
                        }});
                }}
            }} catch (error) {{
                console.error("Error in renderForce:", error);
                throw error;
            }}
        }}
        
        function renderBundling(container, data) {{
            try {{
                const width = container.clientWidth - 40;
                const height = container.clientHeight - 40;
                const radius = Math.min(width, height) / 2 - 150;
                
                const svg = d3.select(container).html("").append("svg")
                    .attr("viewBox", [-width/2, -height/2, width, height]);

                const tree = d3.cluster()
                    .size([2 * Math.PI, radius]);
                    
                const root = tree(d3.hierarchy(fullData.bundling_hierarchy)
                    .sort((a, b) => d3.ascending(a.data.name, b.data.name)));
                    
                const map = new Map(root.leaves().map(d => [d.data.name, d]));
                
                // Create links from data
                const links_data = d3.rollup(data, v => d3.sum(v, d => d.amount), d => d.provider_dept, d => d.receiver_dept);
                const links = [];
                links_data.forEach((targets, source) => {{
                    targets.forEach((value, target) => {{
                        const sourceNode = map.get(source);
                        const targetNode = map.get(target);
                        if (sourceNode && targetNode) {{
                            links.push({{source: sourceNode, target: targetNode, value}});
                        }}
                    }});
                }});

                const line = d3.lineRadial()
                    .curve(d3.curveBundle.beta(0.85))
                    .radius(d => d.y)
                    .angle(d => d.x);
                    
                const color = d3.scaleOrdinal(d3.schemeCategory10);
                
                // Draw outer arc
                svg.append("g")
                    .selectAll("path")
                    .data(root.leaves())
                    .join("path")
                    .attr("d", d => `M${{d3.pointRadial(d.x, d.y)}}L${{d3.pointRadial(d.x, radius + 10)}}`)
                    .attr("stroke", "#000")
                    .attr("stroke-opacity", 0.2);

                // Add labels
                svg.append("g")
                    .selectAll("text")
                    .data(root.leaves())
                    .join("text")
                    .attr("transform", d => `
                        rotate(${{d.x * 180 / Math.PI - 90}}) 
                        translate(${{radius + 15}},0)
                        ${{d.x > Math.PI ? " rotate(180)" : ""}}
                    `)
                    .attr("dy", "0.31em")
                    .attr("text-anchor", d => d.x > Math.PI ? "end" : "start")
                    .text(d => d.data.name)
                    .style("font-size", "9px");

                // Draw links
                svg.append("g")
                    .attr("stroke-opacity", 0.4)
                    .attr("fill", "none")
                    .selectAll("path")
                    .data(links)
                    .join("path")
                    .attr("d", d => line(d.source.path(d.target)))
                    .attr("stroke", d => color(d.source.parent.data.name))
                    .attr("stroke-width", d => Math.max(0.5, Math.sqrt(d.value / 50000)));
                    
            }} catch (error) {{
                console.error("Error in renderBundling:", error);
                throw error;
            }}
        }}

        // --- UI & Filtering Logic ---

        function populateFilters() {{
            const filters = fullData.filters;
            const lineDeptMap = fullData.line_dept_map;

            ['provider', 'receiver'].forEach(type => {{
                const lineSelect = document.getElementById(`filter-${{type}}-line`);
                const deptSelect = document.getElementById(`filter-${{type}}-dept`);
                
                // Populate line select
                lineSelect.innerHTML = '<option value="all">All</option>';
                filters[`${{type}}_lines`].forEach(val => {{
                    const option = document.createElement('option');
                    option.value = val;
                    option.textContent = val;
                    lineSelect.appendChild(option);
                }});

                // Add change handler for line select
                lineSelect.addEventListener('change', function() {{
                    const selectedLine = this.value;
                    deptSelect.innerHTML = '<option value="all">All</option>';
                    
                    if (selectedLine !== 'all' && lineDeptMap[type][selectedLine]) {{
                        lineDeptMap[type][selectedLine].forEach(dept => {{
                            const option = document.createElement('option');
                            option.value = dept;
                            option.textContent = dept;
                            deptSelect.appendChild(option);
                        }});
                    }} else {{
                        // Show all departments if "All" is selected
                        filters[`${{type}}_depts`].forEach(dept => {{
                            const option = document.createElement('option');
                            option.value = dept;
                            option.textContent = dept;
                            deptSelect.appendChild(option);
                        }});
                    }}
                    
                    updateVisualization();
                }});
                
                // Populate department select initially
                deptSelect.innerHTML = '<option value="all">All</option>';
                filters[`${{type}}_depts`].forEach(dept => {{
                    const option = document.createElement('option');
                    option.value = dept;
                    option.textContent = dept;
                    deptSelect.appendChild(option);
                }});
                
                deptSelect.addEventListener('change', updateVisualization);
            }});
            
            // Reset filters button
            document.getElementById('reset-filters').addEventListener('click', function() {{
                document.getElementById('filter-provider-line').value = 'all';
                document.getElementById('filter-provider-dept').value = 'all';
                document.getElementById('filter-receiver-line').value = 'all';
                document.getElementById('filter-receiver-dept').value = 'all';
                
                // Re-populate department dropdowns
                populateFilters();
                updateVisualization();
            }});
        }}

        function getFilteredData() {{
            const providerLine = document.getElementById('filter-provider-line').value;
            const providerDept = document.getElementById('filter-provider-dept').value;
            const receiverLine = document.getElementById('filter-receiver-line').value;
            const receiverDept = document.getElementById('filter-receiver-dept').value;
            
            return fullData.transactions.filter(d => 
                (providerLine === 'all' || d.provider_line === providerLine) &&
                (providerDept === 'all' || d.provider_dept === providerDept) &&
                (receiverLine === 'all' || d.receiver_line === receiverLine) &&
                (receiverDept === 'all' || d.receiver_dept === receiverDept)
            );
        }}

        function updateVisualization() {{
            const container = document.getElementById('chart-container');
            container.innerHTML = '<div class="loading-overlay">Rendering...</div>';
            
            const filteredData = getFilteredData();
            
            if (filteredData.length === 0) {{
                container.innerHTML = '<div class="loading-overlay">❌ No data for selected filters.</div>';
                updateStats([]);
                return;
            }}
            
            updateStats(filteredData);

            setTimeout(() => {{
                try {{
                    switch (currentVis) {{
                        case 'chord': 
                            renderChord(container, filteredData); 
                            break;
                        case 'tree': 
                            renderTree(container, filteredData, false); 
                            break;
                        case 'radialtree': 
                            renderTree(container, filteredData, true); 
                            break;
                        case 'force': 
                            renderForce(container, filteredData); 
                            break;
                        case 'bundling': 
                            renderBundling(container, filteredData); 
                            break;
                        default: 
                            throw new Error("Visualization not implemented yet.");
                    }}
                }} catch (error) {{
                    console.error("D3 Render Error:", error);
                    container.innerHTML = `<div class="loading-overlay">❌ Error: ${{error.message}}</div>`;
                }}
            }}, 100);
        }}

        // --- Initial Setup ---

        document.addEventListener('DOMContentLoaded', () => {{
            initTooltip();
            populateFilters();
            
            // Visualization buttons
            document.querySelectorAll('.vis-btn').forEach(btn => {{
                btn.addEventListener('click', function() {{
                    document.querySelectorAll('.vis-btn').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    currentVis = this.id.replace('btn-', '');
                    updateVisualization();
                }});
            }});
            
            updateVisualization();
        }});

    </script>
</body>
</html>'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ Successfully generated: {output_file}")

def main():
    """Main function to run the script."""
    print("=" * 60)
    print("Interactive D3.js Visualization Dashboard Generator")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python advanced_visualizations.py <path_to_your_excel_file.xlsx>")
        print("\nExample: python advanced_visualizations.py data.xlsx")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"\n❌ Error: File not found at '{input_file}'")
        sys.exit(1)

    print(f"\n📁 Reading and processing data from: {input_file.name}")
    
    try:
        # Read Excel file
        df = pd.read_excel(input_file)
        print(f"✅ Loaded {len(df)} rows from Excel file")
        
        # Define column mapping
        column_mapping = {
            'สายงานผู้ให้บริการ': 'provider_line', 
            'ฝ่ายผู้ให้บริการ': 'provider_dept',
            'สายงานผู้รับบริการ': 'receiver_line', 
            'ฝ่ายผู้รับบริการ': 'receiver_dept',
            'บริการ': 'service', 
            'จำนวนเงิน (PxQ)': 'amount'
        }
        
        # Check required columns
        required_cols = list(column_mapping.keys())
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"\n❌ Error: Missing required columns in Excel file:")
            for col in missing_cols:
                print(f"   - {col}")
            print("\nRequired columns are:")
            for col in required_cols:
                print(f"   ✓ {col}")
            sys.exit(1)
        
        # Rename columns
        df.rename(columns=column_mapping, inplace=True)
        
        # Clean amount column
        df['amount'] = pd.to_numeric(
            df['amount'].astype(str).str.replace(',', '', regex=True), 
            errors='coerce'
        ).fillna(0)
        
        # Remove rows where amount is 0 or negative
        initial_count = len(df)
        df = df[df['amount'] > 0]
        removed_count = initial_count - len(df)
        if removed_count > 0:
            print(f"⚠️  Removed {removed_count} rows with invalid amounts")
        
        # Fill NaN values with appropriate defaults
        df = df.fillna({
            'provider_line': 'Unknown',
            'provider_dept': 'Unknown',
            'receiver_line': 'Unknown', 
            'receiver_dept': 'Unknown',
            'service': 'Unknown Service'
        })
        
        print(f"✅ Data cleaned and processed: {len(df)} valid rows")
        
        # Prepare dashboard data
        dashboard_data = prepare_dashboard_data(df)
        
        # Generate output file
        output_filename = input_file.stem + "_dashboard.html"
        print(f"\n🎨 Generating interactive dashboard: {output_filename}")
        generate_interactive_dashboard_html(dashboard_data, output_filename)
        
        print(f"\n✅ Success! Dashboard has been generated: {output_filename}")
        
        # Try to open in browser
        try:
            full_path = Path(output_filename).absolute()
            webbrowser.open(f"file://{full_path}")
            print(f"🌐 Opening dashboard in your default web browser...")
        except Exception as e:
            print(f"⚠️  Could not automatically open the file: {e}")
            print(f"   Please open '{output_filename}' in a web browser manually.")
            
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()