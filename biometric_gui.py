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
        self.root.geometry("950x750")
        self.root.resizable(True, True)

        # Load configuration
        config = self.load_config()

        # Variables - use loaded config values
        self.csv_file_path = tk.StringVar(value=config.get('last_csv_path', ''))
        self.biometric_dir = tk.StringVar(value=config.get('biometric_dir', r"C:\Biometric"))
        self.api_url = tk.StringVar(value=config.get('api_url', "http:192.168.0.7:4000"))
        self.auth_token = tk.StringVar()
        self.input_mode = tk.StringVar(value=config.get('input_mode', 'csv'))
        self.manual_numbers_list = config.get('manual_numbers', [])
        self.is_processing = False
        self.message_queue = queue.Queue()

        # Styling
        self.setup_styles()

        # Create UI
        self.create_widgets()

        # Start queue checker
        self.check_queue()

    def load_config(self):
        """Load configuration from config.json in project directory."""
        import logging
        logger = logging.getLogger(__name__)

        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        default_config = {
            'biometric_dir': r'C:\Biometric',
            'api_url': 'http://192.168.0.7:4000',
            'last_csv_path': '',
            'input_mode': 'csv',
            'manual_numbers': [],
            'version': '1.0'
        }

        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                    # Validate biometric_dir if specified
                    if 'biometric_dir' in config and config['biometric_dir']:
                        if not os.path.exists(config['biometric_dir']):
                            logger.warning(f"Configured biometric directory not found: {config['biometric_dir']}")
                            # Keep the value - drive may be disconnected temporarily

                    # Merge loaded config with defaults (defaults as fallback)
                    return {**default_config, **config}
            else:
                logger.info(f"No config file found at {config_path}, using defaults")
                return default_config

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return default_config

    def save_config(self):
        """Save current settings to config.json."""
        import logging
        logger = logging.getLogger(__name__)

        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        config = {
            'biometric_dir': self.biometric_dir.get(),
            'api_url': self.api_url.get(),
            'last_csv_path': self.csv_file_path.get(),
            'input_mode': self.input_mode.get(),
            'manual_numbers': self.manual_numbers_list,
            'version': '1.0'
        }

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {config_path}")
        except PermissionError:
            logger.error(f"Permission denied writing config to {config_path}")
            # Don't show error to user - non-critical failure
        except Exception as e:
            logger.error(f"Error saving config: {e}")

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

        # Input Mode Selection
        mode_frame = ttk.LabelFrame(main_frame, text="Input Mode", padding="15")
        mode_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Radiobutton(
            mode_frame,
            text="CSV File",
            variable=self.input_mode,
            value='csv',
            command=self.on_mode_change
        ).grid(row=0, column=0, padx=(0, 20), sticky=tk.W)

        ttk.Radiobutton(
            mode_frame,
            text="Manual Numbers",
            variable=self.input_mode,
            value='manual',
            command=self.on_mode_change
        ).grid(row=0, column=1, sticky=tk.W)

        # CSV File Section
        self.csv_frame = ttk.LabelFrame(main_frame, text="CSV File", padding="15")
        self.csv_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.csv_frame.columnconfigure(1, weight=1)

        ttk.Label(
            self.csv_frame,
            text="Select CSV file:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10), columnspan=2)

        file_frame = ttk.Frame(self.csv_frame)
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), columnspan=2, pady=(0, 5))
        file_frame.columnconfigure(0, weight=1)

        self.csv_entry = ttk.Entry(
            file_frame,
            textvariable=self.csv_file_path,
            state="readonly",
            font=("Segoe UI", 10)
        )
        self.csv_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Button(
            file_frame,
            text="Browse...",
            command=self.browse_csv_file
        ).grid(row=0, column=1)

        # Manual Entry Section - HORIZONTAL LAYOUT
        self.manual_frame = ttk.LabelFrame(main_frame, text="Manual License Numbers", padding="15")
        self.manual_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.manual_frame.columnconfigure(0, weight=1)
        self.manual_frame.columnconfigure(1, weight=1)

        # LEFT COLUMN: Input Area
        left_frame = ttk.Frame(self.manual_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        ttk.Label(
            left_frame,
            text="Paste or type numbers (one per line):",
            font=("Segoe UI", 9, "bold")
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.manual_input_text = scrolledtext.ScrolledText(
            left_frame,
            height=6,
            width=30,
            font=("Consolas", 9),
            wrap=tk.NONE,
            bg="#ffffff",
            fg="#000000"
        )
        self.manual_input_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Add placeholder text
        placeholder = "Example:\n10082220\n10116145\n10054321"
        self.manual_input_text.insert("1.0", placeholder)
        self.manual_input_text.config(fg="#999999")

        # Bind focus events for placeholder
        def on_focus_in(event):
            if self.manual_input_text.get("1.0", tk.END).strip() == placeholder:
                self.manual_input_text.delete("1.0", tk.END)
                self.manual_input_text.config(fg="#000000")

        def on_focus_out(event):
            if not self.manual_input_text.get("1.0", tk.END).strip():
                self.manual_input_text.insert("1.0", placeholder)
                self.manual_input_text.config(fg="#999999")

        self.manual_input_text.bind("<FocusIn>", on_focus_in)
        self.manual_input_text.bind("<FocusOut>", on_focus_out)

        input_buttons = ttk.Frame(left_frame)
        input_buttons.grid(row=2, column=0, sticky=(tk.W, tk.E))
        input_buttons.columnconfigure(0, weight=1)
        input_buttons.columnconfigure(1, weight=1)

        ttk.Button(
            input_buttons,
            text="➕ Add to Queue",
            command=self.add_manual_numbers,
            style="Accent.TButton"
        ).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        ttk.Button(
            input_buttons,
            text="🗑 Clear",
            command=lambda: self.manual_input_text.delete("1.0", tk.END)
        ).grid(row=0, column=1, sticky=(tk.W, tk.E))

        # RIGHT COLUMN: Queue
        right_frame = ttk.Frame(self.manual_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        self.manual_queue_label = ttk.Label(
            right_frame,
            text=f"Queue ({len(self.manual_numbers_list)}):",
            font=("Segoe UI", 9, "bold")
        )
        self.manual_queue_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        listbox_frame = ttk.Frame(right_frame, relief=tk.SUNKEN, borderwidth=1)
        listbox_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        self.manual_numbers_listbox = tk.Listbox(
            listbox_frame,
            height=6,
            font=("Consolas", 9),
            selectmode=tk.EXTENDED,
            bg="#ffffff",
            relief=tk.FLAT
        )
        self.manual_numbers_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.manual_numbers_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.manual_numbers_listbox.config(yscrollcommand=scrollbar.set)

        queue_buttons = ttk.Frame(right_frame)
        queue_buttons.grid(row=2, column=0, sticky=(tk.W, tk.E))
        queue_buttons.columnconfigure(0, weight=1)
        queue_buttons.columnconfigure(1, weight=1)

        ttk.Button(
            queue_buttons,
            text="Remove Selected",
            command=self.remove_selected_numbers
        ).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        ttk.Button(
            queue_buttons,
            text="Clear All",
            command=self.clear_manual_numbers
        ).grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Initialize listbox with saved numbers
        self.update_manual_listbox()

        # Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="15")
        config_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)

        # Biometric Directory
        ttk.Label(config_frame, text="Biometric Dir:").grid(row=0, column=0, sticky=tk.W, pady=5)

        bio_dir_frame = ttk.Frame(config_frame)
        bio_dir_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        bio_dir_frame.columnconfigure(0, weight=1)

        ttk.Entry(bio_dir_frame, textvariable=self.biometric_dir).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Button(
            bio_dir_frame,
            text="Browse...",
            command=self.browse_biometric_dir
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
        progress_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
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
        summary_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
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
        button_frame.grid(row=7, column=0, sticky=(tk.W, tk.E))
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
        main_frame.rowconfigure(2, weight=0)  # CSV frame - no expand
        main_frame.rowconfigure(3, weight=0)  # Manual frame - no expand
        main_frame.rowconfigure(5, weight=1)  # Progress frame - expand

        # Call on_mode_change to show/hide appropriate section
        self.on_mode_change()

    def browse_csv_file(self):
        """Open file dialog to select CSV file."""
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.csv_file_path.set(filename)
            self.save_config()

    def browse_biometric_dir(self):
        """Open directory dialog to select biometric directory."""
        dirname = filedialog.askdirectory(
            title="Select Biometric Directory",
            initialdir=self.biometric_dir.get() if self.biometric_dir.get() else None
        )
        if dirname:
            self.biometric_dir.set(dirname)
            self.save_config()
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Biometric directory updated: {dirname}")

    def on_mode_change(self):
        """Handle input mode change (CSV vs Manual)."""
        mode = self.input_mode.get()

        if mode == 'csv':
            # Show CSV section, hide manual section
            self.csv_frame.grid()
            self.manual_frame.grid_remove()
        else:
            # Show manual section, hide CSV section
            self.csv_frame.grid_remove()
            self.manual_frame.grid()

    def add_manual_numbers(self):
        """Add license numbers from input text to the queue."""
        text = self.manual_input_text.get("1.0", tk.END)

        # Check if placeholder text
        placeholder = "Example:\n10082220\n10116145\n10054321"
        if text.strip() == placeholder:
            messagebox.showwarning("No Input", "Please enter license numbers first")
            return

        lines = text.strip().split('\n')

        added = 0
        duplicates = 0
        invalid = 0

        for line in lines:
            numero = line.strip()
            if not numero:
                continue

            # Check duplicates
            if numero in self.manual_numbers_list:
                duplicates += 1
                continue

            self.manual_numbers_list.append(numero)
            added += 1

        self.update_manual_listbox()
        self.save_config()

        # Clear input area and reset placeholder
        self.manual_input_text.delete("1.0", tk.END)
        self.manual_input_text.insert("1.0", placeholder)
        self.manual_input_text.config(fg="#999999")

        # Show summary
        if added > 0 or duplicates > 0 or invalid > 0:
            msg = f"Added {added} number(s)"
            if duplicates > 0:
                msg += f"\n{duplicates} duplicate(s) ignored"
            if invalid > 0:
                msg += f"\n{invalid} invalid format(s) ignored"

            messagebox.showinfo("Numbers Added", msg)
        elif added == 0:
            messagebox.showwarning("No Numbers", "No valid license numbers found to add")

    def remove_selected_numbers(self):
        """Remove selected numbers from the queue."""
        selected_indices = self.manual_numbers_listbox.curselection()

        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select numbers to remove")
            return

        # Remove in reverse order to maintain indices
        for index in reversed(selected_indices):
            del self.manual_numbers_list[index]

        self.update_manual_listbox()
        self.save_config()

    def clear_manual_numbers(self):
        """Clear all numbers from the queue."""
        if not self.manual_numbers_list:
            return

        response = messagebox.askyesno(
            "Clear All",
            f"Remove all {len(self.manual_numbers_list)} license number(s) from queue?"
        )

        if response:
            self.manual_numbers_list.clear()
            self.update_manual_listbox()
            self.save_config()

    def update_manual_listbox(self):
        """Update the listbox display with current numbers."""
        self.manual_numbers_listbox.delete(0, tk.END)

        for numero in self.manual_numbers_list:
            self.manual_numbers_listbox.insert(tk.END, numero)

        # Update label count
        count = len(self.manual_numbers_list)
        self.manual_queue_label.config(
            text=f"Queue ({count}):"
        )

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
        # Validation based on input mode
        mode = self.input_mode.get()

        if mode == 'csv':
            # CSV mode validation
            if not self.csv_file_path.get():
                messagebox.showerror("Error", "Please select a CSV file")
                return

            if not os.path.exists(self.csv_file_path.get()):
                messagebox.showerror("Error", "CSV file does not exist")
                return
        else:
            # Manual mode validation
            if not self.manual_numbers_list:
                messagebox.showerror("Error", "Please add at least one license number to the queue")
                return

        # Common validation
        if not self.api_url.get():
            messagebox.showerror("Error", "Please enter API URL")
            return

        # Validate biometric directory
        if self.biometric_dir.get():
            if not os.path.exists(self.biometric_dir.get()):
                response = messagebox.askyesno(
                    "Directory Not Found",
                    f"The biometric directory does not exist:\n\n{self.biometric_dir.get()}\n\n"
                    f"Files will be skipped if not found.\n\n"
                    f"Continue anyway?",
                    icon='warning'
                )
                if not response:
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
            biometric_dir = self.biometric_dir.get() if self.biometric_dir.get() else None
            processor = BiometricAPIProcessor(self.api_url.get(), headers, biometric_dir)

            # Get license numbers based on input mode
            mode = self.input_mode.get()

            if mode == 'csv':
                # CSV mode: Read and group CSV
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
            else:
                # Manual mode: Create simple dict from manual numbers
                self.message_queue.put({
                    'type': 'status',
                    'text': f"📋 Processing {len(self.manual_numbers_list)} license number(s) from queue",
                    'tag': 'info'
                })

                # Create grouped_records dict (empty list for each number - no CSV data needed)
                grouped_records = {numero: [] for numero in self.manual_numbers_list}
                records = []  # No CSV records in manual mode

                self.message_queue.put({
                    'type': 'status',
                    'text': f"✓ Ready to process {len(grouped_records)} driver(s)\n",
                    'tag': 'success'
                })

            self.message_queue.put({
                'type': 'status',
                'text': "=" * 80,
                'tag': 'header'
            })

            # Process each driver
            results = {
                'total_csv_rows': len(records) if mode == 'csv' else 0,
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

                # Build payload based on mode
                if mode == 'manual':
                    # Manual mode: Build payload directly from license number (no CSV rows)
                    payload = processor.build_payload_from_license_number(numero_carta)
                else:
                    # CSV mode: Build payload from CSV rows
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
