"""
IBM BOB - Certification Workflow GUI
====================================

Graphical user interface for managing certification workflows.

Features:
- Select workflow action (Status Notifications, Completion Reminders, or Industry Badge Reminders)
- Test mode with configurable test email
- Email limiting for testing
- Draft mode toggle
- Real-time progress display
- Results summary
- Colorful and vibrant design

Author: IBM BOB
Date: 2026-05-22
Version: 2.0.0
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import logging
from pathlib import Path
from datetime import datetime
from config_loader import ConfigLoader
from certification_workflow_outlook import CertificationWorkflowOutlook
from certification_reminder_workflow import CertificationReminderWorkflow
from industry_badge_workflow import IndustryBadgeWorkflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('certification_gui.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TextHandler(logging.Handler):
    """Custom logging handler to display logs in GUI text widget."""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.configure(state='disabled')
            self.text_widget.see(tk.END)
        self.text_widget.after(0, append)


class CertificationGUI:
    """Main GUI application for certification workflows."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 IBM CERTIFICATIONS TRACKER")
        self.root.geometry("1000x750")
        
        # Color scheme - Vibrant and professional
        self.colors = {
            'primary': '#0f62fe',      # IBM Blue
            'secondary': '#8a3ffc',    # Purple
            'success': '#24a148',      # Green
            'warning': '#f1c21b',      # Yellow
            'danger': '#da1e28',       # Red
            'info': '#0043ce',         # Dark Blue
            'bg_light': '#f4f4f4',     # Light Gray
            'bg_dark': '#161616',      # Dark Gray
            'text_dark': '#161616',    # Dark Text
            'text_light': '#ffffff',   # White Text
            'accent1': '#ff7eb6',      # Pink
            'accent2': '#82cfff',      # Light Blue
            'accent3': '#42be65',      # Light Green
        }
        
        # Configure root background
        self.root.configure(bg=self.colors['bg_light'])
        
        # Load configuration
        self.config = ConfigLoader()
        
        # Variables
        self.workflow_var = tk.StringVar(value="status")
        self.test_mode_var = tk.BooleanVar(value=True)
        self.draft_mode_var = tk.BooleanVar(value=True)
        self.test_email_var = tk.StringVar(value="")
        self.email_limit_var = tk.IntVar(value=3)
        
        # Running flag
        self.is_running = False
        
        # Create GUI
        self.setup_styles()
        self.create_widgets()
        
        # Setup logging to GUI
        self.setup_logging()
        
        logger.info("Certification Workflow GUI initialized")
    
    def setup_styles(self):
        """Configure custom styles for widgets."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel',
                       font=('Segoe UI', 24, 'bold'),
                       foreground=self.colors['primary'],
                       background=self.colors['bg_light'])
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 12),
                       foreground=self.colors['text_dark'],
                       background=self.colors['bg_light'])
        
        style.configure('Header.TLabelframe',
                       background=self.colors['bg_light'],
                       foreground=self.colors['primary'],
                       borderwidth=2,
                       relief='solid')
        
        style.configure('Header.TLabelframe.Label',
                       font=('Segoe UI', 11, 'bold'),
                       foreground=self.colors['primary'],
                       background=self.colors['bg_light'])
        
        # Radio buttons with colors
        style.configure('Status.TRadiobutton',
                       font=('Segoe UI', 10),
                       foreground=self.colors['success'],
                       background=self.colors['bg_light'])
        
        style.configure('Reminder.TRadiobutton',
                       font=('Segoe UI', 10),
                       foreground=self.colors['danger'],
                       background=self.colors['bg_light'])
        
        style.configure('Badge.TRadiobutton',
                       font=('Segoe UI', 10),
                       foreground=self.colors['warning'],
                       background=self.colors['bg_light'])
        
        # Buttons
        style.configure('Primary.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       foreground=self.colors['text_light'],
                       background=self.colors['primary'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=10)
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['info'])])
        
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 10),
                       foreground=self.colors['text_dark'],
                       background=self.colors['bg_light'],
                       borderwidth=1,
                       focuscolor='none',
                       padding=8)
        
        # Checkbuttons
        style.configure('TCheckbutton',
                       font=('Segoe UI', 10),
                       foreground=self.colors['text_dark'],
                       background=self.colors['bg_light'])
    
    def create_widgets(self):
        """Create all GUI widgets."""
        
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=self.colors['bg_light'], padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Header Section with gradient effect
        header_frame = tk.Frame(main_frame, bg=self.colors['primary'], height=100)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        # Title with icon
        title_label = tk.Label(
            header_frame,
            text="🎯 IBM CERTIFICATIONS TRACKER",
            font=('Segoe UI', 26, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['primary'],
            pady=15
        )
        title_label.grid(row=0, column=0)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Automated Certification Management System for Westpac Banking Corporation",
            font=('Segoe UI', 10),
            fg=self.colors['accent2'],
            bg=self.colors['primary'],
            pady=5
        )
        subtitle_label.grid(row=1, column=0)
        
        # Workflow Selection Frame with colorful cards
        workflow_frame = tk.LabelFrame(
            main_frame,
            text="📋 Select Workflow Action",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['primary'],
            bg=self.colors['bg_light'],
            padx=15,
            pady=15
        )
        workflow_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Card 1: Status Notifications
        card1 = tk.Frame(workflow_frame, bg='white', relief='raised', borderwidth=2)
        card1.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        tk.Radiobutton(
            card1,
            text="📊 Send Certification Status Notifications",
            variable=self.workflow_var,
            value="status",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['success'],
            bg='white',
            activebackground='white',
            selectcolor=self.colors['accent3'],
            padx=10,
            pady=10
        ).pack(anchor=tk.W)
        
        tk.Label(
            card1,
            text="For employees WITH certifications - sends detailed certification status",
            font=('Segoe UI', 9),
            fg='gray',
            bg='white',
            padx=30
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Card 2: Completion Reminders
        card2 = tk.Frame(workflow_frame, bg='white', relief='raised', borderwidth=2)
        card2.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        tk.Radiobutton(
            card2,
            text="⚠️ Send Certification Completion Reminders",
            variable=self.workflow_var,
            value="reminder",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['danger'],
            bg='white',
            activebackground='white',
            selectcolor=self.colors['accent1'],
            padx=10,
            pady=10
        ).pack(anchor=tk.W)
        
        tk.Label(
            card2,
            text="For employees WITHOUT certifications - sends reminder with manager CC",
            font=('Segoe UI', 9),
            fg='gray',
            bg='white',
            padx=30
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Card 3: Industry Badge Reminders
        card3 = tk.Frame(workflow_frame, bg='white', relief='raised', borderwidth=2)
        card3.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        tk.Radiobutton(
            card3,
            text="🎯 Send Industry Badge Completion Reminders",
            variable=self.workflow_var,
            value="badge",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['warning'],
            bg='white',
            activebackground='white',
            selectcolor=self.colors['warning'],
            padx=10,
            pady=10
        ).pack(anchor=tk.W)
        
        tk.Label(
            card3,
            text="For employees with 'No Badge' status - sends Industry Badge reminder with manager CC",
            font=('Segoe UI', 9),
            fg='gray',
            bg='white',
            padx=30
        ).pack(anchor=tk.W, pady=(0, 10))
        
        workflow_frame.columnconfigure(0, weight=1)
        
        # Configuration Frame
        config_frame = tk.LabelFrame(
            main_frame,
            text="⚙️ Configuration",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['primary'],
            bg=self.colors['bg_light'],
            padx=15,
            pady=15
        )
        config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Test Mode
        test_check = tk.Checkbutton(
            config_frame,
            text="🧪 Test Mode (Enable for testing)",
            variable=self.test_mode_var,
            command=self.toggle_test_mode,
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['info'],
            bg=self.colors['bg_light'],
            activebackground=self.colors['bg_light'],
            selectcolor=self.colors['accent2']
        )
        test_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Test Email
        tk.Label(
            config_frame,
            text="📧 Test Email:",
            font=('Segoe UI', 10),
            fg=self.colors['text_dark'],
            bg=self.colors['bg_light']
        ).grid(row=1, column=0, sticky=tk.W, padx=(20, 10), pady=5)
        
        self.test_email_entry = tk.Entry(
            config_frame,
            textvariable=self.test_email_var,
            width=40,
            font=('Segoe UI', 10),
            relief='solid',
            borderwidth=1
        )
        self.test_email_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Email Limit
        tk.Label(
            config_frame,
            text="📊 Email Limit:",
            font=('Segoe UI', 10),
            fg=self.colors['text_dark'],
            bg=self.colors['bg_light']
        ).grid(row=2, column=0, sticky=tk.W, padx=(20, 10), pady=5)
        
        limit_frame = tk.Frame(config_frame, bg=self.colors['bg_light'])
        limit_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        tk.Spinbox(
            limit_frame,
            from_=0,
            to=100,
            textvariable=self.email_limit_var,
            width=10,
            font=('Segoe UI', 10),
            relief='solid',
            borderwidth=1
        ).pack(side=tk.LEFT)
        
        tk.Label(
            limit_frame,
            text=" (0 = no limit)",
            font=('Segoe UI', 9),
            fg='gray',
            bg=self.colors['bg_light']
        ).pack(side=tk.LEFT, padx=5)
        
        # Draft Mode
        draft_check = tk.Checkbutton(
            config_frame,
            text="📝 Draft Mode (Create drafts instead of sending)",
            variable=self.draft_mode_var,
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['secondary'],
            bg=self.colors['bg_light'],
            activebackground=self.colors['bg_light'],
            selectcolor=self.colors['accent1']
        )
        draft_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        config_frame.columnconfigure(1, weight=1)
        
        # Action Buttons Frame
        button_frame = tk.Frame(main_frame, bg=self.colors['bg_light'])
        button_frame.grid(row=3, column=0, pady=15)
        
        # Send Button (Primary)
        self.send_button = tk.Button(
            button_frame,
            text="📧 Send Emails",
            command=self.send_emails,
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['primary'],
            activebackground=self.colors['info'],
            activeforeground=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            padx=30,
            pady=12,
            cursor='hand2'
        )
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        # Clear Button
        tk.Button(
            button_frame,
            text="🔄 Clear Log",
            command=self.clear_log,
            font=('Segoe UI', 10),
            fg=self.colors['text_dark'],
            bg='white',
            activebackground=self.colors['bg_light'],
            relief='solid',
            borderwidth=1,
            padx=20,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        # Exit Button
        tk.Button(
            button_frame,
            text="❌ Exit",
            command=self.root.quit,
            font=('Segoe UI', 10),
            fg=self.colors['text_light'],
            bg=self.colors['danger'],
            activebackground='#ba1b23',
            activeforeground=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            padx=20,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        # Progress and Log Frame
        log_frame = tk.LabelFrame(
            main_frame,
            text="📊 Progress & Log",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['primary'],
            bg=self.colors['bg_light'],
            padx=10,
            pady=10
        )
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        
        # Progress bar with custom colors
        self.progress = ttk.Progressbar(
            log_frame,
            mode='indeterminate',
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configure progress bar style
        style = ttk.Style()
        style.configure('Custom.Horizontal.TProgressbar',
                       background=self.colors['primary'],
                       troughcolor=self.colors['bg_light'],
                       borderwidth=0,
                       thickness=20)
        
        # Log text area with custom colors
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=90,
            height=15,
            state='disabled',
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='white',
            relief='flat',
            borderwidth=0
        )
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar with gradient
        status_frame = tk.Frame(main_frame, bg=self.colors['primary'], height=30)
        status_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        
        self.status_var = tk.StringVar(value="✅ Ready")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 9),
            fg=self.colors['text_light'],
            bg=self.colors['primary'],
            anchor=tk.W,
            padx=10,
            pady=5
        )
        status_label.pack(fill=tk.X)
        
        # Initialize test mode state
        self.toggle_test_mode()
    
    def setup_logging(self):
        """Setup logging to display in GUI."""
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(text_handler)
    
    def toggle_test_mode(self):
        """Enable/disable test mode controls."""
        if self.test_mode_var.get():
            self.test_email_entry.config(state='normal', bg='white')
        else:
            self.test_email_entry.config(state='disabled', bg=self.colors['bg_light'])
    
    def clear_log(self):
        """Clear the log text area."""
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        logger.info("🧹 Log cleared")
    
    def validate_inputs(self):
        """Validate user inputs before running workflow."""
        if self.test_mode_var.get():
            test_email = self.test_email_var.get().strip()
            if test_email and '@' not in test_email:
                messagebox.showerror("Invalid Email", "Please enter a valid test email address")
                return False
        
        return True
    
    def send_emails(self):
        """Send emails based on selected workflow."""
        if self.is_running:
            messagebox.showwarning("Already Running", "A workflow is already running. Please wait.")
            return
        
        if not self.validate_inputs():
            return
        
        # Confirm action
        workflow_names = {
            "status": "📊 Certification Status Notifications",
            "reminder": "⚠️ Certification Completion Reminders",
            "badge": "🎯 Industry Badge Completion Reminders"
        }
        workflow_name = workflow_names.get(self.workflow_var.get(), "Unknown")
        mode = "📝 DRAFT MODE" if self.draft_mode_var.get() else "📧 SEND MODE"
        test_info = f"\n🧪 Test Mode: {self.test_mode_var.get()}"
        if self.test_mode_var.get():
            test_email = self.test_email_var.get().strip()
            if test_email:
                test_info += f"\n📧 Test Email: {test_email}"
            test_info += f"\n📊 Email Limit: {self.email_limit_var.get()}"
        
        message = f"Ready to run:\n\n{workflow_name}\n{mode}{test_info}\n\nContinue?"
        
        if not messagebox.askyesno("Confirm Action", message):
            return
        
        # Run workflow in separate thread
        self.is_running = True
        self.send_button.config(state='disabled', bg='gray')
        self.progress.start()
        self.status_var.set("⏳ Running workflow...")
        
        thread = threading.Thread(target=self.run_workflow, daemon=True)
        thread.start()
    
    def run_workflow(self):
        """Run the selected workflow."""
        try:
            workflow_type = self.workflow_var.get()
            draft_mode = self.draft_mode_var.get()
            test_mode = self.test_mode_var.get()
            test_email = self.test_email_var.get().strip() if test_mode else None
            email_limit = self.email_limit_var.get() if test_mode else 0
            
            logger.info("=" * 80)
            logger.info(f"🚀 Starting workflow: {workflow_type}")
            logger.info(f"📝 Draft mode: {draft_mode}")
            logger.info(f"🧪 Test mode: {test_mode}")
            if test_email:
                logger.info(f"📧 Test email: {test_email}")
            if email_limit > 0:
                logger.info(f"📊 Email limit: {email_limit}")
            logger.info("=" * 80)
            
            if workflow_type == "status":
                # Certification Status Notifications
                workflow = CertificationWorkflowOutlook(
                    config=self.config,
                    draft_mode=draft_mode
                )
                results = workflow.run(
                    send_emails=True,
                    test_mode=test_mode,
                    test_email=test_email,
                    limit_emails=email_limit
                )
            elif workflow_type == "reminder":
                # Certification Completion Reminders
                workflow = CertificationReminderWorkflow(
                    config=self.config,
                    draft_mode=draft_mode
                )
                results = workflow.run(
                    test_mode=test_mode,
                    test_email=test_email,
                    limit=email_limit
                )
            else:  # badge
                # Industry Badge Reminders
                workflow = IndustryBadgeWorkflow(
                    config=self.config,
                    draft_mode=draft_mode
                )
                results = workflow.run(
                    test_mode=test_mode,
                    test_email=test_email,
                    limit=email_limit
                )
            
            # Show results
            self.show_results(results)
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}", exc_info=True)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Workflow failed:\n{str(e)}"))
        
        finally:
            self.root.after(0, self.workflow_complete)
    
    def show_results(self, results):
        """Display workflow results."""
        def display():
            logger.info("\n" + "=" * 80)
            logger.info("📊 WORKFLOW RESULTS")
            logger.info("=" * 80)
            for key, value in results.items():
                if key not in ['errors']:
                    logger.info(f"{key}: {value}")
            logger.info("=" * 80)
            
            if results.get('success'):
                messagebox.showinfo(
                    "✅ Success",
                    f"Workflow completed successfully!\n\n"
                    f"Check Outlook Drafts folder to review emails."
                )
            else:
                messagebox.showwarning(
                    "⚠️ Completed with Errors",
                    f"Workflow completed but encountered errors.\n"
                    f"Check the log for details."
                )
        
        self.root.after(0, display)
    
    def workflow_complete(self):
        """Reset UI after workflow completes."""
        self.is_running = False
        self.send_button.config(state='normal', bg=self.colors['primary'])
        self.progress.stop()
        self.status_var.set("✅ Ready")


def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    
    # Create and run GUI
    app = CertificationGUI(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()

# Made with Bob
