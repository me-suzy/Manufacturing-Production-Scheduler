"""
📊 Gantt View - Professional Production Gantt Chart
Advanced visual scheduling with drag & drop functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime, timedelta
import random
import math

class GanttView:
    def __init__(self, parent, production_lines_df, orders_df, schedule_df):
        self.parent = parent
        self.production_lines_df = production_lines_df
        self.orders_df = orders_df
        self.schedule_df = schedule_df

        # Creează fereastra
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Gantt Chart - Production Schedule")
        self.window.geometry("1400x800")
        self.window.configure(bg='#1a1a2e')
        self.window.transient(parent)

        # Variabile pentru zoom și pan
        self.zoom_level = 1.0
        self.view_start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.view_days = 21  # 3 săptămâni default
        self.pixels_per_day = 120
        self.row_height = 60

        # Drag & drop
        self.drag_data = None
        self.selected_task = None

        # Culori pentru status
        self.status_colors = {
            'Planned': '#3498db',
            'Scheduled': '#0078ff',
            'In Progress': '#f39c12',
            'Completed': '#27ae60',
            'On Hold': '#95a5a6',
            'Critical Delay': '#e74c3c',
            'Queued': '#9b59b6'
        }

        # Culori pentru prioritate
        self.priority_colors = {
            'Critical': '#e74c3c',
            'High': '#f39c12',
            'Medium': '#3498db',
            'Low': '#27ae60'
        }

        print("📊 Gantt View initializing...")
        self.create_interface()

    def create_interface(self):
        """Creează interfața Gantt Chart"""
        # Header cu controale
        self.create_header()

        # Main container
        self.create_main_container()

        # Footer cu informații
        self.create_footer()

        # Populare Gantt
        self.populate_gantt()

    def create_header(self):
        """Creează header-ul cu controale"""
        header_frame = tk.Frame(self.window, bg='#16213e', height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)

        # Titlu
        title_frame = tk.Frame(header_frame, bg='#16213e')
        title_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(title_frame, text="📊 Production Gantt Chart",
                font=('Segoe UI', 16, 'bold'),
                fg='#00d4aa', bg='#16213e').pack(pady=25)

        # Controale zoom și navegare
        controls_frame = tk.Frame(header_frame, bg='#16213e')
        controls_frame.pack(side=tk.RIGHT, pady=15, padx=20)

        # Zoom controls
        zoom_frame = tk.Frame(controls_frame, bg='#16213e')
        zoom_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(zoom_frame, text="🔍 Zoom:",
                font=('Segoe UI', 9, 'bold'),
                fg='#ffffff', bg='#16213e').pack(side=tk.LEFT)

        tk.Button(zoom_frame, text="➖",
                 command=self.zoom_out,
                 font=('Segoe UI', 10), bg='#666666', fg='white',
                 relief='flat', width=3).pack(side=tk.LEFT, padx=2)

        self.zoom_label = tk.Label(zoom_frame, text="100%",
                                  font=('Segoe UI', 9),
                                  fg='#00d4aa', bg='#16213e', width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=2)

        tk.Button(zoom_frame, text="➕",
                 command=self.zoom_in,
                 font=('Segoe UI', 10), bg='#666666', fg='white',
                 relief='flat', width=3).pack(side=tk.LEFT, padx=2)

        # Time navigation
        nav_frame = tk.Frame(controls_frame, bg='#16213e')
        nav_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Button(nav_frame, text="◀◀ Prev Week",
                 command=self.prev_week,
                 font=('Segoe UI', 9), bg='#0078ff', fg='white',
                 relief='flat', padx=10).pack(side=tk.LEFT, padx=2)

        tk.Button(nav_frame, text="📅 Today",
                 command=self.goto_today,
                 font=('Segoe UI', 9), bg='#00d4aa', fg='white',
                 relief='flat', padx=10).pack(side=tk.LEFT, padx=2)

        tk.Button(nav_frame, text="Next Week ▶▶",
                 command=self.next_week,
                 font=('Segoe UI', 9), bg='#0078ff', fg='white',
                 relief='flat', padx=10).pack(side=tk.LEFT, padx=2)

        # View options
        options_frame = tk.Frame(controls_frame, bg='#16213e')
        options_frame.pack(side=tk.LEFT)

        tk.Button(options_frame, text="🔄 Refresh",
                 command=self.refresh_gantt,
                 font=('Segoe UI', 9), bg='#ffa502', fg='white',
                 relief='flat', padx=10).pack(side=tk.LEFT, padx=2)

        tk.Button(options_frame, text="💾 Export",
                 command=self.export_gantt,
                 font=('Segoe UI', 9), bg='#ff6b35', fg='white',
                 relief='flat', padx=10).pack(side=tk.LEFT, padx=2)

    def create_main_container(self):
        """Creează container-ul principal cu scroll - FIXED"""
        main_frame = tk.Frame(self.window, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas principal cu dimensiuni FORȚATE și culoare vizibilă
        self.gantt_canvas = tk.Canvas(main_frame, bg='#2c3e50', highlightthickness=0,
                                     width=1200, height=600)  # DIMENSIUNI EXPLICITE

        # Scrollbars vizibile
        h_scrollbar = tk.Scrollbar(main_frame, orient="horizontal", command=self.gantt_canvas.xview,
                                  bg='#16213e', troughcolor='#1a1a2e', width=20)
        v_scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=self.gantt_canvas.yview,
                                  bg='#16213e', troughcolor='#1a1a2e', width=20)

        self.gantt_canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        # Pack scrollbars și canvas - ORDINEA CORECTĂ
        h_scrollbar.pack(side="bottom", fill="x")
        v_scrollbar.pack(side="right", fill="y")
        self.gantt_canvas.pack(side="left", fill="both", expand=True)

        # Frame pentru conținutul Gantt cu CULOARE VIZIBILĂ
        self.gantt_content = tk.Frame(self.gantt_canvas, bg='#34495e', width=1200)  # CULOARE VIZIBILĂ + WIDTH

        # CREARE WINDOW ÎN CANVAS - CRUCIAL
        self.canvas_window = self.gantt_canvas.create_window(0, 0, window=self.gantt_content, anchor="nw")

        # Bind evenimente - ENHANCED
        def configure_scroll_region(event=None):
            # Actualizează scroll region
            self.gantt_canvas.configure(scrollregion=self.gantt_canvas.bbox("all"))
            # Asigură-te că content-ul se expandează la lățimea canvas-ului
            canvas_width = self.gantt_canvas.winfo_width()
            if canvas_width > 1:
                self.gantt_canvas.itemconfig(self.canvas_window, width=canvas_width)

        self.gantt_content.bind("<Configure>", configure_scroll_region)
        self.gantt_canvas.bind("<Configure>", configure_scroll_region)

        self.gantt_canvas.bind("<Button-1>", self.gantt_click)
        self.gantt_canvas.bind("<B1-Motion>", self.gantt_drag)
        self.gantt_canvas.bind("<ButtonRelease-1>", self.gantt_drop)
        self.gantt_canvas.bind("<MouseWheel>", self.gantt_mousewheel)

    def create_footer(self):
        """Creează footer-ul cu informații"""
        footer_frame = tk.Frame(self.window, bg='#16213e', height=40)
        footer_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        footer_frame.pack_propagate(False)

        # Status info
        self.status_text = tk.StringVar(value="📊 Gantt Chart Ready")
        tk.Label(footer_frame, textvariable=self.status_text,
                font=('Segoe UI', 9),
                fg='#e8eaf0', bg='#16213e').pack(side=tk.LEFT, padx=10, pady=8)

        # Legendă
        legend_frame = tk.Frame(footer_frame, bg='#16213e')
        legend_frame.pack(side=tk.RIGHT, padx=10, pady=8)

        legend_items = [
            ("■ Planned", self.status_colors['Planned']),
            ("■ In Progress", self.status_colors['In Progress']),
            ("■ Completed", self.status_colors['Completed']),
            ("■ Critical", self.status_colors['Critical Delay'])
        ]

        for text, color in legend_items:
            tk.Label(legend_frame, text=text,
                    font=('Segoe UI', 8),
                    fg=color, bg='#16213e').pack(side=tk.LEFT, padx=5)

    def populate_gantt(self):
        """Populează Gantt Chart-ul - FIXED"""
        try:
            print("📊 FIXED Gantt population starting...")

            # Clear content
            for widget in self.gantt_content.winfo_children():
                widget.destroy()

            # FORCE update pentru clear
            self.gantt_content.update_idletasks()

            # TESTEAZĂ mai întâi cu un element simplu VIZIBIL
            print("   Creating test element...")
            test_frame = tk.Frame(self.gantt_content, bg='#e74c3c', height=80, width=1000)  # ROȘU INTENS
            test_frame.pack(fill=tk.X, padx=10, pady=10)
            test_frame.pack_propagate(False)

            test_label = tk.Label(test_frame, text="🔥 GANTT TEST - ELEMENT VIZIBIL",
                                 font=('Segoe UI', 16, 'bold'), fg='white', bg='#e74c3c')
            test_label.pack(expand=True)

            if self.production_lines_df.empty:
                print("❌ No production lines data")
                self.show_no_data_message_visible()
                return

            # Creează header-ul cu timeline CU CULORI VIZIBILE
            print("   Creating timeline header...")
            self.create_timeline_header_visible()

            # Pentru fiecare linie activă, creează rândul Gantt CU CULORI VIZIBILE
            active_lines = self.production_lines_df[self.production_lines_df['Status'] == 'Active']
            print(f"   Creating {len(active_lines)} Gantt rows...")

            for idx, (_, line) in enumerate(active_lines.iterrows()):
                print(f"     Creating Gantt row for {line['LineID']}")
                self.create_gantt_row_visible(line, idx)

            # FORȚEAZĂ actualizarea canvas-ului
            print("   Forcing canvas update...")
            self.gantt_content.update_idletasks()
            self.window.update_idletasks()

            # Update scroll region cu dimensiuni reale
            self.gantt_canvas.update_idletasks()
            bbox = self.gantt_canvas.bbox("all")
            if bbox:
                self.gantt_canvas.configure(scrollregion=bbox)
                print(f"   Canvas bbox: {bbox}")
            else:
                estimated_height = len(active_lines) * 80 + 200
                self.gantt_canvas.configure(scrollregion=(0, 0, 1200, estimated_height))
                print(f"   Fallback scroll region: (0, 0, 1200, {estimated_height})")

            # Asigură-te că content-ul se expandează la lățimea canvas-ului
            canvas_width = self.gantt_canvas.winfo_width()
            if canvas_width > 1:
                self.gantt_canvas.itemconfig(self.canvas_window, width=canvas_width)

            self.status_text.set(f"📊 Gantt Chart showing {len(active_lines)} lines, {self.view_days} days")
            print(f"✅ FIXED Gantt populated - canvas: {self.gantt_canvas.winfo_width()}x{self.gantt_canvas.winfo_height()}")

        except Exception as e:
            print(f"❌ Error populating Gantt: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message_visible(str(e))

    def create_timeline_header_visible(self):
        """Creează header-ul cu timeline - VISIBLE VERSION"""
        header_frame = tk.Frame(self.gantt_content, bg='#9b59b6', height=100, relief='solid', bd=3)
        header_frame.pack(fill=tk.X, pady=(0, 2))
        header_frame.pack_propagate(False)

        # Container pentru layout
        container = tk.Frame(header_frame, bg='#9b59b6')
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Coloana cu "Production Lines" - VIZIBILĂ
        left_section = tk.Frame(container, bg='#8e44ad', width=250, relief='solid', bd=2)
        left_section.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_section.pack_propagate(False)

        tk.Label(left_section, text="🏭 Production\nLines",
                font=('Segoe UI', 12, 'bold'), fg='white', bg='#8e44ad',
                justify=tk.CENTER).pack(expand=True)

        # Secțiunea cu timeline - VIZIBILĂ
        timeline_section = tk.Frame(container, bg='#9b59b6')
        timeline_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Simulare timeline cu zile - VIZIBILE
        days_frame = tk.Frame(timeline_section, bg='#9b59b6')
        days_frame.pack(fill=tk.BOTH, expand=True)

        # Afișează următoarele 14 zile cu CULORI VIZIBILE
        for day_index in range(min(14, self.view_days)):
            current_date = self.view_start_date + timedelta(days=day_index)

            # Frame pentru fiecare zi
            day_color = '#3498db' if current_date.weekday() < 5 else '#95a5a6'  # Albastru/Gri
            if current_date.date() == datetime.now().date():
                day_color = '#e74c3c'  # Roșu pentru astăzi

            day_frame = tk.Frame(days_frame, bg=day_color, width=80, relief='solid', bd=2)
            day_frame.pack(side=tk.LEFT, fill=tk.Y, padx=2)
            day_frame.pack_propagate(False)

            # Ziua săptămânii
            day_name = current_date.strftime('%a')
            tk.Label(day_frame, text=day_name, font=('Segoe UI', 9, 'bold'),
                    fg='white', bg=day_color).pack(pady=(8, 2))

            # Data
            date_str = current_date.strftime('%d/%m')
            tk.Label(day_frame, text=date_str, font=('Segoe UI', 11, 'bold'),
                    fg='white', bg=day_color).pack()

        print("✅ Timeline header created with VISIBLE colors")

    def create_gantt_row_visible(self, line_data, row_index):
        """Creează un rând în Gantt pentru o linie de producție - VISIBLE VERSION"""
        try:
            # Culori distincte pentru fiecare linie
            row_colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
            row_color = row_colors[row_index % len(row_colors)]

            row_frame = tk.Frame(self.gantt_content, bg=row_color, height=self.row_height, relief='solid', bd=3)
            row_frame.pack(fill=tk.X, pady=2)
            row_frame.pack_propagate(False)

            # Container pentru layout
            container = tk.Frame(row_frame, bg=row_color)
            container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Informații linie (partea stângă) - VIZIBILE
            line_info_frame = tk.Frame(container, bg='#2c3e50', width=250, relief='solid', bd=2)
            line_info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
            line_info_frame.pack_propagate(False)

            # Info linie
            info_container = tk.Frame(line_info_frame, bg='#2c3e50')
            info_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

            # Nume linie scurtat
            line_name = line_data['LineName'][:15] + "..." if len(line_data['LineName']) > 15 else line_data['LineName']

            tk.Label(info_container, text=f"🏭 {line_name}",
                    font=('Segoe UI', 10, 'bold'),
                    fg='white', bg='#2c3e50').pack(anchor='w')

            tk.Label(info_container, text=line_data['LineID'],
                    font=('Segoe UI', 9),
                    fg='#ecf0f1', bg='#2c3e50').pack(anchor='w')

            # Status
            status_color = '#00d4aa' if line_data['Status'] == 'Active' else '#ff4757'
            tk.Label(info_container, text=f"● {line_data['Status']}",
                    font=('Segoe UI', 8, 'bold'),
                    fg=status_color, bg='#2c3e50').pack(anchor='w')

            # Zona Gantt (partea dreaptă) - VIZIBILĂ
            gantt_section = tk.Frame(container, bg=row_color)
            gantt_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Simulare task-uri Gantt cu CULORI VIZIBILE
            tasks_container = tk.Frame(gantt_section, bg=row_color)
            tasks_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Afișează task-urile programate pentru această linie
            if not self.schedule_df.empty:
                line_schedules = self.schedule_df[self.schedule_df['LineID'] == line_data['LineID']]

                if not line_schedules.empty:
                    for i, (_, schedule) in enumerate(line_schedules.iterrows()):
                        if i < 3:  # Max 3 task-uri vizibile
                            self.create_gantt_task_visible(tasks_container, schedule, i)
                else:
                    # Slot liber
                    tk.Label(tasks_container, text="Free Slots Available",
                            font=('Segoe UI', 10), fg='white', bg=row_color).pack(expand=True)
            else:
                # Nu sunt programări
                tk.Label(tasks_container, text="No Schedule Data",
                        font=('Segoe UI', 10), fg='white', bg=row_color).pack(expand=True)

            print(f"✅ Gantt row created for {line_data['LineID']} with color {row_color}")

        except Exception as e:
            print(f"❌ Error creating Gantt row: {e}")

    def create_gantt_task_visible(self, parent, schedule_data, task_index):
        """Creează un task vizibil în Gantt"""
        try:
            # Culori pentru task-uri
            task_colors = ['#f39c12', '#e67e22', '#d35400']
            task_color = task_colors[task_index % len(task_colors)]

            # Frame pentru task
            task_frame = tk.Frame(parent, bg=task_color, relief='raised', bd=2)
            task_frame.pack(side=tk.LEFT, fill=tk.Y, padx=2)

            # Găsește order info pentru afișare
            if not self.orders_df.empty:
                order_matches = self.orders_df[self.orders_df['OrderID'] == schedule_data['OrderID']]

                if not order_matches.empty:
                    order_data = order_matches.iloc[0]

                    # Informații task
                    product_name = order_data['ProductName'][:10] + "..." if len(order_data['ProductName']) > 10 else order_data['ProductName']

                    tk.Label(task_frame, text=product_name, font=('Segoe UI', 8, 'bold'),
                            fg='white', bg=task_color).pack(padx=5, pady=2)

                    tk.Label(task_frame, text=f"{order_data['Progress']}%", font=('Segoe UI', 7),
                            fg='white', bg=task_color).pack(padx=5, pady=1)
                else:
                    tk.Label(task_frame, text=schedule_data['OrderID'][:8], font=('Segoe UI', 8, 'bold'),
                            fg='white', bg=task_color).pack(padx=5, pady=2)

            # Bind pentru interacțiuni
            task_frame.bind("<Button-1>", lambda e, s=schedule_data: self.select_gantt_task(e, s))
            task_frame.bind("<Double-Button-1>", lambda e, s=schedule_data: self.edit_gantt_task(e, s))

        except Exception as e:
            print(f"❌ Error creating task: {e}")


    def show_no_data_message_visible(self):
        """Afișează mesaj când nu sunt date - VIZIBIL"""
        message_frame = tk.Frame(self.gantt_content, bg='#e74c3c', height=300, relief='solid', bd=3)
        message_frame.pack(fill=tk.X, padx=20, pady=50)
        message_frame.pack_propagate(False)

        tk.Label(message_frame, text="📊 NO GANTT DATA",
                font=('Segoe UI', 18, 'bold'), fg='white', bg='#e74c3c').pack(expand=True)

    def show_error_message_visible(self, error_text):
        """Afișează mesaj de eroare - VIZIBIL"""
        error_frame = tk.Frame(self.gantt_content, bg='#e74c3c', height=200, relief='solid', bd=3)
        error_frame.pack(fill=tk.X, padx=20, pady=50)
        error_frame.pack_propagate(False)

        tk.Label(error_frame, text="💥 GANTT ERROR", font=('Segoe UI', 16, 'bold'),
                fg='white', bg='#e74c3c').pack(pady=(20, 10))

        tk.Label(error_frame, text=error_text, font=('Segoe UI', 10),
                fg='white', bg='#e74c3c', wraplength=600).pack(pady=(0, 20))

    def create_timeline_header(self):
        """Creează header-ul cu timeline"""
        header_frame = tk.Frame(self.gantt_content, bg='#16213e', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 2))
        header_frame.pack_propagate(False)

        # Coloana cu "Production Lines"
        left_section = tk.Frame(header_frame, bg='#16213e', width=250)
        left_section.pack(side=tk.LEFT, fill=tk.Y)
        left_section.pack_propagate(False)

        tk.Label(left_section, text="🏭 Production Lines",
                font=('Segoe UI', 12, 'bold'),
                fg='#e8eaf0', bg='#16213e').pack(expand=True)

        # Secțiunea cu timeline
        timeline_section = tk.Frame(header_frame, bg='#16213e')
        timeline_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas pentru timeline cu zile
        timeline_canvas = tk.Canvas(timeline_section, bg='#16213e', height=80)
        timeline_canvas.pack(fill=tk.BOTH, expand=True)

        # Desenează axele de timp
        self.draw_timeline_axes(timeline_canvas)

    def draw_timeline_axes(self, canvas):
        """Desenează axele de timp în canvas"""
        canvas.delete("all")

        canvas_width = 1100  # Width estimat
        total_width = self.view_days * self.pixels_per_day * self.zoom_level

        # Background
        canvas.create_rectangle(0, 0, total_width, 80, fill='#16213e', outline='')

        # Linii pentru fiecare zi
        for day in range(self.view_days + 1):
            current_date = self.view_start_date + timedelta(days=day)
            x = day * self.pixels_per_day * self.zoom_level

            # Linie verticală
            canvas.create_line(x, 0, x, 80, fill='#0f3460', width=1)

            if day < self.view_days:
                # Data
                day_text = current_date.strftime('%d')
                month_text = current_date.strftime('%b') if current_date.day == 1 else ""
                weekday_text = current_date.strftime('%a')

                # Text zi
                canvas.create_text(x + (self.pixels_per_day * self.zoom_level) / 2, 15,
                                 text=day_text, fill='#ffffff',
                                 font=('Segoe UI', 10, 'bold'))

                # Text zi săptămână
                canvas.create_text(x + (self.pixels_per_day * self.zoom_level) / 2, 35,
                                 text=weekday_text, fill='#00d4aa',
                                 font=('Segoe UI', 8))

                # Luna (dacă e prima zi)
                if month_text:
                    canvas.create_text(x + (self.pixels_per_day * self.zoom_level) / 2, 55,
                                     text=month_text, fill='#ffa502',
                                     font=('Segoe UI', 8, 'bold'))

                # Weekend highlighting
                if current_date.weekday() >= 5:
                    canvas.create_rectangle(x, 0, x + self.pixels_per_day * self.zoom_level, 80,
                                          fill='#2c3e50', stipple='gray50', outline='')

        # Linia pentru "azi"
        today = datetime.now().date()
        if self.view_start_date.date() <= today <= (self.view_start_date + timedelta(days=self.view_days)).date():
            days_from_start = (today - self.view_start_date.date()).days
            today_x = days_from_start * self.pixels_per_day * self.zoom_level
            canvas.create_line(today_x, 0, today_x, 80, fill='#e74c3c', width=3)

    def create_gantt_row(self, line_data, row_index):
        """Creează un rând în Gantt pentru o linie de producție"""
        row_frame = tk.Frame(self.gantt_content, bg='#16213e', height=self.row_height, relief='solid', bd=1)
        row_frame.pack(fill=tk.X, pady=1)
        row_frame.pack_propagate(False)

        # Informații linie (partea stângă)
        line_info_frame = tk.Frame(row_frame, bg='#0f3460', width=250, relief='solid', bd=1)
        line_info_frame.pack(side=tk.LEFT, fill=tk.Y)
        line_info_frame.pack_propagate(False)

        # Layout info linie
        info_container = tk.Frame(line_info_frame, bg='#0f3460')
        info_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Nume și status
        name_frame = tk.Frame(info_container, bg='#0f3460')
        name_frame.pack(fill=tk.X)

        status_color = '#00d4aa' if line_data['Status'] == 'Active' else '#ff4757'
        line_name = line_data['LineName'][:20] + "..." if len(line_data['LineName']) > 20 else line_data['LineName']

        tk.Label(name_frame, text=f"● {line_name}",
                font=('Segoe UI', 10, 'bold'),
                fg=status_color, bg='#0f3460').pack(anchor='w')

        tk.Label(name_frame, text=line_data['LineID'],
                font=('Segoe UI', 9),
                fg='#b0b0b0', bg='#0f3460').pack(anchor='w')

        # Metrici
        metrics_frame = tk.Frame(info_container, bg='#0f3460')
        metrics_frame.pack(fill=tk.X, pady=(5, 0))

        metrics_text = f"⚡ {line_data['Capacity_UnitsPerHour']}/h | 📊 {line_data['Efficiency']*100:.0f}% | 👥 {line_data['OperatorCount']}"
        tk.Label(metrics_frame, text=metrics_text,
                font=('Segoe UI', 8),
                fg='#ffffff', bg='#0f3460').pack(anchor='w')

        # Zona Gantt (partea dreaptă)
        gantt_section = tk.Frame(row_frame, bg='#1a1a2e')
        gantt_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas pentru task-urile Gantt
        gantt_row_canvas = tk.Canvas(gantt_section, bg='#1a1a2e', height=self.row_height-2)
        gantt_row_canvas.pack(fill=tk.BOTH, expand=True)

        # Desenează task-urile pentru această linie
        self.draw_gantt_tasks(gantt_row_canvas, line_data['LineID'])

    def draw_gantt_tasks(self, canvas, line_id):
        """Desenează task-urile Gantt pentru o linie"""
        canvas.delete("all")

        # Dimensiuni canvas
        canvas_width = 1100
        total_width = self.view_days * self.pixels_per_day * self.zoom_level

        # Background cu linii pentru zile
        for day in range(self.view_days + 1):
            x = day * self.pixels_per_day * self.zoom_level
            canvas.create_line(x, 0, x, self.row_height, fill='#0f3460', width=1)

        # Weekend highlighting
        for day in range(self.view_days):
            current_date = self.view_start_date + timedelta(days=day)
            if current_date.weekday() >= 5:  # Weekend
                x_start = day * self.pixels_per_day * self.zoom_level
                x_end = (day + 1) * self.pixels_per_day * self.zoom_level
                canvas.create_rectangle(x_start, 0, x_end, self.row_height,
                                      fill='#2c3e50', stipple='gray25', outline='')

        # Găsește task-urile programate pentru această linie
        if not self.schedule_df.empty:
            line_schedules = self.schedule_df[self.schedule_df['LineID'] == line_id]

            for _, schedule in line_schedules.iterrows():
                self.draw_single_task(canvas, schedule)

        # Linia pentru "azi"
        today = datetime.now().date()
        if self.view_start_date.date() <= today <= (self.view_start_date + timedelta(days=self.view_days)).date():
            days_from_start = (today - self.view_start_date.date()).days
            today_x = days_from_start * self.pixels_per_day * self.zoom_level
            canvas.create_line(today_x, 0, today_x, self.row_height, fill='#e74c3c', width=2)

    def draw_single_task(self, canvas, schedule_data):
        """Desenează un singur task în Gantt"""
        try:
            # Convertește datele la datetime
            start_date = pd.to_datetime(schedule_data['StartDateTime'])
            end_date = pd.to_datetime(schedule_data['EndDateTime'])

            # Verifică dacă task-ul este în view
            view_end = self.view_start_date + timedelta(days=self.view_days)
            if end_date.date() < self.view_start_date.date() or start_date.date() > view_end.date():
                return

            # Calculează poziția X
            start_days = (start_date.date() - self.view_start_date.date()).days
            duration_days = (end_date - start_date).total_seconds() / (24 * 3600)

            x_start = start_days * self.pixels_per_day * self.zoom_level
            task_width = duration_days * self.pixels_per_day * self.zoom_level

            # Limitează la zona vizibilă
            x_start = max(0, x_start)
            x_end = min(x_start + task_width, self.view_days * self.pixels_per_day * self.zoom_level)
            task_width = x_end - x_start

            if task_width <= 0:
                return

            # Găsește comanda asociată pentru culoare și info
            order_info = self.orders_df[self.orders_df['OrderID'] == schedule_data['OrderID']]

            if not order_info.empty:
                order = order_info.iloc[0]

                # Culoare bazată pe status sau prioritate
                if schedule_data['Status'] in self.status_colors:
                    task_color = self.status_colors[schedule_data['Status']]
                else:
                    task_color = self.priority_colors.get(order['Priority'], '#3498db')

                # Progres
                progress = order['Progress'] / 100.0

                # Desenează task-ul principal
                y_margin = 8
                task_height = self.row_height - 2 * y_margin

                # Background task
                canvas.create_rectangle(x_start, y_margin, x_end, y_margin + task_height,
                                      fill=task_color, outline='#ffffff', width=1)

                # Progress overlay
                if progress > 0:
                    progress_width = task_width * progress
                    canvas.create_rectangle(x_start, y_margin, x_start + progress_width, y_margin + task_height,
                                          fill=self.status_colors['Completed'], outline='', stipple='gray50')

                # Text cu informații
                if task_width > 60:  # Doar dacă task-ul e suficient de lat
                    text_x = x_start + task_width / 2

                    # Nume produs
                    product_name = order['ProductName'][:15] + "..." if len(order['ProductName']) > 15 else order['ProductName']
                    canvas.create_text(text_x, y_margin + task_height/2 - 8,
                                     text=product_name, fill='white',
                                     font=('Segoe UI', 8, 'bold'))

                    # Progres
                    canvas.create_text(text_x, y_margin + task_height/2 + 6,
                                     text=f"{order['Progress']:.0f}%", fill='white',
                                     font=('Segoe UI', 7))

                # Priority indicator
                if order['Priority'] == 'Critical':
                    canvas.create_oval(x_start + 2, y_margin + 2, x_start + 10, y_margin + 10,
                                     fill='#e74c3c', outline='white')

                # Bind pentru interacțiuni
                canvas.tag_bind("current", "<Button-1>",
                              lambda e, s=schedule_data: self.select_gantt_task(e, s))
                canvas.tag_bind("current", "<Double-Button-1>",
                              lambda e, s=schedule_data: self.edit_gantt_task(e, s))

        except Exception as e:
            print(f"❌ Error drawing task: {e}")

    def show_no_data_message(self):
        """Afișează mesaj când nu sunt date"""
        message_frame = tk.Frame(self.gantt_content, bg='#1a1a2e', height=400)
        message_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=100)
        message_frame.pack_propagate(False)

        tk.Label(message_frame, text="📊",
                font=('Segoe UI', 48),
                fg='#666666', bg='#1a1a2e').pack(pady=(50, 20))

        tk.Label(message_frame, text="No Production Data Available",
                font=('Segoe UI', 18, 'bold'),
                fg='#ffffff', bg='#1a1a2e').pack(pady=(0, 10))

        tk.Label(message_frame,
                text="No active production lines or scheduled orders found.\nPlease check your production data.",
                font=('Segoe UI', 12),
                fg='#b0b0b0', bg='#1a1a2e',
                justify=tk.CENTER).pack()

    def show_error_message(self, error_text):
        """Afișează mesaj de eroare"""
        error_frame = tk.Frame(self.gantt_content, bg='#1a1a2e', height=300)
        error_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=100)
        error_frame.pack_propagate(False)

        tk.Label(error_frame, text="⚠️",
                font=('Segoe UI', 48),
                fg='#ff4757', bg='#1a1a2e').pack(pady=(50, 20))

        tk.Label(error_frame, text="Gantt Chart Error",
                font=('Segoe UI', 16, 'bold'),
                fg='#ff4757', bg='#1a1a2e').pack(pady=(0, 10))

        tk.Label(error_frame, text=f"Error: {error_text}",
                font=('Segoe UI', 10),
                fg='#ffffff', bg='#1a1a2e',
                wraplength=600).pack()

    # Funcții pentru controlele de navigare și zoom

    def zoom_in(self):
        """Mărește zoom-ul - FIXED"""
        if self.zoom_level < 3.0:
            self.zoom_level *= 1.25
            self.zoom_label.config(text=f"{int(self.zoom_level*100)}%")
            self.populate_gantt()  # Apelează versiunea fixată

    def zoom_out(self):
        """Micșorează zoom-ul - FIXED"""
        if self.zoom_level > 0.25:
            self.zoom_level /= 1.25
            self.zoom_label.config(text=f"{int(self.zoom_level*100)}%")
            self.populate_gantt()  # Apelează versiunea fixată

    def prev_week(self):
        """Navigare la săptămâna precedentă"""
        self.view_start_date -= timedelta(days=7)
        self.populate_gantt()

    def next_week(self):
        """Navigare la săptămâna următoare"""
        self.view_start_date += timedelta(days=7)
        self.populate_gantt()

    def goto_today(self):
        """Navigare la ziua curentă - FIXED"""
        try:
            print("📅 GOTO TODAY - Gantt fixed version")
            self.view_start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=3)
            self.populate_gantt()  # Apelează versiunea fixată
            self.status_text.set("📅 Gantt navigated to today")
        except Exception as e:
            print(f"❌ Error in goto_today: {e}")

    def refresh_gantt(self):
        """Refresh Gantt Chart - FIXED"""
        try:
            print("🔄 Refreshing Gantt with fixed version...")
            self.populate_gantt()  # Apelează versiunea fixată
            self.status_text.set("🔄 Gantt Chart refreshed")
        except Exception as e:
            print(f"❌ Error refreshing Gantt: {e}")

    def export_gantt(self):
        """Export Gantt Chart"""
        messagebox.showinfo("Export", "Gantt Chart export feature coming soon!")

    # Event handlers

    def update_gantt_scroll(self, event):
        """Actualizează scroll region"""
        self.gantt_canvas.configure(scrollregion=self.gantt_canvas.bbox("all"))

    def gantt_click(self, event):
        """Handle click în Gantt"""
        pass

    def gantt_drag(self, event):
        """Handle drag în Gantt"""
        pass

    def gantt_drop(self, event):
        """Handle drop în Gantt"""
        pass

    def gantt_mousewheel(self, event):
        """Handle mouse wheel pentru scroll orizontal"""
        self.gantt_canvas.xview_scroll(int(-1*(event.delta/120)), "units")

    def select_gantt_task(self, event, schedule_data):
        """Selectează un task din Gantt"""
        self.selected_task = schedule_data
        self.status_text.set(f"Selected: {schedule_data['OrderID']} on {schedule_data['LineID']}")

    def edit_gantt_task(self, event, schedule_data):
        """Editează un task din Gantt"""
        self.show_task_editor(schedule_data)

    def show_task_editor(self, schedule_data):
        """Afișează editorul pentru task"""
        try:
            editor_win = tk.Toplevel(self.window)
            editor_win.title(f"✏️ Edit Task - {schedule_data['OrderID']}")
            editor_win.geometry("500x400")
            editor_win.configure(bg='#1a1a2e')
            editor_win.transient(self.window)
            editor_win.grab_set()

            # Header
            header_frame = tk.Frame(editor_win, bg='#16213e', height=60)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)

            tk.Label(header_frame, text=f"✏️ Edit Task: {schedule_data['OrderID']}",
                    font=('Segoe UI', 14, 'bold'),
                    fg='#00d4aa', bg='#16213e').pack(pady=20)

            # Content
            content_frame = tk.Frame(editor_win, bg='#1a1a2e')
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Găsește order info
            order_info = self.orders_df[self.orders_df['OrderID'] == schedule_data['OrderID']]

            if not order_info.empty:
                order = order_info.iloc[0]

                # Order info
                tk.Label(content_frame, text=f"📦 Product: {order['ProductName']}",
                        font=('Segoe UI', 11, 'bold'),
                        fg='#ffffff', bg='#1a1a2e').pack(anchor='w', pady=5)

                tk.Label(content_frame, text=f"🏢 Customer: {order['CustomerName']}",
                        font=('Segoe UI', 10),
                        fg='#b0b0b0', bg='#1a1a2e').pack(anchor='w', pady=2)

                tk.Label(content_frame, text=f"📊 Quantity: {order['Quantity']} units",
                        font=('Segoe UI', 10),
                        fg='#b0b0b0', bg='#1a1a2e').pack(anchor='w', pady=2)

                # Schedule info
                tk.Label(content_frame, text="📅 Schedule Information:",
                        font=('Segoe UI', 11, 'bold'),
                        fg='#00d4aa', bg='#1a1a2e').pack(anchor='w', pady=(20, 5))

                start_time = pd.to_datetime(schedule_data['StartDateTime'])
                end_time = pd.to_datetime(schedule_data['EndDateTime'])

                tk.Label(content_frame, text=f"🚀 Start: {start_time.strftime('%d/%m/%Y %H:%M')}",
                        font=('Segoe UI', 10),
                        fg='#ffffff', bg='#1a1a2e').pack(anchor='w', pady=2)

                tk.Label(content_frame, text=f"🏁 End: {end_time.strftime('%d/%m/%Y %H:%M')}",
                        font=('Segoe UI', 10),
                        fg='#ffffff', bg='#1a1a2e').pack(anchor='w', pady=2)

                duration = end_time - start_time
                tk.Label(content_frame, text=f"⏱️ Duration: {duration.total_seconds()/3600:.1f} hours",
                        font=('Segoe UI', 10),
                        fg='#ffffff', bg='#1a1a2e').pack(anchor='w', pady=2)

                # Status și progres
                tk.Label(content_frame, text=f"🔄 Status: {schedule_data['Status']}",
                        font=('Segoe UI', 10),
                        fg='#ffa502', bg='#1a1a2e').pack(anchor='w', pady=2)

                tk.Label(content_frame, text=f"📈 Progress: {order['Progress']:.0f}%",
                        font=('Segoe UI', 10),
                        fg='#00d4aa', bg='#1a1a2e').pack(anchor='w', pady=2)

            # Butoane
            buttons_frame = tk.Frame(content_frame, bg='#1a1a2e')
            buttons_frame.pack(fill=tk.X, pady=20)

            tk.Button(buttons_frame, text="📊 View Details",
                     command=lambda: self.view_full_task_details(schedule_data),
                     font=('Segoe UI', 10), bg='#0078ff', fg='white',
                     relief='flat', padx=15, pady=8).pack(side=tk.LEFT, padx=5)

            tk.Button(buttons_frame, text="🔄 Update Progress",
                     command=lambda: self.update_task_progress(schedule_data),
                     font=('Segoe UI', 10), bg='#ff6b35', fg='white',
                     relief='flat', padx=15, pady=8).pack(side=tk.LEFT, padx=5)

            tk.Button(buttons_frame, text="❌ Close",
                     command=editor_win.destroy,
                     font=('Segoe UI', 10), bg='#666666', fg='white',
                     relief='flat', padx=15, pady=8).pack(side=tk.RIGHT, padx=5)

        except Exception as e:
            print(f"❌ Error showing task editor: {e}")

    def view_full_task_details(self, schedule_data):
        """Afișează detaliile complete ale task-ului"""
        messagebox.showinfo("Task Details", f"Full details for {schedule_data['OrderID']} coming soon!")

    def update_task_progress(self, schedule_data):
        """Actualizează progresul task-ului"""
        messagebox.showinfo("Update Progress", f"Progress update for {schedule_data['OrderID']} coming soon!")

if __name__ == "__main__":
    # Test standalone
    import random

    # Date test
    test_lines = pd.DataFrame([
        {'LineID': 'LINE-A01', 'LineName': 'Assembly Line Alpha', 'Status': 'Active',
         'Capacity_UnitsPerHour': 50, 'Efficiency': 0.87, 'OperatorCount': 3},
        {'LineID': 'LINE-B01', 'LineName': 'Machining Line 1', 'Status': 'Active',
         'Capacity_UnitsPerHour': 25, 'Efficiency': 0.78, 'OperatorCount': 2}
    ])

    test_orders = pd.DataFrame([
        {'OrderID': 'ORD-001', 'ProductName': 'Widget Pro X1', 'CustomerName': 'TechCorp',
         'Quantity': 500, 'Priority': 'High', 'Progress': 35, 'Status': 'In Progress'},
        {'OrderID': 'ORD-002', 'ProductName': 'Circuit Board CB-400', 'CustomerName': 'ElectroMax',
         'Quantity': 1200, 'Priority': 'Medium', 'Progress': 60, 'Status': 'In Progress'}
    ])

    test_schedule = pd.DataFrame([
        {'ScheduleID': 'SCH-001', 'OrderID': 'ORD-001', 'LineID': 'LINE-A01',
         'StartDateTime': datetime.now(), 'EndDateTime': datetime.now() + timedelta(hours=8),
         'Status': 'In Progress'},
        {'ScheduleID': 'SCH-002', 'OrderID': 'ORD-002', 'LineID': 'LINE-B01',
         'StartDateTime': datetime.now() + timedelta(days=1), 'EndDateTime': datetime.now() + timedelta(days=2),
         'Status': 'Scheduled'}
    ])

    root = tk.Tk()
    root.withdraw()

    gantt = GanttView(root, test_lines, test_orders, test_schedule)
    root.mainloop()