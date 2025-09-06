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
    
    provider_map = df.groupby('provider_line')['provider_dept'].unique()
    for line, depts in provider_map.items():
        line_dept_map["provider"][str(line)] = sorted([str(d) for d in depts.tolist()])
    
    receiver_map = df.groupby('receiver_line')['receiver_dept'].unique()
    for line, depts in receiver_map.items():
        line_dept_map["receiver"][str(line)] = sorted([str(d) for d in depts.tolist()])

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
            
            <button id="reset-filters" style="margin-top: 15px; background-color: #6c757d; color: white;">
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

        function initTooltip() {{
            tooltip = d3.select("body").append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);
        }}

        function updateStats(data) {{
            const totalAmount = d3.sum(data, d => d.amount);
            const uniqueProviders = new Set(data.map(d => d.provider_dept)).size;
            const uniqueReceivers = new Set(data.map(d => d.receiver_dept)).size;
            const uniqueServices = new Set(data.map(d => d.service)).size;
            
            const statsHtml = `
                <div class="stat-card"><h4>Total Records</h4><div class="value">${{data.length.toLocaleString()}}</div></div>
                <div class="stat-card"><h4>Total Amount</h4><div class="value">${{totalAmount.toLocaleString('th-TH', {{maximumFractionDigits: 0}})}} ฿</div></div>
                <div class="stat-card"><h4>Providers</h4><div class="value">${{uniqueProviders}}</div></div>
                <div class="stat-card"><h4>Receivers</h4><div class="value">${{uniqueReceivers}}</div></div>
                <div class="stat-card"><h4>Services</h4><div class="value">${{uniqueServices}}</div></div>
            `;
            document.getElementById('stats-container').innerHTML = statsHtml;
        }}

        // --- D3 Visualization Functions ---
        
        function renderChord(container, data) {{
            try {{
                const df_agg = d3.rollup(data, v => d3.sum(v, d => d.amount), d => d.provider_dept, d => d.receiver_dept);
                const all_depts = Array.from(new Set(data.flatMap(d => [d.provider_dept, d.receiver_dept]))).sort();
                
                if (all_depts.length === 0) throw new Error("No departments to display.");
                
                const dept_map = new Map(all_depts.map((d, i) => [d, i]));
                const matrix = Array.from({{length: all_depts.length}}, () => Array(all_depts.length).fill(0));
                
                df_agg.forEach((receivers, provider) => {{
                    receivers.forEach((amount, receiver) => {{
                        const p_idx = dept_map.get(provider);
                        const r_idx = dept_map.get(receiver);
                        if (p_idx !== undefined && r_idx !== undefined) matrix[p_idx][r_idx] = amount;
                    }});
                }});
                
                const width = container.clientWidth;
                const height = container.clientHeight;
                const outerRadius = Math.min(width, height) * 0.5 - 150;
                const innerRadius = outerRadius - 15;
                
                const svg = d3.select(container).html("").append("svg").attr("viewBox", [-width / 2, -height / 2, width, height]);

                const chord = d3.chordDirected().padAngle(0.04).sortSubgroups(d3.descending);
                const arc = d3.arc().innerRadius(innerRadius).outerRadius(outerRadius);
                const ribbon = d3.ribbon().radius(innerRadius);
                const color = d3.scaleOrdinal(all_depts, d3.schemeTableau10);
                const chords = chord(matrix);
                
                const group = svg.append("g").selectAll("g").data(chords.groups).join("g");
                group.append("path").attr("fill", d => color(all_depts[d.index])).attr("d", arc)
                    .on("mouseover", (event, d) => {{
                        tooltip.transition().duration(200).style("opacity", .9);
                        const total_out = d3.sum(matrix[d.index]);
                        const total_in = d3.sum(matrix, row => row[d.index]);
                        tooltip.html(`<strong>${{all_depts[d.index]}}</strong><br/>Outgoing: ${{total_out.toLocaleString('th-TH',{{maximumFractionDigits:0}})}} ฿<br/>Incoming: ${{total_in.toLocaleString('th-TH',{{maximumFractionDigits:0}})}} ฿`).style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
                    }}).on("mouseout", () => tooltip.transition().duration(500).style("opacity", 0));
                    
                group.append("text").each(d => {{ d.angle = (d.startAngle + d.endAngle) / 2; }})
                    .attr("dy", ".35em").attr("transform", d => `rotate(${{d.angle * 180 / Math.PI - 90}}) translate(${{outerRadius + 5}}) ${{d.angle > Math.PI ? "rotate(180)" : ""}}`)
                    .attr("text-anchor", d => d.angle > Math.PI ? "end" : null)
                    .text(d => {{ const name = all_depts[d.index]; return name.length > 25 ? name.substring(0, 23) + '...' : name; }});

                svg.append("g").attr("class", "chord-ribbon").selectAll("path").data(chords).join("path")
                    .attr("d", ribbon).attr("fill", d => color(all_depts[d.source.index]))
                    .on("mouseover", (event, d) => {{
                        tooltip.transition().duration(200).style("opacity", .9);
                        tooltip.html(`${{all_depts[d.source.index]}} → ${{all_depts[d.target.index]}}<br/>Amount: ${{d.source.value.toLocaleString('th-TH',{{maximumFractionDigits:0}})}} ฿`).style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
                    }}).on("mouseout", () => tooltip.transition().duration(500).style("opacity", 0));
            }} catch (error) {{ console.error("Error in renderChord:", error); throw error; }}
        }}
        
        function renderTree(container, data, isRadial = false) {{
            try {{
                // Robustly create hierarchy from filtered data
                const hierarchyData = [{{ id: "root", parentId: null, name: "All Providers" }}];
                const nodeIds = new Set(["root"]);

                data.forEach(d => {{
                    if (!d.provider_line || !d.provider_dept || !d.service) return;
                    const l1 = `L1|${{d.provider_line}}`;
                    const l2 = `L2|${{d.provider_line}}|${{d.provider_dept}}`;
                    const l3 = `L3|${{d.provider_line}}|${{d.provider_dept}}|${{d.service}}`;
                    
                    if (!nodeIds.has(l1)) {{ hierarchyData.push({{ id: l1, parentId: "root", name: d.provider_line }}); nodeIds.add(l1); }}
                    if (!nodeIds.has(l2)) {{ hierarchyData.push({{ id: l2, parentId: l1, name: d.provider_dept }}); nodeIds.add(l2); }}
                    if (!nodeIds.has(l3)) {{ hierarchyData.push({{ id: l3, parentId: l2, name: d.service, value: d.amount }}); nodeIds.add(l3); }}
                }});

                if (hierarchyData.length <= 1) throw new Error("Not enough hierarchical data to build a tree.");

                const root = d3.stratify()(hierarchyData)
                    .sum(d => d.value || 0) // Sum values from leaf nodes
                    .sort((a, b) => b.value - a.value);

                const width = container.clientWidth;
                const height = container.clientHeight;
                const svg = d3.select(container).html("").append("svg");
                const layout = isRadial 
                    ? d3.tree().size([2 * Math.PI, Math.min(width, height) / 2 - 150])
                    : d3.tree().size([height - 40, width - 400]);
                layout(root);
                
                let g, linkGenerator;
                if (isRadial) {{
                    svg.attr("viewBox", [-width / 2, -height / 2, width, height]);
                    g = svg.append("g");
                    linkGenerator = d3.linkRadial().angle(d => d.x).radius(d => d.y);
                }} else {{
                    svg.attr("viewBox", [0, 0, width, height]);
                    g = svg.append("g").attr("transform", `translate(150, 20)`);
                    linkGenerator = d3.linkHorizontal().x(d => d.y).y(d => d.x);
                }}
                
                g.append("g").attr("fill", "none").attr("stroke", "#555").attr("stroke-opacity", 0.4).attr("stroke-width", 1.5)
                    .selectAll("path").data(root.links()).join("path").attr("d", linkGenerator);

                const node = g.append("g").selectAll("g").data(root.descendants()).join("g")
                    .attr("transform", d => isRadial ? `rotate(${{d.x * 180 / Math.PI - 90}}) translate(${{d.y}},0)` : `translate(${{d.y}},${{d.x}})`);
                
                node.append("circle").attr("fill", d => d.children ? "#555" : "#999").attr("r", 4);
                
                node.append("text").attr("dy", "0.31em")
                    .attr("x", d => isRadial ? (d.x < Math.PI ? 8 : -8) : (d.children ? -8 : 8))
                    .attr("text-anchor", d => isRadial ? (d.x < Math.PI ? "start" : "end") : (d.children ? "end" : "start"))
                    .attr("transform", d => isRadial && d.x >= Math.PI ? "rotate(180)" : null)
                    .text(d => d.data.name)
                    .on("mouseover", (event, d) => {{
                        tooltip.transition().duration(200).style("opacity", .9);
                        tooltip.html(`<strong>${{d.data.name}}</strong><br/>Amount: ${{d.value.toLocaleString('th-TH',{{maximumFractionDigits:0}})}} ฿`).style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
                    }}).on("mouseout", () => tooltip.transition().duration(500).style("opacity", 0));

            }} catch (error) {{ console.error("Error in renderTree:", error); throw error; }}
        }}

        function renderForce(container, data) {{
            try {{
                const links_data = d3.rollup(data, v => d3.sum(v, d => d.amount), d => d.provider_dept, d => d.receiver_dept);
                const nodes = Array.from(new Set(data.flatMap(d => [d.provider_dept, d.receiver_dept]))).map(id => ({{id}}));
                if (nodes.length === 0) throw new Error("No departments to display.");
                
                const links = [];
                links_data.forEach((targets, source) => {{
                    targets.forEach((value, target) => links.push({{source, target, value}}));
                }});
                
                const width = container.clientWidth;
                const height = container.clientHeight;
                const svg = d3.select(container).html("").append("svg").attr("viewBox", [0, 0, width, height]);

                const simulation = d3.forceSimulation(nodes)
                    .force("link", d3.forceLink(links).id(d => d.id).distance(100))
                    .force("charge", d3.forceManyBody().strength(-200))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .force("collision", d3.forceCollide().radius(20));

                const link = svg.append("g").attr("stroke", "#999").attr("stroke-opacity", 0.6)
                    .selectAll("line").data(links).join("line")
                    .attr("stroke-width", d => Math.max(0.5, Math.sqrt(d.value / 10000)));

                const color = d3.scaleOrdinal(d3.schemeCategory10);
                const node = svg.append("g").selectAll("g").data(nodes).join("g").call(drag(simulation));
                
                node.append("circle").attr("r", 10).attr("fill", d => color(d.id.substring(0, 10))).attr("stroke", "#fff").attr("stroke-width", 1.5);
                node.append("text").text(d => d.id.length > 20 ? d.id.substring(0, 18) + "..." : d.id).attr("x", 12).attr("y", 3);
                node.on("mouseover", (event, d) => {{ tooltip.transition().duration(200).style("opacity", .9); tooltip.html(`<strong>${{d.id}}</strong>`).style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px"); }})
                    .on("mouseout", () => tooltip.transition().duration(500).style("opacity", 0));

                simulation.on("tick", () => {{
                    link.attr("x1", d => d.source.x).attr("y1", d => d.source.y).attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                    node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
                }});

                function drag(simulation) {{
                    return d3.drag()
                        .on("start", (e, d) => {{ if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }})
                        .on("drag", (e, d) => {{ d.fx = e.x; d.fy = e.y; }})
                        .on("end", (e, d) => {{ if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }});
                }}
            }} catch (error) {{ console.error("Error in renderForce:", error); throw error; }}
        }}
        
        function renderBundling(container, data) {{
            try {{
                const links_data = d3.rollup(data, v => d3.sum(v, d => d.amount), d => d.provider_dept, d => d.receiver_dept);
                const links = [];
                links_data.forEach((targets, source) => {{
                    targets.forEach((value, target) => links.push({{source, target, value}}));
                }});
                
                const width = container.clientWidth;
                const height = container.clientHeight;
                const radius = Math.min(width, height) / 2;
                const svg = d3.select(container).html("").append("svg").attr("viewBox", [-radius, -radius, width, height]);

                const tree = d3.cluster().size([2 * Math.PI, radius - 130]);
                const root = tree(d3.hierarchy(fullData.bundling_hierarchy).sort((a, b) => d3.ascending(a.data.name, b.data.name)));
                const map = new Map(root.leaves().map(d => [d.data.name, d]));
                
                const bundledLinks = links.map(l => ({{source: map.get(l.source), target: map.get(l.target), value: l.value}})).filter(l => l.source && l.target);
                if (links.length > 0 && bundledLinks.length === 0) console.warn("Could not map any links for bundling.");

                const line = d3.lineRadial().curve(d3.curveBundle.beta(0.85)).radius(d => d.y).angle(d => d.x);
                const color = d3.scaleOrdinal(root.data.children.map(d => d.name), d3.schemeTableau10);
                
                svg.append("g").selectAll("text").data(root.leaves()).join("text")
                    .attr("transform", d => `rotate(${{d.x * 180 / Math.PI - 90}}) translate(${{radius - 120}},0)${{d.x > Math.PI ? " rotate(180)" : ""}}`)
                    .attr("dy", "0.31em").attr("text-anchor", d => d.x > Math.PI ? "end" : "start")
                    .text(d => d.data.name).style("font-size", "9px");

                svg.append("g").attr("stroke-opacity", 0.5).attr("fill", "none").selectAll("path").data(bundledLinks).join("path")
                    .attr("d", d => line(d.source.path(d.target)))
                    .attr("stroke", d => color(d.source.parent.data.name))
                    .attr("stroke-width", d => Math.max(0.5, Math.sqrt(d.value / 50000)));
            }} catch (error) {{ console.error("Error in renderBundling:", error); throw error; }}
        }}

        // --- UI & Filtering Logic ---

        function populateFilters() {{
            const filters = fullData.filters;
            const lineDeptMap = fullData.line_dept_map;

            ['provider', 'receiver'].forEach(type => {{
                const lineSelect = document.getElementById(`filter-${{type}}-line`);
                const deptSelect = document.getElementById(`filter-${{type}}-dept`);
                lineSelect.innerHTML = '<option value="all">All</option>';
                filters[`${{type}}_lines`].forEach(val => {{
                    const option = document.createElement('option');
                    option.value = val;
                    option.textContent = val;
                    lineSelect.appendChild(option);
                }});
                lineSelect.addEventListener('change', function() {{
                    const selectedLine = this.value;
                    deptSelect.innerHTML = '<option value="all">All</option>';
                    const depts = selectedLine === 'all' ? filters[`${{type}}_depts`] : (lineDeptMap[type][selectedLine] || []);
                    depts.forEach(dept => {{
                        const option = document.createElement('option');
                        option.value = dept;
                        option.textContent = dept;
                        deptSelect.appendChild(option);
                    }});
                    updateVisualization();
                }});
                deptSelect.innerHTML = '<option value="all">All</option>';
                filters[`${{type}}_depts`].forEach(dept => {{
                    const option = document.createElement('option');
                    option.value = dept;
                    option.textContent = dept;
                    deptSelect.appendChild(option);
                }});
                deptSelect.addEventListener('change', updateVisualization);
            }});
            
            document.getElementById('reset-filters').addEventListener('click', function() {{
                ['provider-line', 'provider-dept', 'receiver-line', 'receiver-dept'].forEach(id => document.getElementById(`filter-${{id}}`).value = 'all');
                document.getElementById('filter-provider-line').dispatchEvent(new Event('change'));
                document.getElementById('filter-receiver-line').dispatchEvent(new Event('change'));
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
                        case 'chord': renderChord(container, filteredData); break;
                        case 'tree': renderTree(container, filteredData, false); break;
                        case 'radialtree': renderTree(container, filteredData, true); break;
                        case 'force': renderForce(container, filteredData); break;
                        case 'bundling': renderBundling(container, filteredData); break;
                        default: throw new Error("Visualization not implemented yet.");
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
        df = pd.read_excel(input_file)
        print(f"✅ Loaded {len(df)} rows from Excel file")
        
        column_mapping = {
            'สายงานผู้ให้บริการ': 'provider_line', 
            'ฝ่ายผู้ให้บริการ': 'provider_dept',
            'สายงานผู้รับบริการ': 'receiver_line', 
            'ฝ่ายผู้รับบริการ': 'receiver_dept',
            'บริการ': 'service', 
            'จำนวนเงิน (PxQ)': 'amount'
        }
        
        required_cols = list(column_mapping.keys())
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"\n❌ Error: Missing required columns in Excel file:")
            for col in missing_cols: print(f"   - {col}")
            sys.exit(1)
        
        df.rename(columns=column_mapping, inplace=True)
        
        df['amount'] = pd.to_numeric(df['amount'].astype(str).str.replace(',', '', regex=True), errors='coerce').fillna(0)
        
        initial_count = len(df)
        df = df[df['amount'] > 0]
        if initial_count > len(df):
            print(f"⚠️  Removed {initial_count - len(df)} rows with invalid amounts")
        
        dashboard_data = prepare_dashboard_data(df)
        
        output_filename = input_file.stem + "_dashboard.html"
        print(f"\n🎨 Generating interactive dashboard: {output_filename}")
        generate_interactive_dashboard_html(dashboard_data, output_filename)
        
        print(f"\n✅ Success! Dashboard has been generated: {output_filename}")
        
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

