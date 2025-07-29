"""
📊 Orders Analytics
Comprehensive analytics dashboard for production orders
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime, timedelta
import math
import random

class OrdersAnalytics:
    def __init__(self, parent, orders_df, production_lines_df, schedule_df, production_metrics):
        self.parent = parent
        self.orders_df = orders_df
        self.production_lines_df = production_lines_df
        self.schedule_df = schedule_df
        self.production_metrics = production_metrics

        # Creează fereastra
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Orders Analytics Dashboard")
        self.window.geometry("1300x800")
        self.window.configure(bg='#1a1a2e')
        self.window.transient(parent)

        # Variables pentru configurări
        self.auto_refresh = tk.BooleanVar(value=True)
        self.analysis_period = tk.StringVar(value="30_days")

        # INIȚIALIZARE EXPLICITĂ A VARIABILELOR STATUS
        self.status_text = tk.StringVar(value="📊 Orders Analytics Ready")
        self.last_update = tk.StringVar(value=f"Updated: {datetime.now().strftime('%H:%M:%S')}")

        print("📊 Orders Analytics initializing...")
        self.create_interface()
        # START AUTO-REFRESH DUPĂ INIȚIALIZARE COMPLETĂ
        self.window.after(1000, self.start_auto_refresh)

    def create_interface(self):
        """Creează interfața analytics"""
        # Header
        self.create_header()

        # Main content cu tabs
        self.create_main_content()

        # Status bar
        self.create_status_bar()

    def create_header(self):
        """Creează header-ul"""
        header_frame = tk.Frame(self.window, bg='#16213e', height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)

        # Titlu
        tk.Label(header_frame,
                text="📊 Orders Analytics Dashboard",
                font=('Segoe UI', 16, 'bold'),
                fg='#00d4aa', bg='#16213e').pack(side=tk.LEFT, pady=25, padx=20)

        # Controale
        controls_frame = tk.Frame(header_frame, bg='#16213e')
        controls_frame.pack(side=tk.RIGHT, pady=20, padx=20)

        # Period selector
        tk.Label(controls_frame, text="Analysis Period:",
                font=('Segoe UI', 9), fg='#ffffff', bg='#16213e').pack(side=tk.LEFT, padx=(0, 5))

        period_combo = ttk.Combobox(controls_frame, textvariable=self.analysis_period,
                                  values=["7_days", "30_days", "90_days", "1_year", "all_time"],
                                  state="readonly", width=10)
        period_combo.pack(side=tk.LEFT, padx=5)
        period_combo.bind("<<ComboboxSelected>>", self.refresh_analytics)

        # Auto refresh
        tk.Checkbutton(controls_frame, text="🔄 Auto",
                      variable=self.auto_refresh,
                      font=('Segoe UI', 9),
                      fg='#ffffff', bg='#16213e',
                      selectcolor='#00d4aa').pack(side=tk.LEFT, padx=10)

        # Export button
        tk.Button(controls_frame, text="📊 Export",
                 command=self.export_analytics,
                 font=('Segoe UI', 9), bg='#ff6b35', fg='white',
                 relief='flat', padx=10, pady=5).pack(side=tk.LEFT, padx=5)

    def create_main_content(self):
        """Creează conținutul principal cu tabs"""
        main_frame = tk.Frame(self.window, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Notebook pentru tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Overview
        self.create_overview_tab()

        # Tab 2: Performance Analysis
        self.create_performance_tab()

        # Tab 3: Customer Analysis
        self.create_customer_tab()

        # Tab 4: Timeline Analysis
        self.create_timeline_tab()

        # Tab 5: Recommendations
        self.create_recommendations_tab()

    def create_overview_tab(self):
        """Creează tab-ul de overview"""
        overview_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(overview_frame, text="📈 Overview")

        # Canvas pentru scroll
        canvas = tk.Canvas(overview_frame, bg='#1a1a2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(overview_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a2e')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. Summary Cards
        self.create_summary_cards(scrollable_frame)

        # 2. Status Distribution Chart
        self.create_status_distribution_chart(scrollable_frame)

        # 3. Priority Breakdown Chart
        self.create_priority_breakdown_chart(scrollable_frame)

        # 4. Progress Overview Chart
        self.create_progress_overview_chart(scrollable_frame)

        self.overview_scrollable_frame = scrollable_frame

    def create_summary_cards(self, parent):
        """Creează cardurile de sumar"""
        summary_frame = tk.LabelFrame(parent, text="📊 Orders Summary",
                                    bg='#16213e', fg='#00d4aa',
                                    font=('Segoe UI', 12, 'bold'))
        summary_frame.pack(fill=tk.X, padx=20, pady=20)

        cards_frame = tk.Frame(summary_frame, bg='#16213e')
        cards_frame.pack(fill=tk.X, padx=20, pady=20)

        # Calculează statistici
        stats = self.calculate_order_statistics()

        # Cards data
        cards_data = [
            ("📋 Total Orders", str(stats['total_orders']), "#0078ff", "All orders in system"),
            ("✅ Completed", f"{stats['completed']} ({stats['completion_rate']:.1f}%)", "#2ecc71", "Successfully completed"),
            ("🔄 In Progress", str(stats['in_progress']), "#ffa502", "Currently being processed"),
            ("⏰ Overdue", str(stats['overdue']), "#ff4757", "Past due date"),
            ("🚨 Critical", str(stats['critical']), "#ff4757", "High priority orders"),
            ("📈 Avg Progress", f"{stats['avg_progress']:.1f}%", "#9b59b6", "Average completion"),
            ("💰 Total Value", f"${stats['total_value']:,.0f}", "#f39c12", "Estimated order value"),
            ("⚡ Efficiency", f"{stats['efficiency']:.1f}%", "#00d4aa", "Overall performance")
        ]

        # Creează cardurile în grid 4x2
        for i, (title, value, color, description) in enumerate(cards_data):
            row = i // 4
            col = i % 4

            card_frame = tk.Frame(cards_frame, bg=color, relief='raised', bd=2)
            card_frame.grid(row=row, column=col, sticky='ew', padx=5, pady=5)
            cards_frame.columnconfigure(col, weight=1)

            tk.Label(card_frame, text=title,
                    font=('Segoe UI', 9, 'bold'),
                    fg='white', bg=color).pack(pady=(10, 2))

            tk.Label(card_frame, text=value,
                    font=('Segoe UI', 14, 'bold'),
                    fg='white', bg=color).pack(pady=(0, 2))

            tk.Label(card_frame, text=description,
                    font=('Segoe UI', 7),
                    fg='white', bg=color,
                    wraplength=120).pack(pady=(0, 10), padx=5)

    def create_status_distribution_chart(self, parent):
        """Creează chart-ul de distribuție status"""
        chart_frame = tk.LabelFrame(parent, text="📊 Order Status Distribution",
                                  bg='#16213e', fg='#00d4aa',
                                  font=('Segoe UI', 12, 'bold'))
        chart_frame.pack(fill=tk.X, padx=20, pady=20)

        chart_canvas = tk.Canvas(chart_frame, width=600, height=300, bg='#0f3460', highlightthickness=0)
        chart_canvas.pack(pady=20)

        # Generează date pentru pie chart
        status_data = self.get_status_distribution()
        self.draw_pie_chart(chart_canvas, status_data, "Order Status Distribution")

    def create_priority_breakdown_chart(self, parent):
        """Creează chart-ul breakdown prioritate"""
        chart_frame = tk.LabelFrame(parent, text="🎯 Priority Breakdown",
                                  bg='#16213e', fg='#00d4aa',
                                  font=('Segoe UI', 12, 'bold'))
        chart_frame.pack(fill=tk.X, padx=20, pady=20)

        chart_canvas = tk.Canvas(chart_frame, width=600, height=300, bg='#0f3460', highlightthickness=0)
        chart_canvas.pack(pady=20)

        # Generează date pentru bar chart
        priority_data = self.get_priority_breakdown()
        self.draw_horizontal_bar_chart(chart_canvas, priority_data, "Orders by Priority")

    def create_progress_overview_chart(self, parent):
        """Creează chart-ul overview progres"""
        chart_frame = tk.LabelFrame(parent, text="📈 Progress Overview",
                                  bg='#16213e', fg='#00d4aa',
                                  font=('Segoe UI', 12, 'bold'))
        chart_frame.pack(fill=tk.X, padx=20, pady=20)

        chart_canvas = tk.Canvas(chart_frame, width=600, height=300, bg='#0f3460', highlightthickness=0)
        chart_canvas.pack(pady=20)

        # Generează date pentru histogram
        progress_data = self.get_progress_distribution()
        self.draw_histogram(chart_canvas, progress_data, "Progress Distribution")

    def create_performance_tab(self):
        """Creează tab-ul de performance"""
        performance_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(performance_frame, text="⚡ Performance")

        # Performance metrics și charts
        perf_content = tk.Frame(performance_frame, bg='#1a1a2e')
        perf_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 1. Delivery Performance
        delivery_frame = tk.LabelFrame(perf_content, text="⏰ Delivery Performance",
                                     bg='#16213e', fg='#00d4aa',
                                     font=('Segoe UI', 12, 'bold'))
        delivery_frame.pack(fill=tk.X, pady=(0, 20))

        delivery_stats = self.calculate_delivery_performance()
        delivery_text = f"""
📊 On-Time Delivery Rate: {delivery_stats['on_time_rate']:.1f}%
⏰ Average Lead Time: {delivery_stats['avg_lead_time']:.1f} days
🚨 Overdue Orders: {delivery_stats['overdue_count']} ({delivery_stats['overdue_rate']:.1f}%)
📈 Improvement Trend: {delivery_stats['trend']}
        """

        tk.Label(delivery_frame, text=delivery_text,
                font=('Segoe UI', 10),
                fg='#ffffff', bg='#16213e',
                justify=tk.LEFT).pack(anchor='w', padx=20, pady=20)

        # 2. Efficiency by Product Type
        efficiency_frame = tk.LabelFrame(perf_content, text="🎯 Efficiency by Product Type",
                                       bg='#16213e', fg='#00d4aa',
                                       font=('Segoe UI', 12, 'bold'))
        efficiency_frame.pack(fill=tk.X, pady=(0, 20))

        self.create_product_efficiency_chart(efficiency_frame)

        # 3. Line Performance
        line_frame = tk.LabelFrame(perf_content, text="🏭 Line Performance Analysis",
                                 bg='#16213e', fg='#00d4aa',
                                 font=('Segoe UI', 12, 'bold'))
        line_frame.pack(fill=tk.X)

        self.create_line_performance_analysis(line_frame)

    def create_customer_tab(self):
        """Creează tab-ul de customer analysis"""
        customer_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(customer_frame, text="🏢 Customers")

        # Customer analytics
        customer_content = tk.Frame(customer_frame, bg='#1a1a2e')
        customer_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 1. Top Customers
        top_customers_frame = tk.LabelFrame(customer_content, text="🏆 Top Customers",
                                          bg='#16213e', fg='#00d4aa',
                                          font=('Segoe UI', 12, 'bold'))
        top_customers_frame.pack(fill=tk.X, pady=(0, 20))

        top_customers = self.get_top_customers()
        self.create_top_customers_table(top_customers_frame, top_customers)

        # 2. Customer Performance
        customer_perf_frame = tk.LabelFrame(customer_content, text="📊 Customer Performance",
                                          bg='#16213e', fg='#00d4aa',
                                          font=('Segoe UI', 12, 'bold'))
        customer_perf_frame.pack(fill=tk.BOTH, expand=True)

        self.create_customer_performance_chart(customer_perf_frame)

    def create_timeline_tab(self):
        """Creează tab-ul de timeline analysis"""
        timeline_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(timeline_frame, text="📅 Timeline")

        # Timeline content
        timeline_content = tk.Frame(timeline_frame, bg='#1a1a2e')
        timeline_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 1. Orders Over Time
        timeline_chart_frame = tk.LabelFrame(timeline_content, text="📈 Orders Volume Over Time",
                                           bg='#16213e', fg='#00d4aa',
                                           font=('Segoe UI', 12, 'bold'))
        timeline_chart_frame.pack(fill=tk.X, pady=(0, 20))

        self.create_orders_timeline_chart(timeline_chart_frame)

        # 2. Upcoming Deadlines
        deadlines_frame = tk.LabelFrame(timeline_content, text="⏰ Upcoming Deadlines",
                                      bg='#16213e', fg='#00d4aa',
                                      font=('Segoe UI', 12, 'bold'))
        deadlines_frame.pack(fill=tk.BOTH, expand=True)

        self.create_deadlines_timeline(deadlines_frame)

    def create_recommendations_tab(self):
        """Creează tab-ul de recomandări"""
        recommendations_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(recommendations_frame, text="💡 Recommendations")

        # Recommendations content
        rec_content = tk.Frame(recommendations_frame, bg='#1a1a2e')
        rec_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Generate recommendations
        recommendations = self.generate_recommendations()

        for i, (category, recs) in enumerate(recommendations.items()):
            rec_frame = tk.LabelFrame(rec_content, text=f"💡 {category}",
                                    bg='#16213e', fg='#00d4aa',
                                    font=('Segoe UI', 12, 'bold'))
            rec_frame.pack(fill=tk.X, pady=10)

            for rec in recs:
                rec_item = tk.Frame(rec_frame, bg='#0f3460', relief='solid', bd=1)
                rec_item.pack(fill=tk.X, padx=15, pady=5)

                tk.Label(rec_item, text=f"• {rec}",
                        font=('Segoe UI', 10),
                        fg='#ffffff', bg='#0f3460',
                        justify=tk.LEFT).pack(anchor='w', padx=15, pady=10)

    def create_status_bar(self):
        """Creează bara de status"""
        self.status_bar = tk.Frame(self.window, bg='#16213e', height=30)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)

        # Status info
        tk.Label(self.status_bar, textvariable=self.status_text,
                font=('Segoe UI', 9),
                fg='#e8eaf0', bg='#16213e').pack(side=tk.LEFT, padx=10, pady=5)

        # Last update
        tk.Label(self.status_bar, textvariable=self.last_update,
                font=('Segoe UI', 9),
                fg='#00d4aa', bg='#16213e').pack(side=tk.RIGHT, padx=10, pady=5)

    # DATA CALCULATION METHODS

    def calculate_order_statistics(self):
        """Calculează statistici pentru comenzi"""
        try:
            if self.orders_df.empty:
                return {
                    'total_orders': 0, 'completed': 0, 'completion_rate': 0,
                    'in_progress': 0, 'overdue': 0, 'critical': 0,
                    'avg_progress': 0, 'total_value': 0, 'efficiency': 0
                }

            stats = {}

            stats['total_orders'] = len(self.orders_df)
            stats['completed'] = len(self.orders_df[self.orders_df['Progress'] == 100])
            stats['completion_rate'] = (stats['completed'] / stats['total_orders'] * 100) if stats['total_orders'] > 0 else 0
            stats['in_progress'] = len(self.orders_df[(self.orders_df['Progress'] > 0) & (self.orders_df['Progress'] < 100)])
            stats['overdue'] = len(self.orders_df[pd.to_datetime(self.orders_df['DueDate']) < datetime.now()])
            stats['critical'] = len(self.orders_df[self.orders_df['Priority'] == 'Critical'])
            stats['avg_progress'] = self.orders_df['Progress'].mean()

            # Estimate total value (simulated)
            stats['total_value'] = stats['total_orders'] * 15000 + random.uniform(-5000, 10000)

            # Calculate efficiency based on completion rate and on-time delivery
            on_time_orders = len(self.orders_df[
                (self.orders_df['Progress'] == 100) &
                (pd.to_datetime(self.orders_df['DueDate']) >= datetime.now())
            ])
            stats['efficiency'] = (on_time_orders / stats['total_orders'] * 100) if stats['total_orders'] > 0 else 0

            return stats

        except Exception as e:
            print(f"❌ Error calculating order statistics: {e}")
            return {
                'total_orders': 0, 'completed': 0, 'completion_rate': 0,
                'in_progress': 0, 'overdue': 0, 'critical': 0,
                'avg_progress': 0, 'total_value': 0, 'efficiency': 0
            }

    def get_status_distribution(self):
        """Obține distribuția statusurilor"""
        if self.orders_df.empty:
            return []

        status_counts = self.orders_df['Status'].value_counts()
        colors = {
            'Planned': '#0078ff',
            'In Progress': '#ffa502',
            'Completed': '#2ecc71',
            'Critical Delay': '#ff4757',
            'On Hold': '#666666',
            'Queued': '#b0b0b0',
            'Scheduled': '#9b59b6'
        }

        return [(status, count, colors.get(status, '#0078ff')) for status, count in status_counts.items()]

    def get_priority_breakdown(self):
        """Obține breakdown-ul priorităților"""
        if self.orders_df.empty:
            return []

        priority_counts = self.orders_df['Priority'].value_counts()
        colors = {
            'Critical': '#ff4757',
            'High': '#ff6b35',
            'Medium': '#ffa502',
            'Low': '#2ecc71'
        }

        return [(priority, count, colors.get(priority, '#0078ff')) for priority, count in priority_counts.items()]

    def get_progress_distribution(self):
        """Obține distribuția progresului"""
        if self.orders_df.empty:
            return []

        # Grupează progresul în buckets de 10%
        bins = range(0, 101, 10)
        progress_counts = pd.cut(self.orders_df['Progress'], bins=bins, include_lowest=True).value_counts()

        return [(f"{int(interval.left)}-{int(interval.right)}%", count) for interval, count in progress_counts.items()]

    def calculate_delivery_performance(self):
        """Calculează performanța de livrare"""
        try:
            if self.orders_df.empty:
                return {
                    'on_time_rate': 0, 'avg_lead_time': 0,
                    'overdue_count': 0, 'overdue_rate': 0,
                    'trend': 'No data'
                }

            completed_orders = self.orders_df[self.orders_df['Progress'] == 100]
            total_orders = len(self.orders_df)

            if len(completed_orders) > 0:
                on_time_completed = len(completed_orders[pd.to_datetime(completed_orders['DueDate']) >= datetime.now()])
                on_time_rate = (on_time_completed / len(completed_orders)) * 100
            else:
                on_time_rate = 0

            # Calculate average lead time (simulated)
            avg_lead_time = 8.5 + random.uniform(-2, 3)

            overdue_count = len(self.orders_df[pd.to_datetime(self.orders_df['DueDate']) < datetime.now()])
            overdue_rate = (overdue_count / total_orders * 100) if total_orders > 0 else 0

            # Trend analysis (simulated)
            if on_time_rate > 85:
                trend = "Improving ↗️"
            elif on_time_rate > 70:
                trend = "Stable ➡️"
            else:
                trend = "Needs attention ↘️"

            return {
                'on_time_rate': on_time_rate,
                'avg_lead_time': avg_lead_time,
                'overdue_count': overdue_count,
                'overdue_rate': overdue_rate,
                'trend': trend
            }

        except Exception as e:
            print(f"❌ Error calculating delivery performance: {e}")
            return {
                'on_time_rate': 0, 'avg_lead_time': 0,
                'overdue_count': 0, 'overdue_rate': 0,
                'trend': 'Error'
            }

    def get_top_customers(self):
        """Obține top clienții"""
        if self.orders_df.empty:
            return []

        customer_stats = self.orders_df.groupby('CustomerName').agg({
            'OrderID': 'count',
            'Progress': 'mean',
            'Quantity': 'sum'
        }).round(1)

        customer_stats.columns = ['Orders', 'Avg_Progress', 'Total_Quantity']
        customer_stats = customer_stats.sort_values('Orders', ascending=False).head(10)

        return customer_stats.reset_index().to_dict('records')

    def generate_recommendations(self):
        """Generează recomandări"""
        recommendations = {
            "Priority Actions": [],
            "Process Improvements": [],
            "Resource Optimization": [],
            "Quality Enhancements": []
        }

        try:
            stats = self.calculate_order_statistics()

            # Priority Actions
            if stats['overdue'] > 0:
                recommendations["Priority Actions"].append(
                    f"Address {stats['overdue']} overdue orders immediately"
                )

            if stats['critical'] > 0:
                recommendations["Priority Actions"].append(
                    f"Prioritize {stats['critical']} critical orders for expedited processing"
                )

            # Process Improvements
            if stats['completion_rate'] < 80:
                recommendations["Process Improvements"].append(
                    "Improve order completion rate - currently below 80%"
                )

            if stats['avg_progress'] < 60:
                recommendations["Process Improvements"].append(
                    "Review workflow efficiency - average progress is low"
                )

            # Resource Optimization
            if stats['in_progress'] > stats['total_orders'] * 0.6:
                recommendations["Resource Optimization"].append(
                    "High number of orders in progress - consider resource reallocation"
                )

            recommendations["Resource Optimization"].append(
                "Review line assignments for optimal capacity utilization"
            )

            # Quality Enhancements
            recommendations["Quality Enhancements"].append(
                "Implement automated quality checkpoints"
            )

            recommendations["Quality Enhancements"].append(
                "Establish customer feedback loops for continuous improvement"
            )

        except Exception as e:
            print(f"❌ Error generating recommendations: {e}")

        return recommendations

    # CHART DRAWING METHODS

    def draw_pie_chart(self, canvas, data, title):
        """Desenează un pie chart"""
        if not data:
            canvas.create_text(300, 150, text="No data available",
                              font=('Segoe UI', 12), fill='white')
            return

        # Chart setup
        center_x, center_y, radius = 200, 150, 80
        total = sum(item[1] for item in data)

        # Title
        canvas.create_text(300, 30, text=title, font=('Segoe UI', 12, 'bold'), fill='white')

        start_angle = 0
        for label, value, color in data:
            extent = (value / total) * 360 if total > 0 else 0

            # Draw arc
            canvas.create_arc(center_x - radius, center_y - radius,
                             center_x + radius, center_y + radius,
                             start=start_angle, extent=extent,
                             fill=color, outline='white', width=2)

            # Label
            mid_angle = math.radians(start_angle + extent/2)
            label_x = center_x + (radius + 40) * math.cos(mid_angle)
            label_y = center_y + (radius + 40) * math.sin(mid_angle)

            canvas.create_text(label_x, label_y, text=f"{label}\n{value}",
                              font=('Segoe UI', 8, 'bold'), fill='white')

            start_angle += extent

    def draw_horizontal_bar_chart(self, canvas, data, title):
        """Desenează un horizontal bar chart"""
        if not data:
            return

        canvas.create_text(300, 30, text=title, font=('Segoe UI', 12, 'bold'), fill='white')

        max_value = max(item[1] for item in data)
        bar_height = 40
        start_y = 70

        for i, (label, value, color) in enumerate(data):
            y = start_y + i * (bar_height + 10)
            bar_width = (value / max_value) * 300

            # Draw bar
            canvas.create_rectangle(150, y, 150 + bar_width, y + bar_height,
                                   fill=color, outline='white', width=1)

            # Label
            canvas.create_text(140, y + bar_height//2, text=label,
                              font=('Segoe UI', 9), fill='white', anchor='e')

            # Value
            canvas.create_text(160 + bar_width, y + bar_height//2, text=str(value),
                              font=('Segoe UI', 9, 'bold'), fill='white', anchor='w')

    def draw_histogram(self, canvas, data, title):
        """Desenează un histogram"""
        if not data:
            return

        canvas.create_text(300, 30, text=title, font=('Segoe UI', 12, 'bold'), fill='white')

        max_value = max(item[1] for item in data)
        bar_width = 50
        start_x = 50
        chart_height = 200

        for i, (label, value) in enumerate(data):
            x = start_x + i * (bar_width + 5)
            bar_height = (value / max_value) * chart_height if max_value > 0 else 0
            y = 250 - bar_height

            # Draw bar
            canvas.create_rectangle(x, y, x + bar_width, 250,
                                   fill='#00d4aa', outline='white', width=1)

            # Value on top
            canvas.create_text(x + bar_width//2, y - 10, text=str(value),
                              font=('Segoe UI', 8, 'bold'), fill='white')

            # Label
            canvas.create_text(x + bar_width//2, 265, text=label,
                              font=('Segoe UI', 7), fill='white', anchor='n')

    def create_product_efficiency_chart(self, parent):
        """Creează chart pentru eficiența pe tip produs"""
        chart_canvas = tk.Canvas(parent, width=600, height=200, bg='#0f3460', highlightthickness=0)
        chart_canvas.pack(pady=20)

        # Simulate efficiency by product type
        if not self.orders_df.empty:
            product_types = self.orders_df['ProductType'].unique()
            efficiency_data = [(ptype, random.uniform(70, 95), '#00d4aa') for ptype in product_types]
        else:
            efficiency_data = [
                ("Electronics", 85.2, '#00d4aa'),
                ("Automotive", 78.9, '#0078ff'),
                ("Medical", 91.5, '#2ecc71')
            ]

        self.draw_horizontal_bar_chart(chart_canvas, efficiency_data, "Efficiency by Product Type (%)")

    def create_line_performance_analysis(self, parent):
        """Creează analiza performanței liniilor"""
        if self.production_lines_df.empty:
            tk.Label(parent, text="No production lines data available",
                    font=('Segoe UI', 12), fg='#ff6b35', bg='#16213e').pack(pady=20)
            return

        # Create a simple performance table
        table_frame = tk.Frame(parent, bg='#16213e')
        table_frame.pack(fill=tk.X, padx=20, pady=20)

        # Headers
        headers = ["Line", "Assigned Orders", "Efficiency", "Status"]
        for i, header in enumerate(headers):
            tk.Label(table_frame, text=header, font=('Segoe UI', 10, 'bold'),
                    fg='#00d4aa', bg='#16213e').grid(row=0, column=i, padx=10, pady=5)

        # Data rows
        for idx, (_, line) in enumerate(self.production_lines_df.head(5).iterrows()):
            assigned_orders = len(self.orders_df[self.orders_df['AssignedLine'] == line['LineID']]) if not self.orders_df.empty else 0

            tk.Label(table_frame, text=line['LineName'][:15],
                    font=('Segoe UI', 9), fg='#ffffff', bg='#16213e').grid(row=idx+1, column=0, padx=10, pady=2)

            tk.Label(table_frame, text=str(assigned_orders),
                    font=('Segoe UI', 9), fg='#ffffff', bg='#16213e').grid(row=idx+1, column=1, padx=10, pady=2)

            tk.Label(table_frame, text=f"{line['Efficiency']*100:.1f}%",
                    font=('Segoe UI', 9), fg='#ffffff', bg='#16213e').grid(row=idx+1, column=2, padx=10, pady=2)

            status_color = '#00d4aa' if line['Status'] == 'Active' else '#ff4757'
            tk.Label(table_frame, text=line['Status'],
                    font=('Segoe UI', 9), fg=status_color, bg='#16213e').grid(row=idx+1, column=3, padx=10, pady=2)

    def create_top_customers_table(self, parent, customers_data):
        """Creează tabelul cu top clienți"""
        if not customers_data:
            tk.Label(parent, text="No customer data available",
                    font=('Segoe UI', 12), fg='#ff6b35', bg='#16213e').pack(pady=20)
            return

        table_frame = tk.Frame(parent, bg='#16213e')
        table_frame.pack(fill=tk.X, padx=20, pady=20)

        # Headers
        headers = ["Customer", "Orders", "Avg Progress", "Total Quantity"]
        for i, header in enumerate(headers):
            tk.Label(table_frame, text=header, font=('Segoe UI', 10, 'bold'),
                    fg='#00d4aa', bg='#16213e').grid(row=0, column=i, padx=10, pady=5)

        # Data rows
        for idx, customer in enumerate(customers_data[:5]):
            tk.Label(table_frame, text=customer['CustomerName'][:20],
                    font=('Segoe UI', 9), fg='#ffffff', bg='#16213e').grid(row=idx+1, column=0, padx=10, pady=2)

            tk.Label(table_frame, text=str(customer['Orders']),
                    font=('Segoe UI', 9), fg='#ffffff', bg='#16213e').grid(row=idx+1, column=1, padx=10, pady=2)

            tk.Label(table_frame, text=f"{customer['Avg_Progress']:.1f}%",
                    font=('Segoe UI', 9), fg='#ffffff', bg='#16213e').grid(row=idx+1, column=2, padx=10, pady=2)

            tk.Label(table_frame, text=f"{customer['Total_Quantity']:,.0f}",
                    font=('Segoe UI', 9), fg='#ffffff', bg='#16213e').grid(row=idx+1, column=3, padx=10, pady=2)

    def create_customer_performance_chart(self, parent):
        """Creează chart pentru performanța clienților"""
        chart_canvas = tk.Canvas(parent, width=600, height=300, bg='#0f3460', highlightthickness=0)
        chart_canvas.pack(pady=20)

        # Placeholder chart - FIXAT NUMELE VARIABILEI
        chart_canvas.create_text(300, 150, text="Customer Performance Chart\n(Implementation with real customer metrics)",
                          font=('Segoe UI', 12), fill='white', justify=tk.CENTER)

    def create_orders_timeline_chart(self, parent):
        """Creează chart timeline pentru comenzi"""
        chart_canvas = tk.Canvas(parent, width=600, height=200, bg='#0f3460', highlightthickness=0)
        chart_canvas.pack(pady=20)

        # Simulate timeline data
        timeline_data = []
        for i in range(30):
            date = datetime.now() - timedelta(days=29-i)
            orders_count = random.randint(0, 5)
            timeline_data.append((date, orders_count))

        # Draw simple line chart
        if timeline_data:
            max_orders = max(item[1] for item in timeline_data)

            # Draw line
            points = []
            for i, (date, count) in enumerate(timeline_data):
                x = 50 + (500 * i / (len(timeline_data) - 1))
                y = 150 - (count / max_orders * 100) if max_orders > 0 else 150
                points.extend([x, y])

            if len(points) >= 4:
                chart_canvas.create_line(points, fill='#00d4aa', width=2, smooth=True)

            chart_canvas.create_text(300, 30, text="Orders Volume (Last 30 Days)",
                                   font=('Segoe UI', 12, 'bold'), fill='white')

    def create_deadlines_timeline(self, parent):
        """Creează timeline pentru deadline-uri"""
        if self.orders_df.empty:
            tk.Label(parent, text="No orders with deadlines",
                    font=('Segoe UI', 12), fg='#ff6b35', bg='#16213e').pack(pady=20)
            return

        deadlines_frame = tk.Frame(parent, bg='#16213e')
        deadlines_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Get upcoming deadlines
        future_orders = self.orders_df[pd.to_datetime(self.orders_df['DueDate']) > datetime.now()]
        upcoming = future_orders.nsmallest(5, 'DueDate') if not future_orders.empty else pd.DataFrame()

        if upcoming.empty:
            tk.Label(deadlines_frame, text="No upcoming deadlines",
                    font=('Segoe UI', 12), fg='#b0b0b0', bg='#16213e').pack(pady=20)
        else:
            for _, order in upcoming.iterrows():
                deadline_item = tk.Frame(deadlines_frame, bg='#0f3460', relief='solid', bd=1)
                deadline_item.pack(fill=tk.X, pady=5)

                due_date = pd.to_datetime(order['DueDate'])
                days_left = (due_date - datetime.now()).days

                color = '#ff4757' if days_left <= 3 else '#ffa502' if days_left <= 7 else '#2ecc71'

                deadline_text = f"📋 {order['OrderID']} - {order['ProductName'][:30]}\n"
                deadline_text += f"📅 Due: {due_date.strftime('%Y-%m-%d')} ({days_left} days left)\n"
                deadline_text += f"📊 Progress: {order['Progress']:.0f}%"

                tk.Label(deadline_item, text=deadline_text,
                        font=('Segoe UI', 9),
                        fg=color, bg='#0f3460',
                        justify=tk.LEFT).pack(anchor='w', padx=15, pady=10)

    def refresh_analytics(self, event=None):
        """Refresh analytics cu perioada selectată"""
        try:
            print(f"🔄 Refreshing analytics for period: {self.analysis_period.get()}")

            # VERIFICĂ DACĂ EXISTĂ COMPONENTE ÎNAINTE DE REFRESH
            if not hasattr(self, 'status_text'):
                print("⚠️ Status components not yet initialized, skipping refresh")
                return

            # Refresh overview tab
            if hasattr(self, 'overview_scrollable_frame'):
                for widget in self.overview_scrollable_frame.winfo_children():
                    widget.destroy()

                self.create_summary_cards(self.overview_scrollable_frame)
                self.create_status_distribution_chart(self.overview_scrollable_frame)
                self.create_priority_breakdown_chart(self.overview_scrollable_frame)
                self.create_progress_overview_chart(self.overview_scrollable_frame)

            if hasattr(self, 'last_update'):
                self.last_update.set(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

            if hasattr(self, 'status_text'):
                self.status_text.set("✅ Analytics refreshed")

        except Exception as e:
            print(f"❌ Error refreshing analytics: {e}")
            if hasattr(self, 'status_text'):
                self.status_text.set("❌ Refresh failed")

    def start_auto_refresh(self):
        """Începe auto-refresh-ul - SAFE VERSION"""
        def auto_refresh_loop():
            try:
                if hasattr(self, 'auto_refresh') and self.auto_refresh.get():
                    self.refresh_analytics()

                # Programează următorul refresh doar dacă fereastra încă există
                if self.window.winfo_exists():
                    self.window.after(30000, auto_refresh_loop)  # 30 seconds
            except tk.TclError:
                # Fereastra a fost închisă
                pass
            except Exception as e:
                print(f"❌ Error in auto-refresh loop: {e}")

        # Start first refresh after a delay
        if self.window.winfo_exists():
            self.window.after(30000, auto_refresh_loop)

    def export_analytics(self):
        """Exportă analytics-urile"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Orders Analytics"
            )

            if filename:
                stats = self.calculate_order_statistics()

                with open(filename, 'w') as f:
                    f.write("📊 ORDERS ANALYTICS EXPORT\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Analysis Period: {self.analysis_period.get()}\n\n")

                    f.write("📈 ORDER STATISTICS:\n")
                    f.write("-" * 30 + "\n")
                    for key, value in stats.items():
                        f.write(f"{key.replace('_', ' ').title()}: {value}\n")

                    f.write(f"\n📋 ORDERS BREAKDOWN:\n")
                    f.write("-" * 30 + "\n")

                    if not self.orders_df.empty:
                        status_dist = self.orders_df['Status'].value_counts()
                        for status, count in status_dist.items():
                            f.write(f"{status}: {count}\n")

                messagebox.showinfo("Export Complete", f"Analytics exported to:\n{filename}")

        except Exception as e:
            print(f"❌ Error exporting analytics: {e}")
            messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")

if __name__ == "__main__":
    # Test standalone
    root = tk.Tk()
    root.withdraw()

    # Test data
    test_orders = pd.DataFrame([
        {'OrderID': 'TEST-001', 'Status': 'In Progress', 'Priority': 'High',
         'CustomerName': 'Test Customer', 'ProductType': 'Electronics',
         'ProductName': 'Test Product', 'Progress': 75, 'Quantity': 100,
         'OrderDate': '2025-07-20', 'DueDate': '2025-08-10', 'AssignedLine': 'LINE-A01'}
    ])

    analytics = OrdersAnalytics(root, test_orders, pd.DataFrame(), pd.DataFrame(), {})
    root.mainloop()