#!/usr/bin/env python3
"""
Biometric Data Uploader - GUI Application
Modern interface for uploading biometric data to api-condutores
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import json
import os
import webbrowser
from pathlib import Path
from datetime import datetime
from csv_api_sender import BiometricAPIProcessor
from report_viewer import generate_html_report


class BiometricUploaderGUI:
    """Modern GUI for biometric data upload."""

    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Biometric Data Uploader - api-condutores")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Variables
        self.csv_file_path = tk.StringVar()
        self.api_url = tk.StringVar(value="http://127.0.0.1:5000")
        self.auth_token = tk.StringVar()
        self.is_processing = False
        self.message_queue = queue.Queue()

        # Styling
        self.setup_styles()

        # Create UI
        self.create_widgets()

        # Start queue checker
        self.check_queue()

    def setup_styles(self):
        """Setup ttk styles for modern look."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        bg_color = "#f0f0f0"
        accent_color = "#0078d4"
        success_color = "#107c10"
        error_color = "#d13438"

        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground=accent_color)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="#666666")
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=10)
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))
        style.configure("TEntry", font=("Segoe UI", 10), padding=5)

        self.root.configure(bg=bg_color)

    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        ttk.Label(
            header_frame,
            text="🔐 Biometric Data Uploader",
            style="Title.TLabel"
        ).grid(row=0, column=0, sticky=tk.W)

        ttk.Label(
            header_frame,
            text="Upload driver biometric data to api-condutores",
            style="Subtitle.TLabel"
        ).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="15")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)

        # CSV File Selection
        ttk.Label(config_frame, text="CSV File:").grid(row=0, column=0, sticky=tk.W, pady=5)

        file_frame = ttk.Frame(config_frame)
        file_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        file_frame.columnconfigure(0, weight=1)

        self.csv_entry = ttk.Entry(file_frame, textvariable=self.csv_file_path, state="readonly")
        self.csv_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Button(
            file_frame,
            text="Browse...",
            command=self.browse_csv_file
        ).grid(row=0, column=1)

        # API URL
        ttk.Label(config_frame, text="API URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(
            config_frame,
            textvariable=self.api_url,
            width=50
        ).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # Auth Token (optional)
        ttk.Label(config_frame, text="Auth Token:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(
            config_frame,
            textvariable=self.auth_token,
            show="*",
            width=50
        ).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        ttk.Label(
            config_frame,
            text="(Optional - leave blank if not required)",
            style="Subtitle.TLabel"
        ).grid(row=3, column=1, sticky=tk.W, padx=(10, 0))

        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="15")
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Status text area
        self.status_text = scrolledtext.ScrolledText(
            progress_frame,
            height=15,
            width=80,
            font=("Consolas", 9),
            state='disabled',
            bg="#ffffff",
            fg="#000000"
        )
        self.status_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure text tags for colored output
        self.status_text.tag_config("success", foreground="#107c10")
        self.status_text.tag_config("error", foreground="#d13438")
        self.status_text.tag_config("warning", foreground="#ff8c00")
        self.status_text.tag_config("info", foreground="#0078d4")
        self.status_text.tag_config("header", foreground="#000000", font=("Consolas", 9, "bold"))

        # Summary Section
        summary_frame = ttk.Frame(main_frame)
        summary_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        summary_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.total_label = ttk.Label(summary_frame, text="Total: 0", font=("Segoe UI", 10, "bold"))
        self.total_label.grid(row=0, column=0, padx=5)

        self.success_label = ttk.Label(summary_frame, text="✓ Success: 0", foreground="#107c10")
        self.success_label.grid(row=0, column=1, padx=5)

        self.failed_label = ttk.Label(summary_frame, text="✗ Failed: 0", foreground="#d13438")
        self.failed_label.grid(row=0, column=2, padx=5)

        self.skipped_label = ttk.Label(summary_frame, text="⊘ Skipped: 0", foreground="#ff8c00")
        self.skipped_label.grid(row=0, column=3, padx=5)

        # Action Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)

        self.upload_button = ttk.Button(
            button_frame,
            text="▶ Start Upload",
            command=self.start_upload,
            style="Accent.TButton"
        )
        self.upload_button.grid(row=0, column=0, sticky=tk.E, padx=(0, 10))

        self.save_report_button = ttk.Button(
            button_frame,
            text="💾 Save Report",
            command=self.save_report,
            state='disabled'
        )
        self.save_report_button.grid(row=0, column=1, sticky=tk.E)

        # Configure grid weights for resizing
        main_frame.rowconfigure(2, weight=1)

    def browse_csv_file(self):
        """Open file dialog to select CSV file."""
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.csv_file_path.set(filename)

    def append_status(self, message, tag="info"):
        """Append message to status text area."""
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, message + "\n", tag)
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')

    def update_summary(self, results):
        """Update summary labels."""
        total = results.get('total_drivers', 0)
        success = results.get('success', 0)
        failed = results.get('failed', 0)
        skipped = results.get('skipped', 0)

        self.total_label.config(text=f"Total: {total}")
        self.success_label.config(text=f"✓ Success: {success}")
        self.failed_label.config(text=f"✗ Failed: {failed}")
        self.skipped_label.config(text=f"⊘ Skipped: {skipped}")

    def check_queue(self):
        """Check message queue for updates from worker thread."""
        try:
            while True:
                msg = self.message_queue.get_nowait()

                if msg['type'] == 'status':
                    self.append_status(msg['text'], msg.get('tag', 'info'))
                elif msg['type'] == 'progress':
                    self.progress_var.set(msg['value'])
                elif msg['type'] == 'summary':
                    self.update_summary(msg['results'])
                elif msg['type'] == 'complete':
                    self.upload_button.config(state='normal', text="▶ Start Upload")
                    self.save_report_button.config(state='normal')
                    self.is_processing = False
                    self.results = msg.get('results', {})
        except queue.Empty:
            pass

        self.root.after(100, self.check_queue)

    def start_upload(self):
        """Start the upload process."""
        # Validation
        if not self.csv_file_path.get():
            messagebox.showerror("Error", "Please select a CSV file")
            return

        if not self.api_url.get():
            messagebox.showerror("Error", "Please enter API URL")
            return

        if not os.path.exists(self.csv_file_path.get()):
            messagebox.showerror("Error", "CSV file does not exist")
            return

        # Clear previous results
        self.status_text.config(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state='disabled')
        self.progress_var.set(0)
        self.update_summary({'total_drivers': 0, 'success': 0, 'failed': 0, 'skipped': 0})

        # Disable button
        self.upload_button.config(state='disabled', text="⏳ Processing...")
        self.save_report_button.config(state='disabled')
        self.is_processing = True

        # Start worker thread
        thread = threading.Thread(target=self.upload_worker, daemon=True)
        thread.start()

    def upload_worker(self):
        """Worker thread for upload process."""
        try:
            # Prepare headers
            headers = {'Content-Type': 'application/json'}
            if self.auth_token.get():
                headers['Authorization'] = f'Bearer {self.auth_token.get()}'

            # Create processor
            processor = BiometricAPIProcessor(self.api_url.get(), headers)

            # Read CSV
            self.message_queue.put({
                'type': 'status',
                'text': f"📂 Reading CSV file: {os.path.basename(self.csv_file_path.get())}",
                'tag': 'info'
            })

            records = processor.read_csv(self.csv_file_path.get())
            grouped_records = processor.group_by_license(records)

            self.message_queue.put({
                'type': 'status',
                'text': f"✓ Found {len(records)} CSV rows → {len(grouped_records)} unique drivers\n",
                'tag': 'success'
            })

            self.message_queue.put({
                'type': 'status',
                'text': "=" * 80,
                'tag': 'header'
            })

            # Process each driver
            results = {
                'total_csv_rows': len(records),
                'total_drivers': len(grouped_records),
                'success': 0,
                'failed': 0,
                'skipped': 0,
                'details': []
            }

            for idx, (numero_carta, rows) in enumerate(grouped_records.items(), 1):
                progress = (idx / len(grouped_records)) * 100
                self.message_queue.put({'type': 'progress', 'value': progress})

                if not numero_carta:
                    msg = f"[{idx}/{len(grouped_records)}] ✗ SKIPPED: Missing license number"
                    self.message_queue.put({'type': 'status', 'text': msg, 'tag': 'error'})
                    results['skipped'] += 1
                    continue

                # Build payload
                payload = processor.build_payload_from_rows(rows)

                if not payload:
                    msg = f"[{idx}/{len(grouped_records)}] ⊘ SKIPPED {numero_carta}: No biometric data found"
                    self.message_queue.put({'type': 'status', 'text': msg, 'tag': 'warning'})
                    results['skipped'] += 1
                    continue

                # Send to API
                result = processor.send_to_api(numero_carta, payload)

                if result['status'] == 'success':
                    results['success'] += 1
                    api_status = result.get('response', {}).get('status', {})

                    files_created = api_status.get('files_created', [])
                    files_updated = api_status.get('files_updated', [])

                    details = f"Created: {len(files_created)}, Updated: {len(files_updated)}"
                    msg = f"[{idx}/{len(grouped_records)}] ✓ SUCCESS {numero_carta}: {details}"
                    self.message_queue.put({'type': 'status', 'text': msg, 'tag': 'success'})

                    results['details'].append({
                        'numero_carta': numero_carta,
                        'status': 'success',
                        'files_created': files_created,
                        'files_updated': files_updated
                    })

                elif result['status'] == 'skipped':
                    results['skipped'] += 1
                    msg = f"[{idx}/{len(grouped_records)}] ⊘ SKIPPED {numero_carta}: {result.get('error', 'No data')}"
                    self.message_queue.put({'type': 'status', 'text': msg, 'tag': 'warning'})

                else:
                    results['failed'] += 1
                    error = result.get('error', 'Unknown error')
                    msg = f"[{idx}/{len(grouped_records)}] ✗ FAILED {numero_carta}: {error}"
                    self.message_queue.put({'type': 'status', 'text': msg, 'tag': 'error'})

                    results['details'].append({
                        'numero_carta': numero_carta,
                        'status': 'failed',
                        'error': error
                    })

                # Update summary
                self.message_queue.put({'type': 'summary', 'results': results})

            # Final summary
            self.message_queue.put({'type': 'status', 'text': "\n" + "=" * 80, 'tag': 'header'})
            self.message_queue.put({'type': 'status', 'text': "UPLOAD COMPLETE", 'tag': 'header'})
            self.message_queue.put({'type': 'status', 'text': "=" * 80 + "\n", 'tag': 'header'})

            if processor.files_not_found:
                self.message_queue.put({
                    'type': 'status',
                    'text': f"⚠ Warning: {len(processor.files_not_found)} file(s) not found",
                    'tag': 'warning'
                })

            self.message_queue.put({'type': 'progress', 'value': 100})
            self.message_queue.put({'type': 'complete', 'results': results})

        except Exception as e:
            self.message_queue.put({
                'type': 'status',
                'text': f"\n✗ ERROR: {str(e)}",
                'tag': 'error'
            })
            self.message_queue.put({'type': 'complete', 'results': {}})

    def save_report(self):
        """Save detailed report to JSON and HTML files."""
        if not hasattr(self, 'results'):
            messagebox.showwarning("Warning", "No results to save")
            return

        # Ask for JSON filename
        json_filename = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"biometric_upload_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        if json_filename:
            try:
                # Save JSON
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False)

                # Generate and save HTML
                html_filename = Path(json_filename).stem + "_report.html"
                html_content = generate_html_report(self.results)

                with open(html_filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)

                # Ask if user wants to open HTML report
                response = messagebox.askyesno(
                    "Report Saved",
                    f"Reports saved successfully:\n\n"
                    f"📄 JSON: {Path(json_filename).name}\n"
                    f"🌐 HTML: {Path(html_filename).name}\n\n"
                    f"Would you like to open the HTML report in your browser?"
                )

                if response:
                    webbrowser.open(f"file://{Path(html_filename).absolute()}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report:\n{str(e)}")


def main():
    """Main entry point for GUI application."""
    root = tk.Tk()
    app = BiometricUploaderGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
