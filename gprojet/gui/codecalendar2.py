import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar
from logic.todo_logic import add_task_to_date, get_tasks_for_date, delete_task_by_index, update_task_in_date, load_tasks, save_tasks
from datetime import datetime
import json

class CalendarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Parental Control Calendar 📅")
        self.geometry("1000x700")
        self.minsize(900, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Enhanced color palette
        self.colors = {
            "background": "#2C3E50",
            "card": "#34495E",
            "accent": "#3498DB",
            "text": "#ECF0F1",
            "danger": "#E74C3C",
            "success": "#2ECC71"
        }
        self.configure(fg_color=self.colors["background"])

        # Variables
        self.selected_date = None
        self.tasks = []
        self.selected_task_index = None

        # Initialize UI
        self.create_widgets()
        self.setup_error_handling()

    def setup_error_handling(self):
        """Configure global exception handling"""
        self.report_callback_exception = self.handle_error

    def handle_error(self, exc, val, tb):
        """Global error handler"""
        messagebox.showerror("Error", f"An unexpected error occurred:\n{str(val)}")
        self.after(100, self.reset_ui_state)

    def reset_ui_state(self):
        """Reset UI to safe state after error"""
        try:
            self.reset_form()
            self.refresh_tasks()
        except Exception:
            pass

    def create_widgets(self):
        """Create application widgets with enhanced UX"""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left Column - Calendar
        self.create_calendar_frame(main_frame)

        # Right Column - Task Management
        self.create_task_management_frame(main_frame)

    def create_calendar_frame(self, parent):
        """Create calendar section with error handling"""
        left_frame = ctk.CTkFrame(parent, fg_color=self.colors["card"])
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        try:
            self.calendar = Calendar(
                left_frame,
                selectmode="day",
                font=("Arial", 14),
                date_pattern="yyyy-mm-dd"
            )
            self.calendar.pack(pady=15, padx=15, fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Calendar Error", f"Failed to initialize calendar: {str(e)}")
            raise

        ctk.CTkButton(
            left_frame,
            text="Select Date 📅",
            command=self.safe_select_date,
            font=("Arial", 14, "bold"),
            fg_color=self.colors["accent"],
            hover_color="#2980B9",
            height=40
        ).pack(pady=10, padx=10, fill="x")

    def create_task_management_frame(self, parent):
        """Create task management section with enhanced features"""
        right_frame = ctk.CTkFrame(parent, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Title with task count
        self.title_label = ctk.CTkLabel(
            right_frame,
            text="Today's Tasks (0) 📝",
            font=("Helvetica", 24, "bold"),
            text_color=self.colors["text"]
        )
        self.title_label.pack(pady=(0, 15))

        # Task display with scrollbar
        self.task_display_frame = ctk.CTkFrame(right_frame, fg_color=self.colors["card"])
        self.task_display_frame.pack(fill="both", expand=True, pady=(0, 15))

        self.tasks_textbox = ctk.CTkTextbox(
            self.task_display_frame,
            font=("Arial", 14),
            wrap="word",
            fg_color=self.colors["card"],
            text_color=self.colors["text"]
        )
        self.tasks_textbox.pack(fill="both", expand=True, padx=5, pady=5)

        # Action buttons
        self.create_action_buttons(right_frame)

        # Task input form
        self.create_task_input_form(right_frame)

    def create_action_buttons(self, parent):
        """Create action buttons with modern UX"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 15))

        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete Task 🗑️",
            command=self.confirm_delete_task,
            font=("Arial", 14),
            fg_color=self.colors["danger"],
            hover_color="#C0392B",
            state="disabled",
            width=150
        )
        self.delete_btn.pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Sort by Time ⏱️",
            command=self.sort_tasks_by_time,
            font=("Arial", 14),
            fg_color=self.colors["accent"],
            hover_color="#2980B9",
            width=150
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Clear Form ✨",
            command=self.reset_form,
            font=("Arial", 14),
            fg_color="#9B59B6",
            hover_color="#8E44AD"
        ).pack(side="right", padx=5)

    def create_task_input_form(self, parent):
        """Create task input form with validation"""
        form_frame = ctk.CTkFrame(parent, fg_color=self.colors["card"])
        form_frame.pack(fill="x", pady=10)

        # Time inputs
        time_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        time_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(time_frame, text="Start Time:", font=("Arial", 14)).pack(side="left", padx=5)
        self.start_hour = ctk.CTkOptionMenu(time_frame, values=[f"{i:02d}" for i in range(24)], width=60)
        self.start_hour.pack(side="left", padx=5)
        self.start_minute = ctk.CTkOptionMenu(time_frame, values=[f"{i:02d}" for i in range(60)], width=60)
        self.start_minute.pack(side="left", padx=5)

        ctk.CTkLabel(time_frame, text="End Time:", font=("Arial", 14)).pack(side="left", padx=(15, 5))
        self.end_hour = ctk.CTkOptionMenu(time_frame, values=[f"{i:02d}" for i in range(24)], width=60)
        self.end_hour.pack(side="left", padx=5)
        self.end_minute = ctk.CTkOptionMenu(time_frame, values=[f"{i:02d}" for i in range(60)], width=60)
        self.end_minute.pack(side="left", padx=5)

        # Task input
        self.task_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter task description...",
            font=("Arial", 14),
            height=40
        )
        self.task_entry.pack(fill="x", pady=10)

        # Submit button
        self.submit_btn = ctk.CTkButton(
            form_frame,
            text="Add Task ➕",
            command=self.add_task_with_time,
            font=("Arial", 14, "bold"),
            fg_color=self.colors["success"],
            hover_color="#27AE60",
            height=40
        )
        self.submit_btn.pack(fill="x")

    def safe_select_date(self):
        """Safe date selection with error handling"""
        try:
            self.selected_date = self.calendar.get_date()
            if self.selected_date:
                self.refresh_tasks()
                self.title_label.configure(text=f"Tasks for {self.selected_date} ({len(self.tasks)}) 📝")
        except Exception as e:
            messagebox.showerror("Date Error", f"Failed to select date: {str(e)}")

    def refresh_tasks(self):
        """Refresh task display with enhanced features"""
        try:
            self.tasks_textbox.configure(state="normal")
            self.tasks_textbox.delete("1.0", "end")

            if not self.selected_date:
                return

            self.tasks = get_tasks_for_date(self.selected_date)
            self.title_label.configure(text=f"Tasks for {self.selected_date} ({len(self.tasks)}) 📝")

            if not self.tasks:
                self.tasks_textbox.insert("end", "No tasks for this date. Add some! 📅\n")
            else:
                for idx, task in enumerate(self.tasks, 1):
                    task_str = f"{idx}. ⏰ {task['start_time']} - {task['end_time']}: {task['task']}\n"
                    self.tasks_textbox.insert("end", task_str)
                    
                    # Make task clickable
                    tag = f"task_{idx}"
                    self.tasks_textbox.tag_add(tag, f"{idx}.0", f"{idx}.end")
                    self.tasks_textbox.tag_config(tag, foreground="#3498DB", underline=True)
                    self.tasks_textbox.tag_bind(tag, "<Button-1>", lambda e, i=idx-1: self.select_task(i))

            self.tasks_textbox.configure(state="disabled")
            self.update_button_states()

        except json.JSONDecodeError:
            messagebox.showerror("Data Error", "Corrupted tasks data. Resetting...")
            save_tasks({})
            self.tasks = []
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Failed to refresh tasks: {str(e)}")

    def update_button_states(self):
        """Update UI button states based on current selection"""
        if self.selected_task_index is not None and 0 <= self.selected_task_index < len(self.tasks):
            self.delete_btn.configure(state="normal")
            self.submit_btn.configure(text="Update Task ✏️", command=self.update_task)
        else:
            self.delete_btn.configure(state="disabled")
            self.submit_btn.configure(text="Add Task ➕", command=self.add_task_with_time)

    def select_task(self, index):
        """Select task with enhanced validation"""
        try:
            if not (0 <= index < len(self.tasks)):
                raise IndexError("Invalid task index")

            task = self.tasks[index]
            self.task_entry.delete(0, "end")
            self.task_entry.insert(0, task["task"])

            start_h, start_m = task["start_time"].split(":")
            end_h, end_m = task["end_time"].split(":")
            
            self.start_hour.set(start_h)
            self.start_minute.set(start_m)
            self.end_hour.set(end_h)
            self.end_minute.set(end_m)

            self.selected_task_index = index
            self.update_button_states()

        except Exception as e:
            messagebox.showerror("Selection Error", f"Failed to select task: {str(e)}")
            self.reset_form()

    def confirm_delete_task(self):
        """Confirm task deletion with modern dialog"""
        if self.selected_task_index is None:
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete this task?\nThis action cannot be undone.",
            icon="warning"
        )
        
        if confirm:
            self.delete_task()

    def delete_task(self):
        """Delete selected task with error handling"""
        try:
            if delete_task_by_index(self.selected_date, self.selected_task_index):
                messagebox.showinfo("Success", "Task deleted successfully!")
                self.reset_form()
                self.refresh_tasks()
            else:
                messagebox.showerror("Error", "Failed to delete task")
        except Exception as e:
            messagebox.showerror("Deletion Error", f"Task deletion failed: {str(e)}")

    def sort_tasks_by_time(self):
        """Sort tasks by start time with visual feedback"""
        try:
            if not self.tasks:
                return

            self.tasks.sort(key=lambda x: (
                datetime.strptime(x["start_time"], "%H:%M"), 
                datetime.strptime(x["end_time"], "%H:%M")
            ))

            # Update stored data
            tasks_data = load_tasks()
            tasks_data[self.selected_date] = self.tasks
            save_tasks(tasks_data)

            self.refresh_tasks()
            messagebox.showinfo("Sorted", "Tasks sorted by time successfully!")

        except Exception as e:
            messagebox.showerror("Sort Error", f"Failed to sort tasks: {str(e)}")

    def add_task_with_time(self):
        """Add new task with comprehensive validation"""
        try:
            if not self.validate_inputs():
                return

            task = self.task_entry.get().strip()
            start_time = f"{self.start_hour.get()}:{self.start_minute.get()}"
            end_time = f"{self.end_hour.get()}:{self.end_minute.get()}"

            if add_task_to_date(self.selected_date, task, start_time, end_time):
                messagebox.showinfo("Success", "Task added successfully! ✅")
                self.reset_form()
                self.refresh_tasks()
            else:
                messagebox.showerror("Error", "Failed to add task")

        except Exception as e:
            messagebox.showerror("Add Error", f"Failed to add task: {str(e)}")

    def update_task(self):
        """Update existing task with validation"""
        try:
            if not self.validate_inputs():
                return

            task = self.task_entry.get().strip()
            start_time = f"{self.start_hour.get()}:{self.start_minute.get()}"
            end_time = f"{self.end_hour.get()}:{self.end_minute.get()}"

            if update_task_in_date(self.selected_date, self.selected_task_index, task, start_time, end_time):
                messagebox.showinfo("Success", "Task updated successfully! ✏️")
                self.reset_form()
                self.refresh_tasks()
            else:
                messagebox.showerror("Error", "Failed to update task")

        except Exception as e:
            messagebox.showerror("Update Error", f"Failed to update task: {str(e)}")

    def validate_inputs(self):
        """Validate all form inputs"""
        if not self.selected_date:
            messagebox.showwarning("Warning", "Please select a date first")
            return False

        task = self.task_entry.get().strip()
        if not task:
            messagebox.showwarning("Warning", "Please enter a task description")
            return False

        start_time = f"{self.start_hour.get()}:{self.start_minute.get()}"
        end_time = f"{self.end_hour.get()}:{self.end_minute.get()}"

        try:
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = datetime.strptime(end_time, "%H:%M")
            
            if start_dt >= end_dt:
                messagebox.showerror("Error", "Start time must be before end time")
                return False
                
            return True
            
        except ValueError:
            messagebox.showerror("Error", "Invalid time format (use HH:MM)")
            return False

    def reset_form(self):
        """Reset form to default state"""
        try:
            self.task_entry.delete(0, "end")
            self.start_hour.set("00")
            self.start_minute.set("00")
            self.end_hour.set("00")
            self.end_minute.set("00")
            self.selected_task_index = None
            self.update_button_states()
        except Exception as e:
            messagebox.showerror("Reset Error", f"Failed to reset form: {str(e)}")

