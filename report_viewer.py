#!/usr/bin/env python3
"""
Generate beautiful HTML reports from JSON upload results.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def get_html_template():
    """Return HTML template with properly escaped CSS."""
    # Using triple quotes and manual string building to avoid format conflicts
    css = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }

        .summary-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }

        .summary-card:hover {
            transform: translateY(-5px);
        }

        .summary-card .number {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .summary-card .label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .total .number { color: #6c757d; }
        .success .number { color: #28a745; }
        .failed .number { color: #dc3545; }
        .skipped .number { color: #ffc107; }

        .details {
            padding: 30px;
        }

        .details h2 {
            margin-bottom: 20px;
            color: #333;
            font-size: 1.8em;
        }

        .filters {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .filter-btn {
            padding: 8px 16px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
        }

        .filter-btn:hover, .filter-btn.active {
            background: #667eea;
            color: white;
        }

        .record {
            background: white;
            border-left: 4px solid #ddd;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.2s;
        }

        .record:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .record.success { border-left-color: #28a745; }
        .record.failed { border-left-color: #dc3545; }
        .record.skipped { border-left-color: #ffc107; }

        .record-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .record-id {
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }

        .badge {
            padding: 5px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
        }

        .badge.success { background: #d4edda; color: #155724; }
        .badge.failed { background: #f8d7da; color: #721c24; }
        .badge.skipped { background: #fff3cd; color: #856404; }

        .record-details {
            color: #666;
            line-height: 1.6;
        }

        .file-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }

        .file-tag {
            background: #e9ecef;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-family: 'Courier New', monospace;
        }

        .file-tag.created { background: #d4edda; color: #155724; }
        .file-tag.updated { background: #d1ecf1; color: #0c5460; }
        .file-tag.missing { background: #fff3cd; color: #856404; }

        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }

        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }

        .no-results {
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 1.1em;
        }

        @media print {
            body { background: white; padding: 0; }
            .container { box-shadow: none; }
            .filter-btn { display: none; }
        }
    """

    # Build the full HTML
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biometric Upload Report</title>
    <style>{css}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Biometric Upload Report</h1>
            <p>Generated on {{timestamp}}</p>
        </div>

        <div class="summary">
            <div class="summary-card total">
                <div class="number">{{total_drivers}}</div>
                <div class="label">Total Drivers</div>
            </div>
            <div class="summary-card success">
                <div class="number">{{success}}</div>
                <div class="label">Successful</div>
            </div>
            <div class="summary-card failed">
                <div class="number">{{failed}}</div>
                <div class="label">Failed</div>
            </div>
            <div class="summary-card skipped">
                <div class="number">{{skipped}}</div>
                <div class="label">Skipped</div>
            </div>
        </div>

        <div class="details">
            <h2>Upload Details</h2>

            <div class="filters">
                <button class="filter-btn active" onclick="filterRecords('all')">All</button>
                <button class="filter-btn" onclick="filterRecords('success')">✓ Success</button>
                <button class="filter-btn" onclick="filterRecords('failed')">✗ Failed</button>
                <button class="filter-btn" onclick="filterRecords('skipped')">⊘ Skipped</button>
            </div>

            <div id="records">
                {{records_html}}
            </div>
        </div>

        <div class="footer">
            <p>Biometric Data Uploader - api-condutores</p>
            <p>Total CSV Rows: {{total_csv_rows}} | Processing Time: {{processing_info}}</p>
        </div>
    </div>

    <script>
        function filterRecords(status) {{
            const records = document.querySelectorAll('.record');
            const buttons = document.querySelectorAll('.filter-btn');

            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');

            records.forEach(record => {{
                if (status === 'all' || record.classList.contains(status)) {{
                    record.style.display = 'block';
                }} else {{
                    record.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>"""


def generate_record_html(detail):
    """Generate HTML for a single record."""
    status = detail.get('status', 'unknown')
    numero_carta = detail.get('numero_carta', 'N/A')

    # Files
    files_created = detail.get('files_created', [])
    files_updated = detail.get('files_updated', [])
    files_missing = detail.get('files_missing', [])

    files_html = ""
    if files_created:
        files_html += "<div class='file-list'>"
        for f in files_created:
            files_html += f"<span class='file-tag created'>✓ {f}</span>"
        files_html += "</div>"

    if files_updated:
        if not files_html:
            files_html = "<div class='file-list'>"
        for f in files_updated:
            files_html += f"<span class='file-tag updated'>↻ {f}</span>"
        if files_created:
            files_html += "</div>"

    if files_missing:
        if not files_html:
            files_html = "<div class='file-list'>"
        for f in files_missing:
            files_html += f"<span class='file-tag missing'>⚠ {f}</span>"
        files_html += "</div>"

    # Error message
    error_html = ""
    if status != 'success' and 'error' in detail:
        error_html = f"<div class='error-message'>Error: {detail['error']}</div>"

    # Driver info
    driver_info = ""
    if detail.get('driver_created'):
        driver_info = "<span style='color: #28a745;'>● New driver created</span>"
    elif status == 'success':
        driver_info = "<span style='color: #0078d4;'>● Existing driver updated</span>"

    csv_rows = detail.get('csv_rows', 0)

    return f"""
    <div class="record {status}">
        <div class="record-header">
            <div class="record-id">🆔 {numero_carta}</div>
            <span class="badge {status}">{status}</span>
        </div>
        <div class="record-details">
            {driver_info}
            {f' | CSV Rows: {csv_rows}' if csv_rows else ''}
            {files_html}
            {error_html}
        </div>
    </div>
    """


def generate_html_report(json_data):
    """Generate full HTML report from JSON data."""
    # Generate records HTML
    records_html = ""
    details = json_data.get('details', [])

    if details:
        for detail in details:
            records_html += generate_record_html(detail)
    else:
        records_html = '<div class="no-results">No records to display</div>'

    # Get template and fill it using string replacement
    template = get_html_template()

    html = template.replace('{{timestamp}}', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    html = html.replace('{{total_drivers}}', str(json_data.get('total_drivers', 0)))
    html = html.replace('{{total_csv_rows}}', str(json_data.get('total_csv_rows', 0)))
    html = html.replace('{{success}}', str(json_data.get('success', 0)))
    html = html.replace('{{failed}}', str(json_data.get('failed', 0)))
    html = html.replace('{{skipped}}', str(json_data.get('skipped', 0)))
    html = html.replace('{{records_html}}', records_html)
    html = html.replace('{{processing_info}}', "See details above")

    return html


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python report_viewer.py <json_report_file>")
        print("\nExample:")
        print("  python report_viewer.py upload_report.json")
        sys.exit(1)

    json_file = sys.argv[1]

    if not Path(json_file).exists():
        print(f"Error: File not found: {json_file}")
        sys.exit(1)

    # Read JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        sys.exit(1)

    # Generate HTML
    html = generate_html_report(data)

    # Save HTML
    output_file = Path(json_file).stem + "_report.html"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✓ HTML report generated: {output_file}")
        print(f"\nOpen in browser: file://{Path(output_file).absolute()}")
    except Exception as e:
        print(f"Error writing HTML file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
