"""
📊 Advanced Analytics Dashboard
Afișează KPI-uri și metrici într-o schemă vizuală avansată
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime, timedelta
import math
import random

class AnalyticsDashboard:
    def __init__(self, parent, production_metrics, production_lines_df, orders_df, schedule_df):
        self.parent = parent
        self.production_metrics = production_metrics
        self.production_lines_df = production_lines_df
        self.orders_df = orders_df
        self.schedule_df = schedule_df

        # Creează fereastra principală
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Advanced Analytics Dashboard")
        self.window.geometry("1400x900")
        self.window.configure(bg='#1a1a2e')
        self.window.transient(parent)

        # Variables pentru actualizare în timp real
        self.auto_refresh = tk.BooleanVar(value=True)
        self.refresh_interval = 5000  # 5 secunde

        print("📊 Analytics Dashboard initializing...")
        self.create_dashboard()
        self.start_auto_refresh()

    def create_dashboard(self):
        """Creează dashboard-ul principal"""
        # Header cu titlu și controale
        self.create_header()

        # Container principal cu tab-uri
        self.create_main_container()

        # Status bar
        self.create_status_bar()

    def create_header(self):
        """Creează header-ul dashboard-ului"""
        header_frame = tk.Frame(self.window, bg='#16213e', height=100)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)

        # Titlu principal
        title_label = tk.Label(header_frame,
                              text="📊 Advanced Analytics Dashboard",
                              font=('Segoe UI', 18, 'bold'),
                              fg='#00d4aa', bg='#16213e')
        title_label.pack(side=tk.LEFT, pady=30, padx=20)

        # Controale din dreapta
        controls_frame = tk.Frame(header_frame, bg='#16213e')
        controls_frame.pack(side=tk.RIGHT, pady=20, padx=20)

        # Auto-refresh toggle
        tk.Checkbutton(controls_frame, text="🔄 Auto Refresh",
                      variable=self.auto_refresh,
                      font=('Segoe UI', 10),
                      fg='#ffffff', bg='#16213e',
                      selectcolor='#00d4aa').pack(side=tk.LEFT, padx=10)

        # Manual refresh button
        tk.Button(controls_frame, text="🔄 Refresh Now",
                 command=self.manual_refresh,
                 font=('Segoe UI', 10), bg='#0078ff', fg='white',
                 relief='flat', padx=15, pady=5).pack(side=tk.LEFT, padx=5)

        # Export button
        tk.Button(controls_frame, text="📊 Export Data",
                 command=self.export_analytics_data,
                 font=('Segoe UI', 10), bg='#ff6b35', fg='white',
                 relief='flat', padx=15, pady=5).pack(side=tk.LEFT, padx=5)

    def create_main_container(self):
        """Creează containerul principal cu tab-uri"""
        main_frame = tk.Frame(self.window, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        # Notebook pentru tab-uri
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: KPI Overview
        self.create_kpi_overview_tab()

        # Tab 2: Performance Trends
        self.create_performance_trends_tab()

        # Tab 3: Line Analysis
        self.create_line_analysis_tab()

        # Tab 4: Order Analytics
        self.create_order_analytics_tab()

    def create_kpi_overview_tab(self):
        """Creează tab-ul cu overview-ul KPI-urilor"""
        kpi_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(kpi_frame, text="📈 KPI Overview")

        # Canvas pentru scroll
        canvas = tk.Canvas(kpi_frame, bg='#1a1a2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(kpi_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a2e')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. KPI Cards Grid
        self.create_kpi_cards_grid(scrollable_frame)

        # 2. KPI Comparison Chart
        self.create_kpi_comparison_chart(scrollable_frame)

        # 3. Performance Gauges
        self.create_performance_gauges(scrollable_frame)

        self.kpi_scrollable_frame = scrollable_frame

    def create_kpi_cards_grid(self, parent):
        """Creează grid-ul cu carduri KPI"""
        kpi_section = tk.LabelFrame(parent, text="📊 Key Performance Indicators",
                                   bg='#16213e', fg='#00d4aa',
                                   font=('Segoe UI', 14, 'bold'))
        kpi_section.pack(fill=tk.X, padx=20, pady=20)

        # Grid container
        grid_frame = tk.Frame(kpi_section, bg='#16213e')
        grid_frame.pack(fill=tk.X, padx=20, pady=20)

        # Calculează KPI-urile
        kpis = self.calculate_advanced_kpis()

        # Definește cardurile KPI
        kpi_cards = [
            ("📊 Overall Efficiency", f"{kpis['efficiency']:.1f}%", self.get_efficiency_color(kpis['efficiency']), "Production efficiency across all lines"),
            ("⏰ On-Time Delivery", f"{kpis['on_time_delivery']:.1f}%", self.get_delivery_color(kpis['on_time_delivery']), "Orders delivered on schedule"),
            ("🏭 Line Utilization", f"{kpis['line_utilization']:.1f}%", self.get_utilization_color(kpis['line_utilization']), "Average line capacity usage"),
            ("📦 Daily Throughput", f"{kpis['throughput']:,.0f}", "#ffa502", "Units produced per day"),
            ("💰 Production Cost/Unit", f"${kpis['cost_per_unit']:.2f}", "#e74c3c", "Average cost per unit"),
            ("⚡ Energy Efficiency", f"{kpis['energy_efficiency']:.1f}%", "#2ecc71", "Energy usage optimization"),
            ("🎯 Quality Rate", f"{kpis['quality_rate']:.1f}%", "#9b59b6", "First-pass quality rate"),
            ("📈 OEE Score", f"{kpis['oee_score']:.1f}%", "#f39c12", "Overall Equipment Effectiveness")
        ]

        # Creează cardurile în grid 4x2
        for i, (title, value, color, description) in enumerate(kpi_cards):
            row = i // 4
            col = i % 4

            card_frame = tk.Frame(grid_frame, bg=color, relief='raised', bd=3)
            card_frame.grid(row=row, column=col, sticky='ew', padx=10, pady=10)
            grid_frame.columnconfigure(col, weight=1)

            # Card content
            tk.Label(card_frame, text=title,
                    font=('Segoe UI', 11, 'bold'),
                    fg='white', bg=color).pack(pady=(15, 5))

            tk.Label(card_frame, text=value,
                    font=('Segoe UI', 20, 'bold'),
                    fg='white', bg=color).pack(pady=(0, 5))

            tk.Label(card_frame, text=description,
                    font=('Segoe UI', 8),
                    fg='white', bg=color,
                    wraplength=150).pack(pady=(0, 15), padx=10)

    def create_kpi_comparison_chart(self, parent):
        """Creează graficul de comparație KPI"""
        chart_section = tk.LabelFrame(parent, text="📈 KPI Performance vs Industry Benchmark",
                                     bg='#16213e', fg='#00d4aa',
                                     font=('Segoe UI', 14, 'bold'))
        chart_section.pack(fill=tk.X, padx=20, pady=20)

        chart_frame = tk.Frame(chart_section, bg='#16213e', height=300)
        chart_frame.pack(fill=tk.X, padx=20, pady=20)
        chart_frame.pack_propagate(False)

        # Simulare grafic cu bare
        kpis = self.calculate_advanced_kpis()
        benchmarks = {
            'Efficiency': (kpis['efficiency'], 85.0),
            'On-Time': (kpis['on_time_delivery'], 90.0),
            'Utilization': (kpis['line_utilization'], 75.0),
            'Quality': (kpis['quality_rate'], 95.0)
        }

        # Header grafic
        tk.Label(chart_frame, text="Current Performance vs Industry Benchmark",
                font=('Segoe UI', 12, 'bold'),
                fg='#ffffff', bg='#16213e').pack(pady=(10, 20))

        # Container pentru bare
        bars_frame = tk.Frame(chart_frame, bg='#16213e')
        bars_frame.pack(fill=tk.X, padx=20)

        for metric, (current, benchmark) in benchmarks.items():
            # Container pentru fiecare metrica
            metric_frame = tk.Frame(bars_frame, bg='#16213e')
            metric_frame.pack(fill=tk.X, pady=10)

            # Label metrica
            tk.Label(metric_frame, text=f"{metric}:",
                    font=('Segoe UI', 10, 'bold'),
                    fg='#ffffff', bg='#16213e').pack(anchor='w')

            # Container bara
            bar_container = tk.Frame(metric_frame, bg='#0f3460', height=30, relief='solid', bd=1)
            bar_container.pack(fill=tk.X, pady=(5, 0))
            bar_container.pack_propagate(False)

            # Bara curentă
            current_width = int((current / 100) * 300)
            current_color = '#00d4aa' if current >= benchmark else '#ff6b35'
            current_bar = tk.Frame(bar_container, bg=current_color, height=28)
            current_bar.place(x=1, y=1, width=current_width)

            # Linia benchmark
            benchmark_x = int((benchmark / 100) * 300)
            benchmark_line = tk.Frame(bar_container, bg='#ffffff', width=3, height=28)
            benchmark_line.place(x=benchmark_x, y=1)

            # Valori text
            tk.Label(bar_container, text=f"Current: {current:.1f}% | Benchmark: {benchmark:.1f}%",
                    font=('Segoe UI', 9),
                    fg='white', bg='#0f3460').place(relx=0.5, rely=0.5, anchor='center')

    def create_performance_gauges(self, parent):
        """Creează gauge-urile de performanță"""
        gauges_section = tk.LabelFrame(parent, text="⚡ Performance Gauges",
                                      bg='#16213e', fg='#00d4aa',
                                      font=('Segoe UI', 14, 'bold'))
        gauges_section.pack(fill=tk.X, padx=20, pady=20)

        gauges_frame = tk.Frame(gauges_section, bg='#16213e')
        gauges_frame.pack(fill=tk.X, padx=20, pady=20)

        # Simulare gauge-uri cu progress circles
        kpis = self.calculate_advanced_kpis()
        gauge_data = [
            ("Overall Health", kpis['overall_health'], "#00d4aa"),
            ("Efficiency Index", kpis['efficiency'], "#0078ff"),
            ("Delivery Performance", kpis['on_time_delivery'], "#2ecc71"),
            ("Resource Utilization", kpis['line_utilization'], "#f39c12")
        ]

        for i, (title, value, color) in enumerate(gauge_data):
            gauge_frame = tk.Frame(gauges_frame, bg='#0f3460', relief='raised', bd=2)
            gauge_frame.grid(row=0, column=i, sticky='ew', padx=10)
            gauges_frame.columnconfigure(i, weight=1)

            # Simulare gauge cu canvas circular
            canvas = tk.Canvas(gauge_frame, width=150, height=150, bg='#0f3460', highlightthickness=0)
            canvas.pack(pady=20)

            # Desenează gauge
            self.draw_gauge(canvas, value, color, 75, 75, 60)

            # Label
            tk.Label(gauge_frame, text=title,
                    font=('Segoe UI', 10, 'bold'),
                    fg='white', bg='#0f3460').pack(pady=(0, 20))

    def draw_gauge(self, canvas, value, color, x, y, radius):
        """Desenează un gauge circular"""
        # Cerc exterior
        canvas.create_oval(x-radius, y-radius, x+radius, y+radius,
                          outline='#1a1a2e', width=8)

        # Arc pentru valoare
        extent = int((value / 100) * 270)  # 270 grade maxim
        canvas.create_arc(x-radius+4, y-radius+4, x+radius-4, y+radius-4,
                         start=135, extent=extent, outline=color, width=6, style='arc')

        # Text valoare
        canvas.create_text(x, y, text=f"{value:.1f}%",
                          font=('Segoe UI', 12, 'bold'), fill='white')

    def create_performance_trends_tab(self):
        """Creează tab-ul cu trenduri de performanță - UPDATED with real charts"""
        trends_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(trends_frame, text="📈 Performance Trends")

        # Header cu controale
        header_frame = tk.Frame(trends_frame, bg='#16213e', height=60)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="📈 Performance Trends Analysis",
                font=('Segoe UI', 14, 'bold'),
                fg='#00d4aa', bg='#16213e').pack(side=tk.LEFT, pady=20, padx=20)

        # Controale pentru charts
        controls_frame = tk.Frame(header_frame, bg='#16213e')
        controls_frame.pack(side=tk.RIGHT, pady=15, padx=20)

        # Time range selector
        self.trend_timeframe = tk.StringVar(value="30_days")
        timeframe_combo = ttk.Combobox(controls_frame, textvariable=self.trend_timeframe,
                                      values=["7_days", "30_days", "90_days", "1_year"],
                                      state="readonly", width=10)
        timeframe_combo.pack(side=tk.LEFT, padx=5)
        timeframe_combo.bind("<<ComboboxSelected>>", self.update_trend_charts)

        tk.Button(controls_frame, text="🔄 Update Charts",
                 command=self.update_trend_charts,
                 font=('Segoe UI', 9), bg='#0078ff', fg='white',
                 relief='flat', padx=10, pady=5).pack(side=tk.LEFT, padx=5)

        # Canvas pentru scroll
        canvas = tk.Canvas(trends_frame, bg='#1a1a2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(trends_frame, orient="vertical", command=canvas.yview)
        self.trends_scrollable_frame = tk.Frame(canvas, bg='#1a1a2e')

        self.trends_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.trends_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Generează charts-urile
        self.create_trend_charts()

    def create_trend_charts(self):
        """Creează charts-urile de trend"""
        # Clear existing charts
        for widget in self.trends_scrollable_frame.winfo_children():
            widget.destroy()

        # Chart 1: Efficiency Trend
        self.create_efficiency_trend_chart()

        # Chart 2: Throughput & Quality Chart
        self.create_throughput_quality_chart()

        # Chart 3: Line Utilization Comparison
        self.create_line_utilization_chart()

        # Chart 4: Orders Performance Chart
        self.create_orders_performance_chart()

    def create_efficiency_trend_chart(self):
        """Creează chart-ul de trend pentru eficiență"""
        chart_frame = tk.LabelFrame(self.trends_scrollable_frame,
                                   text="📊 Efficiency Trend (Last 30 Days)",
                                   bg='#16213e', fg='#00d4aa',
                                   font=('Segoe UI', 12, 'bold'))
        chart_frame.pack(fill=tk.X, padx=20, pady=10)

        # Canvas pentru chart
        chart_canvas = tk.Canvas(chart_frame, width=800, height=300, bg='#0f3460', highlightthickness=0)
        chart_canvas.pack(padx=20, pady=20)

        # Generează date pentru ultimele 30 zile
        trend_data = self.generate_efficiency_trend_data()

        # Desenează chart-ul
        self.draw_line_chart(chart_canvas, trend_data,
                            title="Overall Efficiency (%)",
                            color="#00d4aa",
                            y_range=(60, 100))

    def create_throughput_quality_chart(self):
        """Creează chart pentru throughput și calitate"""
        chart_frame = tk.LabelFrame(self.trends_scrollable_frame,
                                   text="📦 Throughput vs Quality Trends",
                                   bg='#16213e', fg='#00d4aa',
                                   font=('Segoe UI', 12, 'bold'))
        chart_frame.pack(fill=tk.X, padx=20, pady=10)

        # Canvas pentru dual chart
        chart_canvas = tk.Canvas(chart_frame, width=800, height=300, bg='#0f3460', highlightthickness=0)
        chart_canvas.pack(padx=20, pady=20)

        # Generează date
        throughput_data = self.generate_throughput_trend_data()
        quality_data = self.generate_quality_trend_data()

        # Desenează dual chart
        self.draw_dual_line_chart(chart_canvas, throughput_data, quality_data,
                                 title1="Daily Throughput", color1="#ffa502",
                                 title2="Quality Rate (%)", color2="#2ecc71")

    def create_line_utilization_chart(self):
        """Creează chart pentru utilizarea liniilor"""
        chart_frame = tk.LabelFrame(self.trends_scrollable_frame,
                                   text="🏭 Production Lines Utilization Comparison",
                                   bg='#16213e', fg='#00d4aa',
                                   font=('Segoe UI', 12, 'bold'))
        chart_frame.pack(fill=tk.X, padx=20, pady=10)

        # Canvas pentru bar chart
        chart_canvas = tk.Canvas(chart_frame, width=800, height=300, bg='#0f3460', highlightthickness=0)
        chart_canvas.pack(padx=20, pady=20)

        # Generează date pentru linii
        lines_data = self.generate_lines_utilization_data()

        # Desenează bar chart
        self.draw_bar_chart(chart_canvas, lines_data,
                           title="Current Line Utilization (%)",
                           colors=["#00d4aa", "#0078ff", "#ff6b35", "#2ecc71", "#9b59b6", "#f39c12"])

    def create_orders_performance_chart(self):
        """Creează chart pentru performanța comenzilor"""
        chart_frame = tk.LabelFrame(self.trends_scrollable_frame,
                                   text="📋 Orders Performance & Delivery Trends",
                                   bg='#16213e', fg='#00d4aa',
                                   font=('Segoe UI', 12, 'bold'))
        chart_frame.pack(fill=tk.X, padx=20, pady=10)

        # Canvas pentru pie + line chart
        chart_canvas = tk.Canvas(chart_frame, width=800, height=300, bg='#0f3460', highlightthickness=0)
        chart_canvas.pack(padx=20, pady=20)

        # Generează date
        orders_status_data = self.generate_orders_status_data()
        delivery_trend_data = self.generate_delivery_trend_data()

        # Desenează combined chart
        self.draw_combined_chart(chart_canvas, orders_status_data, delivery_trend_data)

    def generate_efficiency_trend_data(self):
        """Generează date de trend pentru eficiență"""
        import random
        from datetime import datetime, timedelta

        data = []
        base_efficiency = self.production_metrics.get('avg_efficiency', 0.75) * 100

        for i in range(30):
            date = datetime.now() - timedelta(days=29-i)
            # Simulare trend cu variații realiste
            variation = random.uniform(-5, 8)
            if i > 20:  # Îmbunătățire în ultimele 10 zile
                variation += 2

            efficiency = max(60, min(98, base_efficiency + variation))
            data.append((date, efficiency))

        return data

    def generate_throughput_trend_data(self):
        """Generează date de trend pentru throughput"""
        import random
        from datetime import datetime, timedelta

        data = []
        base_throughput = self.production_metrics.get('throughput', 2000)

        for i in range(30):
            date = datetime.now() - timedelta(days=29-i)
            variation = random.uniform(-200, 300)

            # Weekend effect
            if date.weekday() >= 5:
                variation -= 400

            throughput = max(1000, base_throughput + variation)
            data.append((date, throughput))

        return data

    def generate_quality_trend_data(self):
        """Generează date de trend pentru calitate"""
        import random
        from datetime import datetime, timedelta

        data = []
        base_quality = 94.0

        for i in range(30):
            date = datetime.now() - timedelta(days=29-i)
            variation = random.uniform(-3, 4)
            quality = max(85, min(99, base_quality + variation))
            data.append((date, quality))

        return data

    def generate_lines_utilization_data(self):
        """Generează date pentru utilizarea liniilor"""
        if hasattr(self, 'production_lines_df') and not self.production_lines_df.empty:
            data = []
            for _, line in self.production_lines_df.iterrows():
                utilization = random.uniform(45, 85)
                if line['Status'] == 'Maintenance':
                    utilization = random.uniform(0, 30)
                data.append((line['LineName'][:12], utilization))
            return data
        else:
            return [
                ("Line Alpha", 78.5),
                ("Line Beta", 82.3),
                ("Line Gamma", 65.8),
                ("Line Delta", 91.2),
                ("Line Epsilon", 76.9)
            ]

    def generate_orders_status_data(self):
        """Generează date pentru status comenzi"""
        if hasattr(self, 'orders_df') and not self.orders_df.empty:
            total = len(self.orders_df)
            completed = len(self.orders_df[self.orders_df['Progress'] == 100])
            in_progress = len(self.orders_df[(self.orders_df['Progress'] > 0) & (self.orders_df['Progress'] < 100)])
            planned = total - completed - in_progress

            return [
                ("Completed", completed, "#2ecc71"),
                ("In Progress", in_progress, "#ffa502"),
                ("Planned", planned, "#0078ff")
            ]
        else:
            return [
                ("Completed", 5, "#2ecc71"),
                ("In Progress", 2, "#ffa502"),
                ("Planned", 1, "#0078ff")
            ]

    def generate_delivery_trend_data(self):
        """Generează date de trend pentru livrări"""
        import random
        from datetime import datetime, timedelta

        data = []
        base_delivery = self.production_metrics.get('on_time_delivery', 80.0)

        for i in range(15):  # Ultimele 15 zile
            date = datetime.now() - timedelta(days=14-i)
            variation = random.uniform(-8, 12)
            delivery_rate = max(70, min(98, base_delivery + variation))
            data.append((date, delivery_rate))

        return data

    def draw_line_chart(self, canvas, data, title, color, y_range=None):
        """Desenează un line chart"""
        if not data:
            return

        width = 800
        height = 300
        margin = 60

        # Background
        canvas.create_rectangle(0, 0, width, height, fill='#0f3460', outline='')

        # Title
        canvas.create_text(width//2, 20, text=title, font=('Segoe UI', 12, 'bold'), fill='white')

        # Calculează range-ul datelor
        values = [item[1] for item in data]
        if y_range:
            min_val, max_val = y_range
        else:
            min_val, max_val = min(values) * 0.9, max(values) * 1.1

        # Desenează axele
        canvas.create_line(margin, height-margin, width-margin, height-margin, fill='#1a1a2e', width=2)  # X axis
        canvas.create_line(margin, margin, margin, height-margin, fill='#1a1a2e', width=2)  # Y axis

        # Grid lines
        for i in range(5):
            y = margin + (height - 2*margin) * i / 4
            canvas.create_line(margin, y, width-margin, y, fill='#1a1a2e', width=1)

            # Y labels
            val = max_val - (max_val - min_val) * i / 4
            canvas.create_text(margin-20, y, text=f"{val:.0f}", font=('Segoe UI', 8), fill='#b0b0b0')

        # Desenează linia
        points = []
        chart_width = width - 2*margin
        chart_height = height - 2*margin

        for i, (date, value) in enumerate(data):
            x = margin + (chart_width * i / (len(data) - 1))
            y = height - margin - ((value - min_val) / (max_val - min_val) * chart_height)
            points.extend([x, y])

        if len(points) >= 4:
            canvas.create_line(points, fill=color, width=3, smooth=True)

            # Dots for data points
            for i in range(0, len(points), 2):
                x, y = points[i], points[i+1]
                canvas.create_oval(x-3, y-3, x+3, y+3, fill=color, outline='white', width=2)

    def draw_dual_line_chart(self, canvas, data1, data2, title1, color1, title2, color2):
        """Desenează un dual line chart"""
        width = 800
        height = 300
        margin = 60

        # Background
        canvas.create_rectangle(0, 0, width, height, fill='#0f3460', outline='')

        # Title
        canvas.create_text(width//2, 20, text=f"{title1} & {title2}", font=('Segoe UI', 12, 'bold'), fill='white')

        # Legend
        canvas.create_rectangle(width-200, 40, width-180, 50, fill=color1, outline='')
        canvas.create_text(width-175, 45, text=title1, font=('Segoe UI', 8), fill='white', anchor='w')
        canvas.create_rectangle(width-200, 55, width-180, 65, fill=color2, outline='')
        canvas.create_text(width-175, 60, text=title2, font=('Segoe UI', 8), fill='white', anchor='w')

        # Desenează primul dataset (left Y axis)
        if data1:
            values1 = [item[1] for item in data1]
            min_val1, max_val1 = min(values1) * 0.9, max(values1) * 1.1

            points1 = []
            chart_width = width - 2*margin
            chart_height = height - 2*margin

            for i, (date, value) in enumerate(data1):
                x = margin + (chart_width * i / (len(data1) - 1))
                y = height - margin - ((value - min_val1) / (max_val1 - min_val1) * chart_height)
                points1.extend([x, y])

            if len(points1) >= 4:
                canvas.create_line(points1, fill=color1, width=3, smooth=True)

        # Desenează al doilea dataset (right Y axis)
        if data2:
            values2 = [item[1] for item in data2]
            min_val2, max_val2 = min(values2) * 0.9, max(values2) * 1.1

            points2 = []

            for i, (date, value) in enumerate(data2):
                x = margin + (chart_width * i / (len(data2) - 1))
                y = height - margin - ((value - min_val2) / (max_val2 - min_val2) * chart_height)
                points2.extend([x, y])

            if len(points2) >= 4:
                canvas.create_line(points2, fill=color2, width=2, smooth=True, dash=(5, 5))

    def draw_bar_chart(self, canvas, data, title, colors):
        """Desenează un bar chart"""
        if not data:
            return

        width = 800
        height = 300
        margin = 60

        # Background
        canvas.create_rectangle(0, 0, width, height, fill='#0f3460', outline='')

        # Title
        canvas.create_text(width//2, 20, text=title, font=('Segoe UI', 12, 'bold'), fill='white')

        # Calculează dimensiunile
        values = [item[1] for item in data]
        max_val = max(values) * 1.1

        chart_width = width - 2*margin
        chart_height = height - 2*margin - 40  # Space for labels
        bar_width = chart_width / len(data) * 0.7

        # Desenează barele
        for i, (label, value) in enumerate(data):
            x = margin + (chart_width * i / len(data)) + (chart_width / len(data) - bar_width) / 2
            bar_height = (value / max_val) * chart_height
            y = height - margin - 30 - bar_height

            color = colors[i % len(colors)]

            # Bara
            canvas.create_rectangle(x, y, x + bar_width, height - margin - 30,
                                   fill=color, outline='white', width=1)

            # Valoarea
            canvas.create_text(x + bar_width/2, y - 10, text=f"{value:.1f}%",
                              font=('Segoe UI', 9, 'bold'), fill='white')

            # Label
            canvas.create_text(x + bar_width/2, height - margin - 15, text=label,
                              font=('Segoe UI', 8), fill='white', anchor='n')

    def draw_combined_chart(self, canvas, pie_data, line_data):
        """Desenează un chart combinat (pie + line)"""
        width = 800
        height = 300

        # Background
        canvas.create_rectangle(0, 0, width, height, fill='#0f3460', outline='')

        # Title
        canvas.create_text(width//2, 20, text="Orders Status & Delivery Performance",
                          font=('Segoe UI', 12, 'bold'), fill='white')

        # Pie chart pentru status (stânga)
        if pie_data:
            pie_x, pie_y, pie_radius = 150, 180, 80
            total = sum(item[1] for item in pie_data)

            start_angle = 0
            for label, value, color in pie_data:
                extent = (value / total) * 360 if total > 0 else 0

                canvas.create_arc(pie_x - pie_radius, pie_y - pie_radius,
                                 pie_x + pie_radius, pie_y + pie_radius,
                                 start=start_angle, extent=extent,
                                 fill=color, outline='white', width=2)

                # Label
                mid_angle = math.radians(start_angle + extent/2)
                label_x = pie_x + (pie_radius + 30) * math.cos(mid_angle)
                label_y = pie_y + (pie_radius + 30) * math.sin(mid_angle)

                canvas.create_text(label_x, label_y, text=f"{label}\n{value}",
                                  font=('Segoe UI', 8, 'bold'), fill='white')

                start_angle += extent

        # Line chart pentru delivery (dreapta)
        if line_data:
            line_margin = 350
            line_width = width - line_margin - 50
            line_height = height - 100

            values = [item[1] for item in line_data]
            min_val, max_val = min(values) * 0.95, max(values) * 1.05

            points = []
            for i, (date, value) in enumerate(line_data):
                x = line_margin + (line_width * i / (len(line_data) - 1))
                y = 50 + line_height - ((value - min_val) / (max_val - min_val) * line_height)
                points.extend([x, y])

            if len(points) >= 4:
                canvas.create_line(points, fill='#00d4aa', width=3, smooth=True)

                # Title pentru line chart
                canvas.create_text(line_margin + line_width//2, 50, text="On-Time Delivery %",
                                  font=('Segoe UI', 10, 'bold'), fill='#00d4aa')

    def update_trend_charts(self, event=None):
        """Actualizează charts-urile când se schimbă timeframe-ul"""
        try:
            print(f"🔄 Updating trend charts for timeframe: {self.trend_timeframe.get()}")
            self.create_trend_charts()
        except Exception as e:
            print(f"❌ Error updating trend charts: {e}")

    # ADAUGĂ aceasta la sfârșitul fișierului analytics_dashboard.py, înlocuind funcția existentă create_performance_trends_tab

    def create_line_analysis_tab(self):
        """Creează tab-ul cu analiza liniilor"""
        lines_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(lines_frame, text="🏭 Line Analysis")

        # Analiză detaliată pe linii
        if hasattr(self, 'production_lines_df') and not self.production_lines_df.empty:
            # Scroll container
            canvas = tk.Canvas(lines_frame, bg='#1a1a2e', highlightthickness=0)
            scrollbar = tk.Scrollbar(lines_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#1a1a2e')

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Analiză pentru fiecare linie
            for _, line in self.production_lines_df.iterrows():
                self.create_line_analysis_card(scrollable_frame, line)
        else:
            tk.Label(lines_frame, text="No production lines data available",
                    font=('Segoe UI', 14), fg='#ffffff', bg='#1a1a2e').pack(expand=True)

    def create_line_analysis_card(self, parent, line_data):
        """Creează card de analiză pentru o linie"""
        card_frame = tk.LabelFrame(parent, text=f"🏭 {line_data['LineName']}",
                                  bg='#16213e', fg='#00d4aa',
                                  font=('Segoe UI', 12, 'bold'))
        card_frame.pack(fill=tk.X, padx=20, pady=10)

        content_frame = tk.Frame(card_frame, bg='#16213e')
        content_frame.pack(fill=tk.X, padx=20, pady=20)

        # Metrici linie
        metrics_text = f"""
📊 Performance Metrics:
• Efficiency: {line_data['Efficiency']*100:.1f}%
• Capacity: {line_data['Capacity_UnitsPerHour']} units/hour
• Operators: {line_data['OperatorCount']}
• Setup Time: {line_data['SetupTime_Minutes']} minutes
• Product Types: {line_data['ProductTypes']}

🔧 Maintenance:
• Status: {line_data['Status']}
• Next Maintenance: {line_data['MaintenanceScheduled']}

📈 Recommendations:
• {self.generate_line_recommendations(line_data)}
        """

        tk.Label(content_frame, text=metrics_text,
                font=('Segoe UI', 10),
                fg='#ffffff', bg='#16213e',
                justify=tk.LEFT).pack(anchor='w')

    def create_order_analytics_tab(self):
        """Creează tab-ul cu analiza comenzilor"""
        orders_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(orders_frame, text="📋 Order Analytics")

        if hasattr(self, 'orders_df') and not self.orders_df.empty:
            # Statistici comenzi
            stats_frame = tk.LabelFrame(orders_frame, text="📊 Order Statistics",
                                       bg='#16213e', fg='#00d4aa',
                                       font=('Segoe UI', 14, 'bold'))
            stats_frame.pack(fill=tk.X, padx=20, pady=20)

            order_stats = self.calculate_order_statistics()

            stats_text = f"""
📋 Order Overview:
• Total Orders: {order_stats['total_orders']}
• Completed: {order_stats['completed']} ({order_stats['completion_rate']:.1f}%)
• In Progress: {order_stats['in_progress']}
• Overdue: {order_stats['overdue']}

⏱️ Timeline Performance:
• Average Lead Time: {order_stats['avg_lead_time']:.1f} days
• On-Time Delivery Rate: {order_stats['on_time_rate']:.1f}%

🎯 Priority Breakdown:
• Critical: {order_stats['critical']} orders
• High: {order_stats['high']} orders
• Medium: {order_stats['medium']} orders
• Low: {order_stats['low']} orders
            """

            tk.Label(stats_frame, text=stats_text,
                    font=('Segoe UI', 11),
                    fg='#ffffff', bg='#16213e',
                    justify=tk.LEFT).pack(anchor='w', padx=20, pady=20)
        else:
            tk.Label(orders_frame, text="No orders data available",
                    font=('Segoe UI', 14), fg='#ffffff', bg='#1a1a2e').pack(expand=True)

    def create_status_bar(self):
        """Creează bara de status"""
        self.status_bar = tk.Frame(self.window, bg='#16213e', height=30)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)

        # Status info
        self.status_text = tk.StringVar(value="📊 Analytics Dashboard Ready")
        tk.Label(self.status_bar, textvariable=self.status_text,
                font=('Segoe UI', 9),
                fg='#e8eaf0', bg='#16213e').pack(side=tk.LEFT, padx=10, pady=5)

        # Last update time
        self.last_update = tk.StringVar(value=f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        tk.Label(self.status_bar, textvariable=self.last_update,
                font=('Segoe UI', 9),
                fg='#00d4aa', bg='#16213e').pack(side=tk.RIGHT, padx=10, pady=5)

    # UTILITY FUNCTIONS

    def calculate_advanced_kpis(self):
        """Calculează KPI-uri avansate"""
        try:
            kpis = {}

            # Base KPIs from production_metrics
            kpis['efficiency'] = self.production_metrics.get('avg_efficiency', 0.75) * 100
            kpis['on_time_delivery'] = self.production_metrics.get('on_time_delivery', 80.0)
            kpis['line_utilization'] = self.production_metrics.get('line_utilization', 60.0)
            kpis['throughput'] = self.production_metrics.get('throughput', 2000)

            # Advanced calculated KPIs
            kpis['cost_per_unit'] = 15.50 + random.uniform(-2, 2)  # Simulat
            kpis['energy_efficiency'] = 78.5 + random.uniform(-5, 5)  # Simulat
            kpis['quality_rate'] = 94.2 + random.uniform(-3, 3)  # Simulat
            kpis['oee_score'] = (kpis['efficiency'] * kpis['line_utilization'] * kpis['quality_rate']) / 10000 * 100
            kpis['overall_health'] = (kpis['efficiency'] + kpis['on_time_delivery'] + kpis['line_utilization']) / 3

            return kpis

        except Exception as e:
            print(f"❌ Error calculating advanced KPIs: {e}")
            return {
                'efficiency': 75, 'on_time_delivery': 80, 'line_utilization': 60,
                'throughput': 2000, 'cost_per_unit': 15.50, 'energy_efficiency': 78.5,
                'quality_rate': 94.2, 'oee_score': 85.0, 'overall_health': 71.7
            }

    def calculate_order_statistics(self):
        """Calculează statistici pentru comenzi"""
        try:
            stats = {}

            stats['total_orders'] = len(self.orders_df)
            stats['completed'] = len(self.orders_df[self.orders_df['Progress'] == 100])
            stats['in_progress'] = len(self.orders_df[(self.orders_df['Progress'] > 0) & (self.orders_df['Progress'] < 100)])
            stats['overdue'] = len(self.orders_df[self.orders_df['DueDate'] < datetime.now()])

            stats['completion_rate'] = (stats['completed'] / stats['total_orders'] * 100) if stats['total_orders'] > 0 else 0
            stats['on_time_rate'] = self.production_metrics.get('on_time_delivery', 80.0)
            stats['avg_lead_time'] = 8.5  # Simulat

            # Priority breakdown
            stats['critical'] = len(self.orders_df[self.orders_df['Priority'] == 'Critical'])
            stats['high'] = len(self.orders_df[self.orders_df['Priority'] == 'High'])
            stats['medium'] = len(self.orders_df[self.orders_df['Priority'] == 'Medium'])
            stats['low'] = len(self.orders_df[self.orders_df['Priority'] == 'Low'])

            return stats

        except Exception as e:
            print(f"❌ Error calculating order statistics: {e}")
            return {
                'total_orders': 0, 'completed': 0, 'in_progress': 0, 'overdue': 0,
                'completion_rate': 0, 'on_time_rate': 80, 'avg_lead_time': 8.5,
                'critical': 0, 'high': 0, 'medium': 0, 'low': 0
            }

    def get_efficiency_color(self, efficiency):
        """Returnează culoarea bazată pe eficiență"""
        if efficiency >= 90: return "#00d4aa"
        elif efficiency >= 80: return "#2ecc71"
        elif efficiency >= 70: return "#f39c12"
        else: return "#e74c3c"

    def get_delivery_color(self, delivery_rate):
        """Returnează culoarea bazată pe rata de livrare"""
        if delivery_rate >= 95: return "#00d4aa"
        elif delivery_rate >= 85: return "#2ecc71"
        elif delivery_rate >= 75: return "#f39c12"
        else: return "#e74c3c"

    def get_utilization_color(self, utilization):
        """Returnează culoarea bazată pe utilizare"""
        if utilization >= 80: return "#00d4aa"
        elif utilization >= 65: return "#2ecc71"
        elif utilization >= 50: return "#f39c12"
        else: return "#e74c3c"

    def generate_line_recommendations(self, line_data):
        """Generează recomandări pentru o linie"""
        recommendations = []

        if line_data['Efficiency'] < 0.8:
            recommendations.append("Consider efficiency optimization")
        if line_data['SetupTime_Minutes'] > 45:
            recommendations.append("Reduce setup time")
        if line_data['Status'] == 'Maintenance':
            recommendations.append("Schedule maintenance completion")

        return " • ".join(recommendations) if recommendations else "Operating optimally"

    def manual_refresh(self):
        """Refresh manual al datelor"""
        try:
            self.status_text.set("🔄 Refreshing analytics data...")

            # Refresh KPI tab
            if hasattr(self, 'kpi_scrollable_frame'):
                for widget in self.kpi_scrollable_frame.winfo_children():
                    widget.destroy()

                self.create_kpi_cards_grid(self.kpi_scrollable_frame)
                self.create_kpi_comparison_chart(self.kpi_scrollable_frame)
                self.create_performance_gauges(self.kpi_scrollable_frame)

            self.last_update.set(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            self.status_text.set("✅ Analytics data refreshed")

        except Exception as e:
            print(f"❌ Error refreshing analytics: {e}")
            self.status_text.set("❌ Refresh failed")

    def start_auto_refresh(self):
        """Începe auto-refresh-ul"""
        def auto_refresh_loop():
            if self.auto_refresh.get():
                self.manual_refresh()

            # Programează următorul refresh
            self.window.after(self.refresh_interval, auto_refresh_loop)

        # Începe loop-ul
        self.window.after(self.refresh_interval, auto_refresh_loop)

    def export_analytics_data(self):
        """Exportă datele analytics"""
        try:
            from tkinter import filedialog

            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Analytics Data"
            )

            if filename:
                kpis = self.calculate_advanced_kpis()

                with open(filename, 'w') as f:
                    f.write("📊 MANUFACTURING ANALYTICS EXPORT\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                    f.write("📈 KEY PERFORMANCE INDICATORS:\n")
                    f.write("-" * 30 + "\n")
                    for key, value in kpis.items():
                        if isinstance(value, float):
                            f.write(f"{key.replace('_', ' ').title()}: {value:.2f}\n")
                        else:
                            f.write(f"{key.replace('_', ' ').title()}: {value}\n")

                    f.write(f"\n📋 PRODUCTION LINES: {len(self.production_lines_df)}\n")
                    f.write(f"📦 ORDERS: {len(self.orders_df)}\n")
                    f.write(f"📅 SCHEDULES: {len(self.schedule_df)}\n")

                messagebox.showinfo("Export Complete", f"Analytics data exported to:\n{filename}")

        except Exception as e:
            print(f"❌ Error exporting analytics: {e}")
            messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")

if __name__ == "__main__":
    # Test standalone
    root = tk.Tk()
    root.withdraw()  # Ascunde fereastra principală

    # Date test
    test_metrics = {
        'avg_efficiency': 0.85,
        'on_time_delivery': 92.0,
        'line_utilization': 72.0,
        'throughput': 2850
    }

    import pandas as pd
    test_lines_df = pd.DataFrame([
        {'LineName': 'Test Line', 'Efficiency': 0.85, 'Capacity_UnitsPerHour': 50,
         'OperatorCount': 3, 'SetupTime_Minutes': 30, 'ProductTypes': 'Electronics',
         'Status': 'Active', 'MaintenanceScheduled': '2025-08-01'}
    ])

    test_orders_df = pd.DataFrame([
        {'OrderID': 'TEST-001', 'Progress': 75, 'Priority': 'High', 'DueDate': datetime.now()}
    ])

    dashboard = AnalyticsDashboard(root, test_metrics, test_lines_df, test_orders_df, pd.DataFrame())
    root.mainloop()