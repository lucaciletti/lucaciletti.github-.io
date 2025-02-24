import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import re
import sympy as sp

current_function = None
current_derivative = None
derivative_line = None
x_values = None
computed_derivative_values = None

x_sym = sp.symbols('x')

def preprocess_function_string(func_str):
    func_str = func_str.replace('^', '**')
    func_str = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', func_str)
    func_str = re.sub(r'(\))(\d)', r'\1*\2', func_str)
    func_str = re.sub(r'(\))([a-zA-Z])', r'\1*\2', func_str)
    return func_str

def compute_derivative():
    global current_function, current_derivative, derivative_line, x_values, computed_derivative_values
    func_str = function_entry.get().strip()
    if not func_str:
        messagebox.showwarning("Input Error", "Please enter a function")
        return

    processed_str = preprocess_function_string(func_str)
    
    try:
        expr_sym = sp.sympify(processed_str)
        deriv_sym = sp.diff(expr_sym, x_sym)
        deriv_text = sp.pretty(deriv_sym, use_unicode=True)
        deriv_var.set("Symbolic Derivative: " + deriv_text)
    except Exception as e:
        messagebox.showerror("Symbolic Error", f"Error computing symbolic derivative: {e}")
        return

    try:
        f = lambda x: eval(processed_str, {"x": x, **math.__dict__})
        current_function = f
    except Exception as e:
        messagebox.showerror("Function Error", f"Invalid function: {e}")
        return
    
    h = 1e-5
    derivative = lambda x: (f(x + h) - f(x - h)) / (2 * h)
    current_derivative = derivative

    x_values = np.linspace(-10, 10, 400)
    
    try:
        y_function = [f(x) for x in x_values]
        computed_derivative_values = np.array([derivative(x) for x in x_values])
    except Exception as e:
        messagebox.showerror("Evaluation Error", f"Error evaluating function: {e}")
        return
    
    ax.clear()
    ax.plot(x_values, y_function, label='Original Function')
    
    scale = float(slider.get())
    derivative_plot_values = scale * computed_derivative_values
    global derivative_line
    derivative_line, = ax.plot(x_values, derivative_plot_values, label='Derivative', linestyle='--')
    
    ax.set_title('Function and Scaled Derivative')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.legend()
    ax.grid(True)
    
    canvas.draw()

def update_derivative(val):
    global derivative_line, computed_derivative_values, x_values
    if derivative_line is None or computed_derivative_values is None:
        return
    try:
        scale = float(val)
        new_values = scale * computed_derivative_values
        derivative_line.set_ydata(new_values)
        canvas.draw()
    except Exception:
        pass

root = tk.Tk()
root.title("Function Derivative Visualizer")

input_frame = ttk.Frame(root)
input_frame.pack(pady=10, padx=10, fill=tk.X)

ttk.Label(input_frame, text="f(x) =").pack(side=tk.LEFT)
function_entry = ttk.Entry(input_frame, width=30)
function_entry.pack(side=tk.LEFT, padx=5)
ttk.Button(input_frame, text="Plot", command=compute_derivative).pack(side=tk.LEFT)

deriv_var = tk.StringVar()
deriv_var.set("Symbolic Derivative: ")
deriv_label = ttk.Label(root, textvariable=deriv_var, font=('Courier', 12))
deriv_label.pack(pady=5)

fig, ax = plt.subplots(figsize=(7, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

slider = tk.Scale(root, from_=-10, to=10, orient=tk.HORIZONTAL, resolution=0.1,
                  label="Slope", command=update_derivative)
slider.set(1)
slider.pack(pady=10, padx=10, fill=tk.X)

ax.grid(True)
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)

root.mainloop()
