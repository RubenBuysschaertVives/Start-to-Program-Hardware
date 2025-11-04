#!/usr/bin/env python3
"""
Strudel Pattern Generator - GUI Version
Generates MQTT patterns from sound patterns with a graphical interface
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import re


def generate_mqtt_pattern(sound_pattern, trigger_sounds=None, color_map=None):
    """
    Generate MQTT pattern from sound pattern.

    Args:
        sound_pattern: String like "bd bd hh bd rim bd hh bd, - - - - jazz - - -"
        trigger_sounds: List of sounds that should trigger MQTT (default: ['bd'])
        color_map: Dict mapping sounds to colors (e.g., {'bd': 'purple', 'rim': 'green'})

    Returns:
        tuple: (control_pattern, color_pattern) for MQTT
    """
    if trigger_sounds is None:
        trigger_sounds = ['bd']

    # Split pattern into tokens (words and separators)
    tokens = re.findall(r'\w+|[^\w\s]|\s+', sound_pattern)

    control_tokens = []
    color_tokens = []

    for token in tokens:
        # Keep whitespace and special characters as-is
        if not re.match(r'\w+', token):
            control_tokens.append(token)
            color_tokens.append(token)
        # Replace trigger sounds with 'on' for control
        elif token in trigger_sounds:
            control_tokens.append('on')
            # Add color if mapping exists
            if color_map and token in color_map:
                color_tokens.append(color_map[token])
            else:
                color_tokens.append('on')
        # Replace everything else with '-'
        else:
            control_tokens.append('-')
            color_tokens.append('-')

    control_pattern = ''.join(control_tokens)
    color_pattern = ''.join(color_tokens)

    return control_pattern, color_pattern


class PatternGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Strudel MQTT Pattern Generator")
        self.root.geometry("800x700")

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')

        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Strudel MQTT Pattern Generator",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Sound Pattern:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pattern_entry = ttk.Entry(input_frame, width=50)
        self.pattern_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.pattern_entry.insert(0, "bd bd hh bd rim bd hh bd, - - - - jazz - - -")

        # Color options
        color_frame = ttk.LabelFrame(main_frame, text="Color Options", padding="10")
        color_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        color_frame.columnconfigure(1, weight=1)

        self.use_colors_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(color_frame, text="Use colors",
                       variable=self.use_colors_var,
                       command=self.toggle_color_options).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)

        ttk.Label(color_frame, text="Color for 'bd':").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.bd_color = ttk.Combobox(color_frame, values=['magenta', 'red', 'green', 'blue', 'white', 'cyan', 'yellow', 'random'])
        self.bd_color.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.bd_color.set('magenta')
        self.bd_color.state(['disabled'])

        ttk.Label(color_frame, text="Color for 'rim':").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.rim_color = ttk.Combobox(color_frame, values=['green', 'red', 'magenta', 'blue', 'white', 'cyan', 'yellow', 'random'])
        self.rim_color.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.rim_color.set('green')
        self.rim_color.state(['disabled'])

        # Broker settings
        broker_frame = ttk.LabelFrame(main_frame, text="MQTT Broker Settings", padding="10")
        broker_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        broker_frame.columnconfigure(1, weight=1)

        ttk.Label(broker_frame, text="Broker:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.broker_entry = ttk.Entry(broker_frame)
        self.broker_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.broker_entry.insert(0, "mqtt.rubu.be")

        ttk.Label(broker_frame, text="Port:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.port_entry = ttk.Entry(broker_frame)
        self.port_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.port_entry.insert(0, "9003")

        # Generate button
        generate_btn = ttk.Button(main_frame, text="Generate Pattern", command=self.generate_pattern)
        generate_btn.grid(row=4, column=0, columnspan=2, pady=10)

        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Generated Strudel Code", padding="10")
        output_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)

        self.output_text = scrolledtext.ScrolledText(output_frame, width=70, height=15, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=5)

        ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save to File", command=self.save_to_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_output).pack(side=tk.LEFT, padx=5)

    def toggle_color_options(self):
        """Enable/disable color selection based on checkbox"""
        if self.use_colors_var.get():
            self.bd_color.state(['!disabled'])
            self.rim_color.state(['!disabled'])
        else:
            self.bd_color.state(['disabled'])
            self.rim_color.state(['disabled'])

    def generate_pattern(self):
        """Generate the Strudel pattern and display it"""
        sound_pattern = self.pattern_entry.get().strip()

        if not sound_pattern:
            messagebox.showwarning("Input Required", "Please enter a sound pattern")
            return

        broker = self.broker_entry.get().strip()
        port = self.port_entry.get().strip()
        use_colors = self.use_colors_var.get()

        # Determine trigger sounds and colors
        if use_colors:
            trigger_sounds = ['bd', 'rim']
            color_map = {
                'bd': self.bd_color.get(),
                'rim': self.rim_color.get()
            }
        else:
            trigger_sounds = ['bd']
            color_map = None

        # Generate patterns
        control_pattern, color_pattern = generate_mqtt_pattern(sound_pattern, trigger_sounds, color_map)

        # Generate Strudel code
        code = f'''// MQTT synchroon met instrumenten
const soundPattern = "{sound_pattern}"
const controlPattern = "{control_pattern}"  // Triggers LED flash
'''

        if use_colors and color_map:
            code += f'''const colorPattern = "{color_pattern}"  // Color changes

stack(
  sound(soundPattern).scope(),
  sound(controlPattern).mqtt('strudel', 'qifj3258', 'strudel/control', 'wss://{broker}:{port}/mqtt', 'strudelid437354', 0),
  sound(colorPattern).mqtt('strudel', 'qifj3258', 'strudel/color', 'wss://{broker}:{port}/mqtt', 'strudelid437354', 0)
)
'''
        else:
            code += f'''
stack(
  sound(soundPattern).scope(),
  sound(controlPattern).mqtt('strudel', 'qifj3258', 'strudel/control', 'wss://{broker}:{port}/mqtt', 'strudelid437354', 0)
)
'''

        # Display in output
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, code)

    def copy_to_clipboard(self):
        """Copy output to clipboard"""
        code = self.output_text.get(1.0, tk.END).strip()
        if code:
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("Success", "Code copied to clipboard!")
        else:
            messagebox.showwarning("No Content", "Generate a pattern first")

    def save_to_file(self):
        """Save output to a file"""
        code = self.output_text.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("No Content", "Generate a pattern first")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="strudel_pattern.txt"
        )

        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(code)
                messagebox.showinfo("Success", f"Saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def clear_output(self):
        """Clear the output window"""
        self.output_text.delete(1.0, tk.END)


def main():
    root = tk.Tk()
    app = PatternGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
