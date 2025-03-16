import csv
import tkinter as tk
from tkinter import messagebox, filedialog


class Process:
    def __init__(self, id, arrival_time, burst_time, priority_level):
        self.id = id
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority_level = priority_level
        self.completion_time = 0
        self.tat = 0
        self.wt = 0
        self.remaining_time = burst_time


def readfile(filename):
    processes = []
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            processes.append(Process(
                int(row['TaskID']),
                int(row['ArrivalTime']),
                int(row['CPUBurstTime']),
                int(row['PriorityLevel'])
            ))
    return processes

def sort_fcfs(processes):
    processes.sort(key=lambda p: p.arrival_time)

def sort_sjf(processes):
    processes.sort(key=lambda p: (p.burst_time, p.arrival_time))

def sort_priorityScheduling(processes):
    processes.sort(key=lambda p: p.priority_level)

def calculate_metrics(processes):
    processes[0].completion_time = processes[0].arrival_time + processes[0].burst_time
    for i in range(1, len(processes)):
        if processes[i].arrival_time > processes[i - 1].completion_time:
            processes[i].completion_time = processes[i].arrival_time + processes[i].burst_time
        else:
            processes[i].completion_time = processes[i - 1].completion_time + processes[i].burst_time

    for process in processes:
        process.tat = process.completion_time - process.arrival_time
        process.wt = process.tat - process.burst_time

def display_processes(processes, result_text):
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"{'PID':<10}{'ArrivalTime':<15}{'BurstTime':<15}{'PriorityLevel':<15}{'CompletionTime':<15}{'TurnAroundTime':<15}{'WaitingTime':<15}\n")
    #result_text.insert(tk.END, "PID\tArrivalTime\tBurstTime\tPriorityLevel\tCompletionTime\tTurnAroundTime\tWaitingTime\n")
    for process in processes:
        result_text.insert(
            tk.END,
            f"{process.id:<10}{process.arrival_time:<15}{process.burst_time:<15}{process.priority_level:<15}{process.completion_time:<15}{process.tat:<15}{process.wt:<15}\n"
            #f"{process.id}\t{process.arrival_time}\t\t{process.burst_time}\t\t{process.priority_level}\t\t{process.completion_time}\t\t{process.tat}\t\t{process.wt}\n"
        )

def ganttchart(processes, result_text):
    result_text.insert(tk.END, "Gantt Chart: \n")
    for process in processes:
        result_text.insert(tk.END, f"p{process.id}\t")
    result_text.insert(tk.END, "\n")
    for process in processes:
        result_text.insert(tk.END, f"{process.completion_time}\t")
    result_text.insert(tk.END, "\n")

def round_robin(processes, time_quantum):
    time = 0
    completed = 0  
    n = len(processes)

    while completed < n:
        done = True
        for process in processes:
            if process.remaining_time > 0:
                done = False
                if process.remaining_time > time_quantum:
                    time += time_quantum
                    process.remaining_time -= time_quantum
                else:
                    time += process.remaining_time
                    process.completion_time = time
                    process.remaining_time = 0
                    completed += 1

    for process in processes:
        process.tat = process.completion_time - process.arrival_time
        process.wt = process.tat - process.burst_time

def fcfs(processes, result_text):
    sort_fcfs(processes)
    calculate_metrics(processes)
    display_processes(processes, result_text)
    ganttchart(processes, result_text)

def sjf(processes, result_text):
    sort_sjf(processes)
    calculate_metrics(processes)
    display_processes(processes, result_text)
    ganttchart(processes, result_text)

def priorityscheduling(processes, result_text):
    sort_priorityScheduling(processes)
    calculate_metrics(processes)
    display_processes(processes, result_text)
    ganttchart(processes, result_text)

def reset_processes(processes):
    for process in processes:
        process.completion_time = 0
        process.tat = 0
        process.wt = 0
        process.remaining_time = process.burst_time

def selectalgorithm(processes, algorithmchoice, time_quantum, result_text):
    reset_processes(processes)
    if algorithmchoice == "FCFS":
        fcfs(processes, result_text)
    elif algorithmchoice == "SJF":
        sjf(processes, result_text)
    elif algorithmchoice == "Round Robin":
        round_robin(processes, time_quantum)
        display_processes(processes, result_text)
        ganttchart(processes, result_text)
    else:
        priorityscheduling(processes, result_text)

# Function to open file dialog and get the file path
def open_file_dialog():
    file_path = filedialog.askopenfilename(title="Select a CSV file", filetypes=[("CSV Files", "*.csv")])
    return file_path

def main():
    time_quantum = 2
    file_path = None
    processes = []

    window = tk.Tk()
    window.title("Process Scheduler")

    tk.Label(window, text="Process Scheduler").pack(pady=5)

    def load_file():
        nonlocal file_path, processes
        file_path = open_file_dialog()
        if file_path:
            try:
                processes = readfile(file_path)
                messagebox.showinfo("Success", f"File loaded: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {e}")
        else:
            messagebox.showerror("Error", "No file selected.")

    
    tk.Button(window, text="Select CSV File", command=load_file).pack(pady=5)

    algorithmchoice = tk.StringVar(value="Select Scheduling Algorithm:")
    tk.OptionMenu(window, algorithmchoice, "FCFS", "SJF", "Round Robin", "Priority Scheduling").pack(pady=5)

    tk.Label(window, text="Results:").pack(pady=10)
    frame = tk.Frame(window)
    frame.pack(padx=10, pady=5)

    result_text = tk.Text(window, height=10, width=100)
    result_text.pack(padx=10, pady=5)

    scrollbar = tk.Scrollbar(frame, command=result_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    result_text.config(yscrollcommand=scrollbar.set)

    # Run Scheduling Button
    def run_scheduling():
        if not file_path:
            messagebox.showerror("Error", "Please select a CSV file first.")
            return
        if not algorithmchoice.get() or algorithmchoice.get() == "Select Scheduling Algorithm:":
            messagebox.showerror("Error", "Please select a scheduling algorithm.")
            return
        try:
            processes = readfile(file_path)
            selectalgorithm(processes, algorithmchoice.get(), time_quantum, result_text)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while running the scheduling: {e}")

    tk.Button(window, text="Run Scheduling", command=run_scheduling).pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    main()
