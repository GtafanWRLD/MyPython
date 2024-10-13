import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import struct
import os
import math

class ADFileProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("AD File Compiler/Decompiler")

        # Create a button to load .ad File
        self.load_button = tk.Button(root, text="Load .ad File", command=self.load_ad_file)
        self.load_button.pack(pady=10)

        # Tab control for splines and trees
        self.tab_control = None

        # Variables to hold spline and tree tabs
        self.splines_tabs = []
        self.trees_tabs = []

    def load_ad_file(self):
        # Open file dialog to select .ad file
        file_path = filedialog.askopenfilename(filetypes=[("AD Files", "*.ad")])
        if not file_path:
            return

        try:
            with open(file_path, 'rb') as f:
                # Read tree offsets from 0x8, 0xC, 0x10, and 0x14
                f.seek(0x8)
                tree1_offset = struct.unpack('<I', f.read(4))[0]
                tree2_offset = struct.unpack('<I', f.read(4))[0]
                tree3_offset = struct.unpack('<I', f.read(4))[0]
                tree4_offset = struct.unpack('<I', f.read(4))[0]

                # Create new tab control after loading the file
                if self.tab_control:
                    self.tab_control.destroy()  # Remove old tabs if any
                self.tab_control = ttk.Notebook(self.root)
                self.tab_control.pack(expand=1, fill="both")

                # Create tabs for each tree based on the offsets we extracted
                tree_offsets = [tree1_offset, tree2_offset, tree3_offset, tree4_offset]
                for i, offset in enumerate(tree_offsets):
                    tree_tab = ttk.Frame(self.tab_control)
                    self.tab_control.add(tree_tab, text=f"Tree {i+1}")
                    self.trees_tabs.append(tree_tab)
                    self.create_tree_tab(tree_tab, i, offset, f)

                # Extract the ADLN section from the AD file
                self.extract_adln_file(file_path, f)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load AD file: {str(e)}")

    def extract_adln_file(self, ad_file_path, ad_file):
        try:
            # ADLN starts at 0x80 of the .ad file
            ad_file.seek(0x80)
            adln_header = ad_file.read(0x80)  # Read the ADLN header (size is 128 bytes)

            # Get the size of the ADLN file from 0xC of the ADLN header
            ad_file.seek(0x80 + 0xC)
            adln_size = struct.unpack('<I', ad_file.read(4))[0]

            # Extract ADLN data based on its size
            ad_file.seek(0x80)
            adln_data = ad_file.read(adln_size)

            # Generate ADLN file path with the same name as the .ad file
            adln_file_path = os.path.splitext(ad_file_path)[0] + ".adln"

            # Write extracted ADLN data to a separate file
            with open(adln_file_path, 'wb') as adln_file:
                adln_file.write(adln_data)

            # Prompt to load the extracted ADLN file
            self.load_adln_file(adln_file_path)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract ADLN data: {str(e)}")

    def load_adln_file(self, adln_file_path):
        try:
            with open(adln_file_path, 'rb') as f:
                # Read the spline count from 0x14 of the ADLN header
                f.seek(0x14)
                spline_count = struct.unpack('<I', f.read(4))[0]

                # Read splines' offsets (starting at 0x30 relative to ADLN header)
                f.seek(0x30)
                spline_offsets = [struct.unpack('<I', f.read(4))[0] for _ in range(spline_count)]

                # Ensure that only 8 spline tabs are created
                for i, offset in enumerate(spline_offsets[:8]):
                    spline_tab = ttk.Frame(self.tab_control)
                    self.tab_control.add(spline_tab, text=f"Spline {i+1}")
                    self.splines_tabs.append(spline_tab)
                    self.create_spline_tab(spline_tab, i, offset, f)

                messagebox.showinfo("File Loaded", f"ADLN File successfully extracted and loaded from {adln_file_path}!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ADLN file: {str(e)}")

    def create_spline_tab(self, tab, spline_index, offset, adln_file):
        # Read the spline node count (first byte at the offset)
        adln_file.seek(offset)
        node_count = struct.unpack('<B', adln_file.read(1))[0]

        if node_count == 0:
            return  # No nodes, so we skip this spline

        # Skip 63 bytes of padding (1 byte for node count + 63 bytes padding)
        adln_file.seek(offset + 1 + 63)

        # Add widgets for node data on the left side
        left_frame = tk.Frame(tab)
        left_frame.pack(side=tk.LEFT, padx=10)

        nodes = []
        arcs = []  # List to hold arc data

        for node_index in range(node_count):
            # Read node data (64 bytes per node)
            node_data = adln_file.read(64)

            # Extract XYZ coordinates (bytes 4 to 16)
            x, y, z = struct.unpack('<fff', node_data[4:16])
            is_corner = struct.unpack('<B', node_data[0:1])[0]  # First byte
            arc_radius = struct.unpack('<f', node_data[25:29])[0]  # Radius (bytes 25-28)

            nodes.append((x, y, z, is_corner, arc_radius))

            # Display node coordinates in left frame
            tk.Label(left_frame, text=f"Node {node_index + 1}: X={x:.2f}, Y={y:.2f}, Z={z:.2f}, Radius={arc_radius:.2f}").pack()

        # Add a canvas for visualization on the right side
        right_frame = tk.Frame(tab)
        right_frame.pack(side=tk.RIGHT, padx=10, expand=True, fill=tk.BOTH)

        canvas = tk.Canvas(right_frame, bg="white")
        canvas.pack(fill=tk.BOTH, expand=True)

        # Draw the nodes on the canvas
        self.visualize_spline(canvas, nodes)

        # Add button to dump nodes to .obj files
        dump_button = tk.Button(tab, text="Dump to .obj", command=lambda: self.dump_to_obj(nodes, spline_index))
        dump_button.pack(pady=10)

    def create_tree_tab(self, tab, tree_index, offset, ad_file):
        # Read 128 bytes of tree data
        ad_file.seek(offset)
        tree_data = ad_file.read(128)

        # Add widgets for tree data visualization
        left_frame = tk.Frame(tab)
        left_frame.pack(side=tk.LEFT, padx=10)

        for i in range(0, len(tree_data), 4):
            hex_values = ' '.join(f"{b:02X}" for b in tree_data[i:i + 4])
            dec_values = ' '.join(f"{b}" for b in tree_data[i:i + 4])
            tk.Label(left_frame, text=f"{hex_values}  ({dec_values})").pack()

    def visualize_spline(self, canvas, nodes):
        # Adjust zoom and pan with default settings
        self.scale = 1.0
        self.pan_x, self.pan_y = 0, 0
        self.offset_x, self.offset_y = 300, 300

        def draw_nodes():
            canvas.delete("all")

            for i in range(len(nodes) - 1):
                x1, y1 = nodes[i][0] * self.scale + self.pan_x + self.offset_x, nodes[i][1] * self.scale + self.pan_y + self.offset_y
                x2, y2 = nodes[i + 1][0] * self.scale + self.pan_x + self.offset_x, nodes[i + 1][1] * self.scale + self.pan_y + self.offset_y
                
                # Draw arcs based on corner data
                if nodes[i][3] == 1:  # Is corner
                    radius = abs(nodes[i][4])
                    start_angle, extent_angle = self.calculate_arc_angles(x1, y1, x2, y2, radius, nodes[i][4] > 0)
                    self.draw_arc(canvas, x1, y1, radius, start_angle, extent_angle)

                canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)

        def zoom(event):
            self.scale = self.scale * 1.1 if event.delta > 0 else self.scale / 1.1
            draw_nodes()

        def pan_start(event):
            canvas.scan_mark(event.x, event.y)

        def pan_move(event):
            canvas.scan_dragto(event.x, event.y, gain=1)
            self.pan_x += (event.x - canvas.canvasx(0)) / self.scale
            self.pan_y += (event.y - canvas.canvasy(0)) / self.scale
            draw_nodes()

        # Bind mouse events for zoom and pan
        canvas.bind("<MouseWheel>", zoom)
        canvas.bind("<ButtonPress-1>", pan_start)
        canvas.bind("<B1-Motion>", pan_move)

        # Initial draw
        draw_nodes()

    def calculate_arc_angles(self, x1, y1, x2, y2, radius, is_left_turn):
        # Calculate angles for the arc
        dx = x2 - x1
        dy = y2 - y1
        distance = math.hypot(dx, dy)
        if distance == 0:
            return 0, 0

        # Determine the center of the arc
        if distance < 2 * radius:
            angle = math.degrees(math.acos(distance / (2 * radius)))
            if is_left_turn:
                start_angle = math.degrees(math.atan2(dy, dx)) - angle
                extent_angle = 2 * angle
            else:
                start_angle = math.degrees(math.atan2(dy, dx)) + angle
                extent_angle = -2 * angle
        else:
            # If the distance is too large, just draw a line
            start_angle = 0
            extent_angle = 0

        return start_angle, extent_angle

    def draw_arc(self, canvas, x1, y1, radius, start_angle, extent_angle):
        # Draw an arc on the canvas
        if extent_angle == 0:
            return

        bounding_box = [
            x1 - radius, y1 - radius, 
            x1 + radius, y1 + radius
        ]

        canvas.create_arc(bounding_box, start=start_angle, extent=extent_angle, style=tk.ARC, outline="red", width=2)

    def dump_to_obj(self, nodes, spline_index):
        # Directory for saving .obj files
        save_dir = filedialog.askdirectory(title="Select Directory to Save .obj Files")
        if not save_dir:
            return

        try:
            for node_index, (x, y, z, is_corner, arc_radius) in enumerate(nodes):
                # Create .obj file content
                obj_content = f"v {x:.2f} {-z:.2f} {-y:.2f}\n"

                # Write to .obj file
                obj_filename = os.path.join(save_dir, f"spline_{spline_index + 1}_node_{node_index + 1}.obj")
                with open(obj_filename, 'w') as obj_file:
                    obj_file.write(obj_content)

            messagebox.showinfo("Success", f"Nodes successfully dumped to .obj files in {save_dir}!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to dump nodes to .obj files: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ADFileProcessor(root)
    root.mainloop()

