"""
📈 Production Reports Generator
Generează rapoarte complete cu toate KPI-urile și metricile de producție
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime, timedelta
import json
import os

class ReportsGenerator:
    def __init__(self, parent, production_metrics, production_lines_df, orders_df, schedule_df, baseline_metrics, optimization_vars):
        self.parent = parent
        self.production_metrics = production_metrics
        self.production_lines_df = production_lines_df
        self.orders_df = orders_df
        self.schedule_df = schedule_df
        self.baseline_metrics = baseline_metrics
        self.optimization_vars = optimization_vars

        # Creează fereastra principală
        self.window = tk.Toplevel(parent)
        self.window.title("📈 Production Reports Generator")
        self.window.geometry("1200x800")
        self.window.configure(bg='#1a1a2e')
        self.window.transient(parent)

        # Variables pentru configurarea raportului
        self.report_type = tk.StringVar(value="comprehensive")
        self.export_format = tk.StringVar(value="html")
        self.include_charts = tk.BooleanVar(value=True)
        self.include_recommendations = tk.BooleanVar(value=True)

        print("📈 Reports Generator initializing...")
        self.create_interface()

    def create_interface(self):
        """Creează interfața generatorului de rapoarte"""
        # Header
        self.create_header()

        # Main content cu 2 coloane
        self.create_main_content()

        # Footer cu butoane acțiune
        self.create_footer()

    def create_header(self):
        """Creează header-ul"""
        header_frame = tk.Frame(self.window, bg='#16213e', height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)

        # Titlu
        tk.Label(header_frame,
                text="📈 Production Reports Generator",
                font=('Segoe UI', 18, 'bold'),
                fg='#00d4aa', bg='#16213e').pack(side=tk.LEFT, pady=25, padx=20)

        # Data și ora
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tk.Label(header_frame,
                text=f"📅 {current_time}",
                font=('Segoe UI', 11),
                fg='#ffffff', bg='#16213e').pack(side=tk.RIGHT, pady=30, padx=20)

    def create_main_content(self):
        """Creează conținutul principal"""
        main_frame = tk.Frame(self.window, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Coloana stânga - Configurare raport
        left_frame = tk.Frame(main_frame, bg='#1a1a2e', width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        # Coloana dreapta - Preview raport
        right_frame = tk.Frame(main_frame, bg='#1a1a2e')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Populare coloane
        self.create_configuration_panel(left_frame)
        self.create_preview_panel(right_frame)

    def create_configuration_panel(self, parent):
        """Creează panoul de configurare"""
        # Secțiunea tipul raportului
        report_type_frame = tk.LabelFrame(parent, text="📊 Report Type",
                                        bg='#16213e', fg='#00d4aa',
                                        font=('Segoe UI', 12, 'bold'))
        report_type_frame.pack(fill=tk.X, pady=(0, 20))

        report_types = [
            ("comprehensive", "📈 Comprehensive Report", "Complete analysis with all metrics"),
            ("kpi_summary", "🎯 KPI Summary", "Key Performance Indicators only"),
            ("production_lines", "🏭 Production Lines Report", "Focus on line performance"),
            ("orders_analysis", "📋 Orders Analysis", "Order management and timeline"),
            ("optimization", "🚀 Optimization Report", "Optimization results and recommendations")
        ]

        for value, title, description in report_types:
            radio_frame = tk.Frame(report_type_frame, bg='#16213e')
            radio_frame.pack(anchor='w', padx=15, pady=5)

            tk.Radiobutton(radio_frame, text=title,
                          variable=self.report_type, value=value,
                          font=('Segoe UI', 10, 'bold'),
                          fg='#ffffff', bg='#16213e',
                          selectcolor='#0f3460',
                          command=self.update_preview).pack(anchor='w')

            tk.Label(radio_frame, text=description,
                    font=('Segoe UI', 9),
                    fg='#b0b0b0', bg='#16213e').pack(anchor='w', padx=20)

        # Secțiunea opțiuni export
        export_frame = tk.LabelFrame(parent, text="💾 Export Options",
                                   bg='#16213e', fg='#00d4aa',
                                   font=('Segoe UI', 12, 'bold'))
        export_frame.pack(fill=tk.X, pady=(0, 20))

        # Format export
        tk.Label(export_frame, text="📄 Export Format:",
                font=('Segoe UI', 10, 'bold'),
                fg='#ffffff', bg='#16213e').pack(anchor='w', padx=15, pady=(10, 5))

        format_frame = tk.Frame(export_frame, bg='#16213e')
        format_frame.pack(anchor='w', padx=30, pady=(0, 10))

        formats = [("html", "HTML Report"), ("pdf", "PDF Document"), ("excel", "Excel Spreadsheet"), ("json", "JSON Data")]

        for value, text in formats:
            tk.Radiobutton(format_frame, text=text,
                          variable=self.export_format, value=value,
                          font=('Segoe UI', 9),
                          fg='#ffffff', bg='#16213e',
                          selectcolor='#0f3460').pack(anchor='w')

        # Opțiuni suplimentare
        tk.Label(export_frame, text="⚙️ Additional Options:",
                font=('Segoe UI', 10, 'bold'),
                fg='#ffffff', bg='#16213e').pack(anchor='w', padx=15, pady=(10, 5))

        tk.Checkbutton(export_frame, text="📊 Include Charts and Graphs",
                      variable=self.include_charts,
                      font=('Segoe UI', 9),
                      fg='#ffffff', bg='#16213e',
                      selectcolor='#0f3460').pack(anchor='w', padx=30)

        tk.Checkbutton(export_frame, text="💡 Include Recommendations",
                      variable=self.include_recommendations,
                      font=('Segoe UI', 9),
                      fg='#ffffff', bg='#16213e',
                      selectcolor='#0f3460').pack(anchor='w', padx=30, pady=(0, 10))

        # Secțiunea date selection
        data_frame = tk.LabelFrame(parent, text="📅 Data Range",
                                 bg='#16213e', fg='#00d4aa',
                                 font=('Segoe UI', 12, 'bold'))
        data_frame.pack(fill=tk.X, pady=(0, 20))

        # Date range options
        self.date_range = tk.StringVar(value="current")
        date_options = [
            ("current", "📊 Current State"),
            ("last_week", "📅 Last 7 Days"),
            ("last_month", "📆 Last 30 Days"),
            ("custom", "🎯 Custom Range")
        ]

        for value, text in date_options:
            tk.Radiobutton(data_frame, text=text,
                          variable=self.date_range, value=value,
                          font=('Segoe UI', 9),
                          fg='#ffffff', bg='#16213e',
                          selectcolor='#0f3460').pack(anchor='w', padx=15, pady=2)

    def create_preview_panel(self, parent):
        """Creează panoul de preview"""
        preview_frame = tk.LabelFrame(parent, text="👁️ Report Preview",
                                    bg='#16213e', fg='#00d4aa',
                                    font=('Segoe UI', 12, 'bold'))
        preview_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas cu scroll pentru preview
        canvas = tk.Canvas(preview_frame, bg='#0f3460', highlightthickness=0)
        scrollbar = tk.Scrollbar(preview_frame, orient="vertical", command=canvas.yview)
        self.preview_content = tk.Frame(canvas, bg='#0f3460')

        self.preview_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.preview_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Inițializare preview
        self.update_preview()

    def create_footer(self):
        """Creează footer-ul cu butoane"""
        footer_frame = tk.Frame(self.window, bg='#16213e', height=70)
        footer_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        footer_frame.pack_propagate(False)

        # Butoane acțiune
        buttons_frame = tk.Frame(footer_frame, bg='#16213e')
        buttons_frame.pack(expand=True, pady=20)

        tk.Button(buttons_frame, text="👁️ Update Preview",
                 command=self.update_preview,
                 font=('Segoe UI', 11), bg='#0078ff', fg='white',
                 relief='flat', padx=20, pady=8).pack(side=tk.LEFT, padx=10)

        tk.Button(buttons_frame, text="💾 Generate & Save Report",
                 command=self.generate_report,
                 font=('Segoe UI', 11, 'bold'), bg='#00d4aa', fg='white',
                 relief='flat', padx=20, pady=8).pack(side=tk.LEFT, padx=10)

        tk.Button(buttons_frame, text="📧 Email Report",
                 command=self.email_report,
                 font=('Segoe UI', 11), bg='#ff6b35', fg='white',
                 relief='flat', padx=20, pady=8).pack(side=tk.LEFT, padx=10)

        tk.Button(buttons_frame, text="❌ Close",
                 command=self.window.destroy,
                 font=('Segoe UI', 11), bg='#666666', fg='white',
                 relief='flat', padx=20, pady=8).pack(side=tk.LEFT, padx=10)

    def update_preview(self):
        """Actualizează preview-ul raportului"""
        try:
            # Șterge conținutul existent
            for widget in self.preview_content.winfo_children():
                widget.destroy()

            # Generează preview bazat pe tipul selectat
            report_type = self.report_type.get()

            if report_type == "comprehensive":
                self.generate_comprehensive_preview()
            elif report_type == "kpi_summary":
                self.generate_kpi_preview()
            elif report_type == "production_lines":
                self.generate_lines_preview()
            elif report_type == "orders_analysis":
                self.generate_orders_preview()
            elif report_type == "optimization":
                self.generate_optimization_preview()

        except Exception as e:
            print(f"❌ Error updating preview: {e}")
            tk.Label(self.preview_content, text=f"Preview Error: {str(e)}",
                    font=('Segoe UI', 12), fg='#ff4757', bg='#0f3460').pack(pady=20)

    def generate_comprehensive_preview(self):
        """Generează preview pentru raportul comprehensiv"""
        # Header raport
        tk.Label(self.preview_content,
                text="📈 COMPREHENSIVE PRODUCTION REPORT",
                font=('Segoe UI', 16, 'bold'),
                fg='#00d4aa', bg='#0f3460').pack(pady=(20, 10))

        tk.Label(self.preview_content,
                text=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                font=('Segoe UI', 10),
                fg='#ffffff', bg='#0f3460').pack(pady=(0, 20))

        # Executive Summary
        self.add_section_header("📊 EXECUTIVE SUMMARY")

        kpis = self.calculate_report_kpis()
        summary_text = f"""
🎯 Overall Performance: {self.get_performance_rating(kpis['overall_efficiency'])}
📊 Efficiency: {kpis['overall_efficiency']:.1f}%
⏰ On-Time Delivery: {kpis['on_time_delivery']:.1f}%
🏭 Line Utilization: {kpis['line_utilization']:.1f}%
📦 Daily Throughput: {kpis['throughput']:,.0f} units

💡 Key Insights:
• {self.get_top_insight()}
• {self.get_efficiency_insight(kpis['overall_efficiency'])}
• {self.get_delivery_insight(kpis['on_time_delivery'])}
        """

        self.add_section_content(summary_text)

        # KPI Details
        self.add_section_header("📈 KEY PERFORMANCE INDICATORS")
        self.generate_kpi_details()

        # Production Lines
        self.add_section_header("🏭 PRODUCTION LINES ANALYSIS")
        self.generate_lines_analysis()

        # Orders Analysis
        self.add_section_header("📋 ORDERS ANALYSIS")
        self.generate_orders_analysis()

        # Recommendations
        if self.include_recommendations.get():
            self.add_section_header("💡 RECOMMENDATIONS")
            self.generate_recommendations()

    def generate_kpi_preview(self):
        """Generează preview pentru KPI summary"""
        tk.Label(self.preview_content,
                text="🎯 KPI SUMMARY REPORT",
                font=('Segoe UI', 16, 'bold'),
                fg='#00d4aa', bg='#0f3460').pack(pady=(20, 20))

        self.generate_kpi_details()

    def generate_lines_preview(self):
        """Generează preview pentru production lines"""
        tk.Label(self.preview_content,
                text="🏭 PRODUCTION LINES REPORT",
                font=('Segoe UI', 16, 'bold'),
                fg='#00d4aa', bg='#0f3460').pack(pady=(20, 20))

        self.generate_lines_analysis()

    def generate_orders_preview(self):
        """Generează preview pentru orders analysis"""
        tk.Label(self.preview_content,
                text="📋 ORDERS ANALYSIS REPORT",
                font=('Segoe UI', 16, 'bold'),
                fg='#00d4aa', bg='#0f3460').pack(pady=(20, 20))

        self.generate_orders_analysis()

    def generate_optimization_preview(self):
        """Generează preview pentru optimization report"""
        tk.Label(self.preview_content,
                text="🚀 OPTIMIZATION REPORT",
                font=('Segoe UI', 16, 'bold'),
                fg='#00d4aa', bg='#0f3460').pack(pady=(20, 20))

        self.add_section_header("⚙️ OPTIMIZATION SETTINGS")

        opt_text = f"""
🎯 Current Optimization Criteria:
• Minimize Delays: {self.optimization_vars['minimize_delays'].get():.1f}
• Maximize Efficiency: {self.optimization_vars['maximize_efficiency'].get():.1f}
• Balance Workload: {self.optimization_vars['balance_workload'].get():.1f}
• Minimize Setup Time: {self.optimization_vars['minimize_setup'].get():.1f}

📊 Performance vs Baseline:
• Efficiency: {self.production_metrics.get('avg_efficiency', 0.75)*100:.1f}% vs {self.baseline_metrics.get('avg_efficiency', 0.68)*100:.1f}% baseline
• On-Time Delivery: {self.production_metrics.get('on_time_delivery', 80):.1f}% vs {self.baseline_metrics.get('on_time_delivery', 72):.1f}% baseline
• Line Utilization: {self.production_metrics.get('line_utilization', 60):.1f}% vs {self.baseline_metrics.get('line_utilization', 45):.1f}% baseline
        """

        self.add_section_content(opt_text)

        if self.include_recommendations.get():
            self.add_section_header("🎯 OPTIMIZATION RECOMMENDATIONS")
            self.generate_optimization_recommendations()

    def generate_kpi_details(self):
        """Generează detaliile KPI-urilor"""
        kpis = self.calculate_report_kpis()

        # KPI Grid
        kpi_frame = tk.Frame(self.preview_content, bg='#0f3460')
        kpi_frame.pack(fill=tk.X, padx=20, pady=10)

        kpi_data = [
            ("📊 Overall Efficiency", f"{kpis['overall_efficiency']:.1f}%", self.get_efficiency_color(kpis['overall_efficiency'])),
            ("⏰ On-Time Delivery", f"{kpis['on_time_delivery']:.1f}%", self.get_delivery_color(kpis['on_time_delivery'])),
            ("🏭 Line Utilization", f"{kpis['line_utilization']:.1f}%", self.get_utilization_color(kpis['line_utilization'])),
            ("📦 Daily Throughput", f"{kpis['throughput']:,.0f}", "#ffa502")
        ]

        for i, (label, value, color) in enumerate(kpi_data):
            row = i // 2
            col = i % 2

            kpi_card = tk.Frame(kpi_frame, bg=color, relief='raised', bd=2)
            kpi_card.grid(row=row, column=col, sticky='ew', padx=5, pady=5)
            kpi_frame.columnconfigure(col, weight=1)

            tk.Label(kpi_card, text=label,
                    font=('Segoe UI', 10, 'bold'),
                    fg='white', bg=color).pack(pady=(10, 5))

            tk.Label(kpi_card, text=value,
                    font=('Segoe UI', 14, 'bold'),
                    fg='white', bg=color).pack(pady=(0, 10))

    def generate_lines_analysis(self):
        """Generează analiza liniilor de producție"""
        if hasattr(self, 'production_lines_df') and not self.production_lines_df.empty:
            for _, line in self.production_lines_df.iterrows():
                line_frame = tk.Frame(self.preview_content, bg='#16213e', relief='solid', bd=1)
                line_frame.pack(fill=tk.X, padx=20, pady=5)

                line_text = f"""
🏭 {line['LineName']} ({line['LineID']})
• Status: {line['Status']} | Efficiency: {line['Efficiency']*100:.1f}%
• Capacity: {line['Capacity_UnitsPerHour']} units/h | Operators: {line['OperatorCount']}
• Products: {line['ProductTypes']}
                """

                tk.Label(line_frame, text=line_text,
                        font=('Segoe UI', 9),
                        fg='#ffffff', bg='#16213e',
                        justify=tk.LEFT).pack(anchor='w', padx=10, pady=10)
        else:
            tk.Label(self.preview_content, text="No production lines data available",
                    font=('Segoe UI', 12), fg='#ff6b35', bg='#0f3460').pack(pady=20)

    def generate_orders_analysis(self):
        """Generează analiza comenzilor"""
        if hasattr(self, 'orders_df') and not self.orders_df.empty:
            order_stats = self.calculate_order_stats()

            stats_text = f"""
📊 Order Statistics:
• Total Orders: {order_stats['total']}
• Completed: {order_stats['completed']} ({order_stats['completion_rate']:.1f}%)
• In Progress: {order_stats['in_progress']}
• Overdue: {order_stats['overdue']}

🎯 Priority Breakdown:
• Critical: {order_stats['critical']} | High: {order_stats['high']}
• Medium: {order_stats['medium']} | Low: {order_stats['low']}
            """

            self.add_section_content(stats_text)
        else:
            tk.Label(self.preview_content, text="No orders data available",
                    font=('Segoe UI', 12), fg='#ff6b35', bg='#0f3460').pack(pady=20)

    def generate_recommendations(self):
        """Generează recomandări"""
        recommendations = self.calculate_recommendations()

        rec_text = "\n".join([f"• {rec}" for rec in recommendations])
        self.add_section_content(rec_text)

    def generate_optimization_recommendations(self):
        """Generează recomandări de optimizare"""
        opt_recommendations = [
            "Consider increasing 'Maximize Efficiency' to 0.8+ for better performance",
            "Balance workload optimization shows potential for 15% improvement",
            "Setup time reduction could increase throughput by 200+ units/day",
            "Review bottleneck lines for capacity optimization"
        ]

        rec_text = "\n".join([f"• {rec}" for rec in opt_recommendations])
        self.add_section_content(rec_text)

    def add_section_header(self, header_text):
        """Adaugă un header de secțiune"""
        tk.Label(self.preview_content,
                text=header_text,
                font=('Segoe UI', 12, 'bold'),
                fg='#00d4aa', bg='#0f3460').pack(anchor='w', padx=20, pady=(20, 10))

    def add_section_content(self, content_text):
        """Adaugă conținut de secțiune"""
        tk.Label(self.preview_content,
                text=content_text,
                font=('Segoe UI', 10),
                fg='#ffffff', bg='#0f3460',
                justify=tk.LEFT).pack(anchor='w', padx=30, pady=(0, 10))

    # UTILITY FUNCTIONS

    def calculate_report_kpis(self):
        """Calculează KPI-urile pentru raport"""
        return {
            'overall_efficiency': self.production_metrics.get('avg_efficiency', 0.75) * 100,
            'on_time_delivery': self.production_metrics.get('on_time_delivery', 80.0),
            'line_utilization': self.production_metrics.get('line_utilization', 60.0),
            'throughput': self.production_metrics.get('throughput', 2000)
        }

    def calculate_order_stats(self):
        """Calculează statistici comenzi"""
        try:
            total = len(self.orders_df)
            completed = len(self.orders_df[self.orders_df['Progress'] == 100])
            in_progress = len(self.orders_df[(self.orders_df['Progress'] > 0) & (self.orders_df['Progress'] < 100)])
            overdue = len(self.orders_df[self.orders_df['DueDate'] < datetime.now()])

            return {
                'total': total,
                'completed': completed,
                'completion_rate': (completed / total * 100) if total > 0 else 0,
                'in_progress': in_progress,
                'overdue': overdue,
                'critical': len(self.orders_df[self.orders_df['Priority'] == 'Critical']),
                'high': len(self.orders_df[self.orders_df['Priority'] == 'High']),
                'medium': len(self.orders_df[self.orders_df['Priority'] == 'Medium']),
                'low': len(self.orders_df[self.orders_df['Priority'] == 'Low'])
            }
        except:
            return {'total': 0, 'completed': 0, 'completion_rate': 0, 'in_progress': 0, 'overdue': 0,
                    'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

    def calculate_recommendations(self):
        """Calculează recomandări"""
        recommendations = []
        kpis = self.calculate_report_kpis()

        if kpis['overall_efficiency'] < 80:
            recommendations.append("Focus on efficiency improvement - target 85%+")

        if kpis['on_time_delivery'] < 90:
            recommendations.append("Improve delivery performance - review scheduling")

        if kpis['line_utilization'] < 70:
            recommendations.append("Increase line utilization - optimize workload distribution")

        if not recommendations:
            recommendations.append("Performance is strong - maintain current optimization levels")

        return recommendations

    def get_performance_rating(self, efficiency):
        """Returnează rating de performanță"""
        if efficiency >= 90: return "🌟 Excellent"
        elif efficiency >= 80: return "✅ Good"
        elif efficiency >= 70: return "⚠️ Needs Improvement"
        else: return "🚨 Critical"

    def get_top_insight(self):
        """Returnează top insight"""
        kpis = self.calculate_report_kpis()
        if kpis['overall_efficiency'] > 85:
            return "Production efficiency exceeds industry standards"
        else:
            return "Optimization opportunities identified in efficiency metrics"

    def get_efficiency_insight(self, efficiency):
        """Returnează insight pentru eficiență"""
        if efficiency > 85:
            return "Efficiency levels are optimal"
        else:
            return f"Efficiency at {efficiency:.1f}% - target improvement to 85%+"

    def get_delivery_insight(self, delivery_rate):
        """Returnează insight pentru livrare"""
        if delivery_rate > 90:
            return "On-time delivery performance is excellent"
        else:
            return f"On-time delivery at {delivery_rate:.1f}% - review scheduling processes"

    def get_efficiency_color(self, efficiency):
        """Returnează culoarea pentru eficiență"""
        if efficiency >= 90: return "#00d4aa"
        elif efficiency >= 80: return "#2ecc71"
        elif efficiency >= 70: return "#f39c12"
        else: return "#e74c3c"

    def get_delivery_color(self, delivery_rate):
        """Returnează culoarea pentru livrare"""
        if delivery_rate >= 95: return "#00d4aa"
        elif delivery_rate >= 85: return "#2ecc71"
        elif delivery_rate >= 75: return "#f39c12"
        else: return "#e74c3c"

    def get_utilization_color(self, utilization):
        """Returnează culoarea pentru utilizare"""
        if utilization >= 80: return "#00d4aa"
        elif utilization >= 65: return "#2ecc71"
        elif utilization >= 50: return "#f39c12"
        else: return "#e74c3c"

    def generate_report(self):
        """Generează și salvează raportul"""
        try:
            # Selectează fișierul pentru salvare
            file_types = {
                'html': [("HTML files", "*.html")],
                'pdf': [("PDF files", "*.pdf")],
                'excel': [("Excel files", "*.xlsx")],
                'json': [("JSON files", "*.json")]
            }

            format_selected = self.export_format.get()
            filename = filedialog.asksaveasfilename(
                defaultextension=f".{format_selected}",
                filetypes=file_types[format_selected],
                title=f"Save {format_selected.upper()} Report"
            )

            if filename:
                if format_selected == 'html':
                    self.generate_html_report(filename)
                elif format_selected == 'json':
                    self.generate_json_report(filename)
                elif format_selected == 'excel':
                    self.generate_excel_report(filename)
                else:
                    messagebox.showinfo("Info", f"{format_selected.upper()} export not yet implemented")
                    return

                messagebox.showinfo("Report Generated", f"Report saved successfully:\n{filename}")

        except Exception as e:
            print(f"❌ Error generating report: {e}")
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")

    def generate_html_report(self, filename):
        """Generează raport HTML"""
        kpis = self.calculate_report_kpis()

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Production Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: white; margin: 20px; }}
        .header {{ background: #16213e; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }}
        .kpi-card {{ background: #0f3460; padding: 20px; border-radius: 10px; text-align: center; }}
        .section {{ background: #16213e; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .highlight {{ color: #00d4aa; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 Production Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="section">
        <h2 class="highlight">📊 Key Performance Indicators</h2>
        <div class="kpi-grid">
            <div class="kpi-card">
                <h3>📊 Overall Efficiency</h3>
                <h2>{kpis['overall_efficiency']:.1f}%</h2>
            </div>
            <div class="kpi-card">
                <h3>⏰ On-Time Delivery</h3>
                <h2>{kpis['on_time_delivery']:.1f}%</h2>
            </div>
            <div class="kpi-card">
                <h3>🏭 Line Utilization</h3>
                <h2>{kpis['line_utilization']:.1f}%</h2>
            </div>
            <div class="kpi-card">
                <h3>📦 Daily Throughput</h3>
                <h2>{kpis['throughput']:,.0f}</h2>
            </div>
        </div>
    </div>

    <div class="section">
        <h2 class="highlight">💡 Summary</h2>
        <p>Performance Rating: {self.get_performance_rating(kpis['overall_efficiency'])}</p>
        <p>Top Insight: {self.get_top_insight()}</p>
        <p>Key Recommendations:</p>
        <ul>
        """

        for rec in self.calculate_recommendations():
            html_content += f"<li>{rec}</li>"

        html_content += """
        </ul>
    </div>
</body>
</html>
        """

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def generate_json_report(self, filename):
        """Generează raport JSON"""
        report_data = {
            'report_info': {
                'type': self.report_type.get(),
                'generated_at': datetime.now().isoformat(),
                'include_charts': self.include_charts.get(),
                'include_recommendations': self.include_recommendations.get()
            },
            'kpis': self.calculate_report_kpis(),
            'production_metrics': self.production_metrics,
            'baseline_metrics': self.baseline_metrics,
            'optimization_settings': {
                'minimize_delays': self.optimization_vars['minimize_delays'].get(),
                'maximize_efficiency': self.optimization_vars['maximize_efficiency'].get(),
                'balance_workload': self.optimization_vars['balance_workload'].get(),
                'minimize_setup': self.optimization_vars['minimize_setup'].get()
            },
            'recommendations': self.calculate_recommendations(),
            'order_statistics': self.calculate_order_stats()
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)

    def generate_excel_report(self, filename):
        """Generează raport Excel"""
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # KPIs Sheet
                kpis_df = pd.DataFrame([self.calculate_report_kpis()])
                kpis_df.to_excel(writer, sheet_name='KPIs', index=False)

                # Production Lines Sheet
                if hasattr(self, 'production_lines_df') and not self.production_lines_df.empty:
                    self.production_lines_df.to_excel(writer, sheet_name='Production_Lines', index=False)

                # Orders Sheet
                if hasattr(self, 'orders_df') and not self.orders_df.empty:
                    self.orders_df.to_excel(writer, sheet_name='Orders', index=False)

                # Summary Sheet
                summary_data = {
                    'Metric': ['Total Orders', 'Active Lines', 'Overall Efficiency', 'On-Time Delivery'],
                    'Value': [
                        len(self.orders_df) if hasattr(self, 'orders_df') else 0,
                        self.production_metrics.get('active_lines', 0),
                        f"{self.production_metrics.get('avg_efficiency', 0)*100:.1f}%",
                        f"{self.production_metrics.get('on_time_delivery', 0):.1f}%"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
        except Exception as e:
            raise Exception(f"Excel generation failed: {str(e)}")

    def email_report(self):
        """Trimite raportul prin email (placeholder)"""
        messagebox.showinfo("Email Report",
                           "Email functionality would integrate with:\n" +
                           "• SMTP server configuration\n" +
                           "• Email template system\n" +
                           "• Recipient management\n" +
                           "• Attachment handling\n\n" +
                           "Feature coming soon!")

if __name__ == "__main__":
    # Test standalone
    root = tk.Tk()
    root.withdraw()

    # Date test
    test_metrics = {
        'avg_efficiency': 0.85,
        'on_time_delivery': 92.0,
        'line_utilization': 72.0,
        'throughput': 2850
    }

    test_baseline = {
        'avg_efficiency': 0.68,
        'on_time_delivery': 72.0,
        'line_utilization': 45.0,
        'throughput': 1800
    }

    test_optimization_vars = {
        'minimize_delays': tk.DoubleVar(value=0.6),
        'maximize_efficiency': tk.DoubleVar(value=0.8),
        'balance_workload': tk.DoubleVar(value=0.4),
        'minimize_setup': tk.DoubleVar(value=0.3)
    }

    reports = ReportsGenerator(root, test_metrics, pd.DataFrame(), pd.DataFrame(),
                              pd.DataFrame(), test_baseline, test_optimization_vars)
    root.mainloop()