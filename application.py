import tkinter as tk
from threading import Thread, Event
import pyautogui
import time
from datetime import datetime, timedelta
from pynput import mouse, keyboard

class PreventIdleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prevent Idle App")
        self.running = False
        self.stop_event = Event()
        self.last_activity_time = datetime.now()

        # Interval Input
        tk.Label(root, text="Interval (seconds):").grid(row=0, column=0, padx=5, pady=5)
        self.interval_entry = tk.Entry(root)
        self.interval_entry.grid(row=0, column=1, padx=5, pady=5)
        self.interval_entry.insert(0, "30")  # Default interval

        # Time Window 1
        tk.Label(root, text="Time Window 1 Start (HH:MM):").grid(row=1, column=0, padx=5, pady=5)
        self.start_time1_entry = tk.Entry(root)
        self.start_time1_entry.grid(row=1, column=1, padx=5, pady=5)
        self.start_time1_entry.insert(0, "09:00")  # Default start time

        tk.Label(root, text="Time Window 1 End (HH:MM):").grid(row=2, column=0, padx=5, pady=5)
        self.end_time1_entry = tk.Entry(root)
        self.end_time1_entry.grid(row=2, column=1, padx=5, pady=5)
        self.end_time1_entry.insert(0, "12:00")  # Default end time

        # Time Window 2
        tk.Label(root, text="Time Window 2 Start (HH:MM):").grid(row=3, column=0, padx=5, pady=5)
        self.start_time2_entry = tk.Entry(root)
        self.start_time2_entry.grid(row=3, column=1, padx=5, pady=5)
        self.start_time2_entry.insert(0, "13:00")  # Default start time

        tk.Label(root, text="Time Window 2 End (HH:MM):").grid(row=4, column=0, padx=5, pady=5)
        self.end_time2_entry = tk.Entry(root)
        self.end_time2_entry.grid(row=4, column=1, padx=5, pady=5)
        self.end_time2_entry.insert(0, "17:00")  # Default end time

        # Start Button
        self.start_button = tk.Button(root, text="Start", command=self.start)
        self.start_button.grid(row=5, column=0, padx=5, pady=5)

        # Stop Button
        self.stop_button = tk.Button(root, text="Stop", command=self.stop, state="disabled")
        self.stop_button.grid(row=5, column=1, padx=5, pady=5)

        # Status Label
        self.status_label = tk.Label(root, text="Status: Stopped", fg="red")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=5)

    def track_user_activity(self):
        """
        Track user activity (mouse or keyboard) and update the last activity timestamp.
        """
        def on_any_event(event):
            self.last_activity_time = datetime.now()

        # Start mouse and keyboard listeners
        self.mouse_listener = mouse.Listener(on_click=on_any_event, on_move=on_any_event, on_scroll=on_any_event)
        self.keyboard_listener = keyboard.Listener(on_press=on_any_event)

        self.mouse_listener.start()
        self.keyboard_listener.start()

    def perform_alt_tab(self, interval, time_windows):
        """
        Perform Alt+Tab switching only if the defined interval has elapsed since the last user activity.
        """
        try:
            while not self.stop_event.is_set():
                now = datetime.now().time()
                time_since_last_activity = datetime.now() - self.last_activity_time

                # Check if the current time is within any of the time windows
                if any(start <= now <= end for start, end in time_windows):
                    # Check if the interval has elapsed since the last activity
                    if time_since_last_activity.total_seconds() >= interval:
                        pyautogui.keyDown("alt")
                        pyautogui.press("tab")
                        pyautogui.keyUp("alt")
                        pyautogui.keyDown("alt")
                        pyautogui.press("tab")
                        pyautogui.keyUp("alt")

                time.sleep(1)
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def start(self):
        """
        Start the prevent idle function.
        """
        try:
            # Get interval and validate it
            interval = float(self.interval_entry.get())
            if interval <= 0:
                self.update_status("Interval must be greater than 0!", "red")
                return

            # Get start and end times for both time windows
            try:
                start_time1 = datetime.strptime(self.start_time1_entry.get(), "%H:%M").time()
                end_time1 = datetime.strptime(self.end_time1_entry.get(), "%H:%M").time()
                start_time2 = datetime.strptime(self.start_time2_entry.get(), "%H:%M").time()
                end_time2 = datetime.strptime(self.end_time2_entry.get(), "%H:%M").time()
            except ValueError:
                self.update_status("Invalid time format! Use HH:MM.", "red")
                return

            time_windows = [(start_time1, end_time1), (start_time2, end_time2)]

            # Start tracking user activity
            self.track_user_activity()

            # Set running state and start the thread
            self.running = True
            self.stop_event.clear()
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.update_status("Status: Running", "green")

            # Run the Alt+Tab function in a separate thread
            self.thread = Thread(
                target=self.perform_alt_tab, args=(interval, time_windows), daemon=True
            )
            self.thread.start()
        except ValueError:
            self.update_status("Invalid interval value!", "red")

    def stop(self):
        """
        Stop the prevent idle function.
        """
        self.running = False
        self.stop_event.set()

        # Stop activity listeners
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.update_status("Status: Stopped", "red")

    def update_status(self, message, color):
        """
        Update the status label.
        """
        self.status_label.config(text=message, fg=color)


if __name__ == "__main__":
    root = tk.Tk()
    app = PreventIdleApp(root)
    root.mainloop()
