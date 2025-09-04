# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Sankey diagram visualization project focused on analyzing service flow relationships between departments and service lines in a Thai telecommunications context. The codebase generates interactive Plotly-based Sankey diagrams from Excel data files showing provider-receiver relationships, service hierarchies, and departmental flows.

## Core Architecture

The project consists of multiple specialized Python scripts, each serving different visualization purposes:

### Main Scripts and Their Purposes

1. **plotly_color_sankey.py** - Primary recommended script
   - Multi-layer Sankey with service grouping and dual role analysis
   - Automatically categorizes services into groups (Cloud, Security, Network, etc.)
   - Shows departments that act as both providers and receivers
   - 5 different view modes with color-coded service groups

2. **plotly_sankey.py** - Full multi-layer visualization 
   - Complete flow: Line → Department → Service → Receiving Department → Receiving Line
   - 5 view modes: Full Flow, Department Focus, Service Focus, High Level, Custom
   - Interactive mode selection

3. **service_chain.py** - Service hierarchy analysis
   - Analyzes service levels (L1-L6: Infrastructure → Application)
   - Service transformation views and dual role chain analysis
   - Hierarchical service classification

4. **create_sankey_cli.py** - Command-line interface tool
   - Flexible filtering and view options
   - Top N filtering capabilities
   - Multiple view modes via CLI arguments

5. **create_alternative_viz.py** - Alternative visualization formats
   - Heatmaps, Sunburst charts, Network graphs
   - Non-Sankey visualization options

6. **sankey_script.py** - D3.js-based HTML output
   - Creates standalone HTML with D3.js (no Plotly dependency)
   - Pure web-based interactive visualization

## Data Structure

The scripts expect Excel files with Thai column names:
- `สายงานผู้ให้บริการ` (Provider Line)
- `ฝ่ายผู้ให้บริการ` (Provider Department) 
- `บริการ` (Service)
- `บริการย่อย` (Sub-service)
- `ฝ่ายผู้รับบริการ` (Receiver Department)
- `สายงานผู้รับบริการ` (Receiver Line)
- `จำนวนเงิน (PxQ)` (Amount)

## Common Commands

### Running Individual Scripts
```bash
# Main recommended script with service grouping
python plotly_color_sankey.py PQ-July.xlsx

# Multi-layer interactive Sankey
python plotly_sankey.py PQ-July.xlsx  

# Service hierarchy analysis
python service_chain.py PQ-July.xlsx

# CLI tool with filtering options
python create_sankey_cli.py PQ-July.xlsx -v dept-to-dept --top-n 30

# Alternative visualizations (heatmap, sunburst, network)
python create_alternative_viz.py PQ-July.xlsx -t heatmap

# D3.js HTML output
python sankey_script.py PQ-July.xlsx
```

### Output Files
Scripts generate HTML files in the same directory:
- `complete_sankey.html`
- `multilayer_sankey.html` 
- `enhanced_chain.html`
- `service_chain_sankey.html`
- `sankey_output.html`

## Key Features

### Service Classification
The system automatically groups services into categories:
- Cloud & Big Data
- Security  
- Network & Internet
- Communication
- Infrastructure
- Software & Apps
- IT Services
- Billing & Finance
- Professional Services

### Dual Role Analysis
Identifies departments that function as both service providers and receivers, with special color coding and analysis.

### Service Hierarchy
Classifies services into 6 levels:
- L1: Infrastructure (cables, towers, buildings)
- L2: Transmission (DWDM, fiber)
- L3: Network (IIG, broadband, datacom)
- L4: Platform (cloud, servers, security)
- L5: Application (software, systems)
- L6: Services (contact center, helpdesk)

## Dependencies

The project uses these Python libraries:
- pandas - Data processing
- plotly - Interactive visualization
- numpy - Numerical operations
- pathlib - Path handling

No package.json, requirements.txt, or other dependency management files exist. Libraries should be installed manually as needed.

## Development Notes

- All user interfaces and documentation are in Thai
- Scripts include interactive menus for view selection
- HTML outputs are standalone and can be opened directly in browsers
- No formal testing framework - verification is visual through generated outputs
- No linting or build configuration present