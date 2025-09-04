import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import argparse
from pathlib import Path
import numpy as np # <<< เพิ่มการ import numpy เพื่อใช้ในการคำนวณ log

def generate_heatmap(df, output_path, title):
    """Generates an interactive heatmap of provider vs. receiver departments."""
    print("Generating Heatmap...")
    heatmap_data = df.groupby(['provider_dept', 'receiver_dept'])['amount'].sum().unstack().fillna(0)
    # filter_threshold = 10000000
    # heatmap_data = heatmap_data.where(heatmap_data >= filter_threshold,0)

    # --- START: สร้าง Custom Colorscale พร้อม Fallback ---
    try:
        # ลองใช้ 'Plasma' ก่อนเป็นอันดับแรก
        base_scale = px.colors.PLOTLY_SCALES['Plasma']
    except KeyError:
        # หากไม่มี 'Plasma' (อาจจะเพราะ Plotly เวอร์ชั่นเก่า) ให้ใช้ 'Viridis' แทน
        print("Warning: 'Plasma' colorscale not found. Falling back to 'Viridis'. You might want to upgrade Plotly (`pip install --upgrade plotly`).")
        base_scale = px.colors.PLOTLY_SCALES['Viridis']

    custom_colorscale = [list(item) for item in base_scale]
    custom_colorscale[0][1] = 'rgb(255, 255, 255)'
    # --- END: สิ้นสุดการสร้าง Custom Colorscale ---
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale=custom_colorscale,
        hovertemplate='Provider: %{y}<br>Receiver: %{x}<br>Amount: %{z:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="ฝ่ายผู้รับบริการ",
        yaxis_title="ฝ่ายผู้ให้บริการ",
        height=800
    )
    fig.write_html(output_path)
    print(f"Successfully generated Heatmap and saved to '{output_path}'")

def generate_sunburst(df, output_path, title):
    """Generates an interactive sunburst chart for the provider's side."""
    print("Generating Sunburst Chart...")
    
    fig = px.sunburst(
        df,
        path=['provider_line', 'provider_dept', 'service'],
        values='amount',
        title=title,
        height=800,
        hover_data={'amount': ':,.0f'}
    )
    fig.update_traces(textinfo="label+percent entry")
    fig.write_html(output_path)
    print(f"Successfully generated Sunburst Chart and saved to '{output_path}'")

def generate_network_graph(df, output_path, title):
    """Generates an interactive network graph of departments based on transaction amount."""
    print("Generating Network Graph...")
    
    df_agg = df.groupby(['provider_dept', 'receiver_dept'])['amount'].sum().reset_index()
    
    G = nx.from_pandas_edgelist(df_agg, 'provider_dept', 'receiver_dept', ['amount'])
    
    pos = nx.spring_layout(G, k=0.8, iterations=50)

    # <<< START: การคำนวณขนาดและความหนาตาม 'amount' >>>

    # สร้าง Edge Traces ที่มีความหนาตาม 'amount'
    edge_traces = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        amount = edge[2]['amount']
        
        # คำนวณความหนาของเส้น (ใช้ log เพื่อไม่ให้เส้นหนาต่างกันจนเกินไป)
        line_width = np.log10(amount) / 2 if amount > 1 else 0.1

        trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line=dict(width=line_width, color='#888'),
            hoverinfo='text',
            text=f'Amount: {amount:,.0f}',
            mode='lines')
        edge_traces.append(trace)

    # คำนวณยอดรวม 'amount' ของแต่ละโหนด (ทั้งเป็นผู้ให้และผู้รับ)
    total_provided = df.groupby('provider_dept')['amount'].sum()
    total_received = df.groupby('receiver_dept')['amount'].sum()
    node_total_amounts = total_provided.add(total_received, fill_value=0)

    node_x, node_y = [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_amounts_for_color = []
    node_sizes = []
    node_text = []
    
    for node in G.nodes():
        total_amount = node_total_amounts.get(node, 0)
        node_amounts_for_color.append(total_amount)
        
        # คำนวณขนาดโหนด (ใช้ log + ค่าคงที่ เพื่อให้ขนาดเหมาะสม)
        size = (np.log10(total_amount) * 3 + 5) if total_amount > 1 else 5
        node_sizes.append(size)

        node_text.append(f'{node}<br>Total Amount: {total_amount:,.0f}')
    
    # <<< END: สิ้นสุดการคำนวณ >>>

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text, # <<< ใช้ node_text ที่สร้างใหม่
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=node_amounts_for_color, # <<< เปลี่ยนสีตามยอดเงิน
            size=node_sizes,             # <<< เปลี่ยนขนาดตามยอดเงิน
            colorbar=dict(
                thickness=15,
                title=dict(
                    text='Total Amount', # <<< เปลี่ยนหัวข้อ Color bar
                    side='right'
                ),
                xanchor='left'
            ),
            line_width=2))

    fig = go.Figure(data=edge_traces + [node_trace], # <<< ใช้ edge_traces ที่สร้างเป็น list
             layout=go.Layout(
                title=dict(text=title, font=dict(size=16)),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="Network graph showing transaction amounts between departments",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    
    fig.update_layout(height=800)
    fig.write_html(output_path)
    print(f"Successfully generated Network Graph and saved to '{output_path}'")


def main():
    parser = argparse.ArgumentParser(
        description="Generate alternative visualizations from service data.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_file", type=str, help="Path to the input CSV or Excel file.")
    parser.add_argument(
        "-t", "--type", type=str, required=True,
        choices=['heatmap', 'sunburst', 'network'],
        help="Type of visualization to generate."
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    output_path = input_path.with_name(f"{input_path.stem}_{args.type}.html")
    
    try:
        if input_path.suffix.lower() == '.csv':
            df = pd.read_csv(input_path, encoding='utf-8-sig')
        elif input_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(input_path)
        else:
            print(f"Error: Unsupported file type '{input_path.suffix}'.")
            return

        # --- Column mapping and data cleaning ---
        column_mapping = {
            'สายงานผู้ให้บริการ': 'provider_line', 'ฝ่ายผู้ให้บริการ': 'provider_dept',
            'สายงานผู้รับบริการ': 'receiver_line', 'ฝ่ายผู้รับบริการ': 'receiver_dept',
            'บริการ': 'service', 'จำนวนเงิน (PxQ)': 'amount'
        }
        # Check for all required columns before renaming
        required_cols = list(column_mapping.keys())
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Missing required columns in Excel file: {', '.join(missing_cols)}")

        df.rename(columns=column_mapping, inplace=True)
        df['amount'] = pd.to_numeric(df['amount'].astype(str).str.replace(',', '', regex=True), errors='coerce')
        df.dropna(subset=['amount'], inplace=True)
        df = df[df['amount'] > 0]
        
        title = f"{args.type.capitalize()} Visualization of Inter-Departmental Services"

        if args.type == 'heatmap':
            generate_heatmap(df, output_path, title)
        elif args.type == 'sunburst':
            generate_sunburst(df, output_path, title)
        elif args.type == 'network':
            generate_network_graph(df, output_path, title)

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_path}'")
    except KeyError as e:
        print(f"Error: {e}. Please check your input file headers.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

