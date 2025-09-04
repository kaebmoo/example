import pandas as pd
import plotly.graph_objects as go
import hashlib
import argparse
from pathlib import Path

def get_color_from_string(text):
    """Generates a consistent hex color from a string."""
    salted_text = text + "_sankey_salt_v7"
    hash_object = hashlib.md5(salted_text.encode())
    return '#' + hash_object.hexdigest()[:6]

def hex_to_rgba(hex_color, alpha=0.6):
    """Converts a hex color to RGBA with transparency."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({r},{g},{b},{alpha})'

def generate_sankey(df, output_path, view_type, filter_line=None, filter_dept=None, top_n=None):
    """Generates and saves a Sankey diagram based on the selected view and filters."""
    print(f"Generating Sankey with view: '{view_type}'...")

    try:
        column_mapping = {
            'สายงานผู้ให้บริการ': 'provider_line', 'ฝ่ายผู้ให้บริการ': 'provider_dept',
            'สายงานผู้รับบริการ': 'receiver_line', 'ฝ่ายผู้รับบริการ': 'receiver_dept',
            'บริการ': 'service', 'จำนวนเงิน (PxQ)': 'amount'
        }
        df.rename(columns=column_mapping, inplace=True)

        df['amount'] = pd.to_numeric(df['amount'].astype(str).str.replace(',', '', regex=True), errors='coerce')
        df.dropna(subset=['amount'], inplace=True)
        df = df[df['amount'] > 0]

        if filter_line:
            print(f"Applying filter for Business Line: '{filter_line}'")
            df = df[(df['provider_line'] == filter_line) | (df['receiver_line'] == filter_line)]
        if filter_dept:
            print(f"Applying filter for Department: '{filter_dept}'")
            df = df[(df['provider_dept'] == filter_dept) | (df['receiver_dept'] == filter_dept)]

        if df.empty:
            print("Warning: No data left after filtering. HTML file will not be generated.")
            return

        title = f"มุมมอง: {view_type}"
        if filter_line: title += f" (กรอง: {filter_line})"
        if filter_dept: title += f" (กรอง: {filter_dept})"
        if top_n: title += f" (Top {top_n} Flows)"

        # --- Logic for different views ---
        if view_type == 'strict-flow':
            title = "Strict Flow (Provider -> Service -> Receiver)"
            df_link1 = df.groupby(['provider_dept', 'service'])['amount'].sum().reset_index()
            df_link2 = df.groupby(['service', 'receiver_dept'])['amount'].sum().reset_index()

            if top_n:
                print(f"Filtering for Top {top_n} flows in each stage...")
                df_link1 = df_link1.nlargest(top_n, 'amount')
                df_link2 = df_link2.nlargest(top_n, 'amount')

            # Create distinct nodes for provider and receiver roles
            df_link1['provider_node'] = df_link1['provider_dept'] + ' (Provider)'
            df_link2['receiver_node'] = df_link2['receiver_dept'] + ' (Receiver)'

            all_nodes = pd.concat([
                df_link1['provider_node'], df_link1['service'], df_link2['receiver_node']
            ]).unique()
            node_dict = {node: i for i, node in enumerate(all_nodes)}

            source1 = df_link1['provider_node'].map(node_dict)
            target1 = df_link1['service'].map(node_dict)
            value1 = df_link1['amount']

            source2 = df_link2['service'].map(node_dict)
            target2 = df_link2['receiver_node'].map(node_dict)
            value2 = df_link2['amount']
            
            source = pd.concat([source1, source2], ignore_index=True).dropna()
            target = pd.concat([target1, target2], ignore_index=True).dropna()
            value = pd.concat([value1, value2], ignore_index=True).dropna()

        elif view_type == 'full-flow':
            title = "End-to-End Flow (Provider -> Service -> Receiver)"
            df_link1 = df.groupby(['provider_dept', 'service'])['amount'].sum().reset_index()
            df_link2 = df.groupby(['service', 'receiver_dept'])['amount'].sum().reset_index()
            if top_n:
                df_link1 = df_link1.nlargest(top_n, 'amount')
                df_link2 = df_link2.nlargest(top_n, 'amount')
            all_nodes = pd.concat([df_link1['provider_dept'], df_link1['service'], df_link2['receiver_dept']]).unique()
            node_dict = {node: i for i, node in enumerate(all_nodes)}
            source1 = df_link1['provider_dept'].map(node_dict); target1 = df_link1['service'].map(node_dict); value1 = df_link1['amount']
            source2 = df_link2['service'].map(node_dict); target2 = df_link2['receiver_dept'].map(node_dict); value2 = df_link2['amount']
            source = pd.concat([source1, source2], ignore_index=True).dropna()
            target = pd.concat([target1, target2], ignore_index=True).dropna()
            value = pd.concat([value1, value2], ignore_index=True).dropna()

        else: # 2-Layer Views
            source_target_map = {
                'line-to-line': ('provider_line', 'receiver_line'), 'dept-to-dept': ('provider_dept', 'receiver_dept'),
                'provider-to-service': ('provider_dept', 'service'), 'service-to-receiver': ('service', 'receiver_dept')
            }
            source_col, target_col = source_target_map[view_type]
            df_agg = df.groupby([source_col, target_col])['amount'].sum().reset_index()
            if top_n: df_agg = df_agg.nlargest(top_n, 'amount')
            all_nodes = pd.concat([df_agg[source_col], df_agg[target_col]]).unique()
            node_dict = {node: i for i, node in enumerate(all_nodes)}
            source = df_agg[source_col].map(node_dict)
            target = df_agg[target_col].map(node_dict)
            value = df_agg['amount']
        
        node_colors = [get_color_from_string(node.rsplit(' (', 1)[0]) for node in all_nodes]
        final_source_indices = source.astype(int).tolist()
        link_colors = [hex_to_rgba(node_colors[src_idx]) for src_idx in final_source_indices]

        fig = go.Figure(data=[go.Sankey(
            node=dict(pad=25, thickness=20, line=dict(color="black", width=0.5), label=all_nodes, color=node_colors),
            link=dict(source=source, target=target, value=value, color=link_colors),
            orientation='h'
        )])
        fig.update_layout(title_text=title, font_size=11, height=1000)
        fig.write_html(output_path)
        print(f"Successfully generated Sankey diagram and saved to '{output_path}'")

    except KeyError as e:
        print(f"Error: Missing required column: {e}. Please check your input file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate a Sankey diagram from a CSV or Excel file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_file", type=str, help="Path to the input CSV or Excel file.")
    parser.add_argument(
        "-v", "--view", type=str, default='strict-flow',
        choices=['strict-flow', 'full-flow', 'line-to-line', 'dept-to-dept', 'provider-to-service', 'service-to-receiver'],
        help="""Select the view to generate:
- 'strict-flow': Enforces 3 strict columns (Provider -> Service -> Receiver) with no backward paths. (Default)
- 'full-flow': 3-layer view from Provider Dept -> Service -> Receiver Dept.
- 'line-to-line': High-level view between business lines.
- 'dept-to-dept': View between provider and receiver departments.
- 'provider-to-service': Shows which departments provide which services.
- 'service-to-receiver': Shows which departments receive which services."""
    )
    parser.add_argument("-o", "--output", type=str, help="Path for the output HTML file. (Optional)")
    parser.add_argument("--filter-line", type=str, help="Filter data for a specific Business Line.")
    parser.add_argument("--filter-dept", type=str, help="Filter data for a specific Department.")
    parser.add_argument("--top-n", type=int, help="Display only the top N flows by amount.")
    
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if args.output:
        output_path = Path(args.output)
    else:
        filter_suffix = ""
        if args.filter_line: filter_suffix += f"_line_{args.filter_line.replace(' ', '_')[:20]}"
        if args.filter_dept: filter_suffix += f"_dept_{args.filter_dept.replace(' ', '_')[:20]}"
        if args.top_n: filter_suffix += f"_top{args.top_n}"
        output_path = input_path.with_name(f"{input_path.stem}_{args.view}{filter_suffix}.html")

    try:
        if input_path.suffix.lower() == '.csv':
            df = pd.read_csv(input_path, encoding='utf-8-sig')
        elif input_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(input_path)
        else:
            print(f"Error: Unsupported file type '{input_path.suffix}'.")
            return
        generate_sankey(df, output_path, args.view, args.filter_line, args.filter_dept, args.top_n)
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_path}'")

if __name__ == "__main__":
    main()

