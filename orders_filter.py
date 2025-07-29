"""
🔍 Orders Filter
Advanced filtering system for production orders
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime, timedelta

class OrdersFilter:
    def __init__(self, parent, orders_df, production_lines_df, on_filter_applied):
        self.parent = parent
        self.orders_df = orders_df
        self.production_lines_df = production_lines_df
        self.on_filter_applied = on_filter_applied  # Callback function

        # Creează fereastra
        self.window = tk.Toplevel(parent)
        self.window.title("🔍 Advanced Orders Filter")
        self.window.geometry("900x700")
        self.window.configure(bg='#1a1a2e')
        self.window.transient(parent)
        self.window.grab_set()

        # Filter variables
        self.init_filter_variables()

        print("🔍 Orders Filter initializing...")
        self.create_interface()

    def init_filter_variables(self):
        """Inițializează variabilele de filtrare"""
        # Status filters
        self.status_vars = {
            'Planned': tk.BooleanVar(value=True),
            'In Progress': tk.BooleanVar(value=True),
            'Completed': tk.BooleanVar(value=True),
            'On Hold': tk.BooleanVar(value=True),
            'Critical Delay': tk.BooleanVar(value=True),
            'Queued': tk.BooleanVar(value=True),
            'Scheduled': tk.BooleanVar(value=True)
        }

        # Priority filters
        self.priority_vars = {
            'Critical': tk.BooleanVar(value=True),
            'High': tk.BooleanVar(value=True),
            'Medium': tk.BooleanVar(value=True),
            'Low': tk.BooleanVar(value=True)
        }

        # Other filters
        self.search_text = tk.StringVar()
        self.customer_filter = tk.StringVar(value="All")
        self.product_type_filter = tk.StringVar(value="All")
        self.assigned_line_filter = tk.StringVar(value="All")

        # Date filters
        self.date_filter_type = tk.StringVar(value="all_time")
        self.custom_start_date = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.custom_end_date = tk.StringVar(value=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))

        # Progress filters
        self.progress_min = tk.IntVar(value=0)
        self.progress_max = tk.IntVar(value=100)

        # Overdue filter
        self.show_overdue_only = tk.BooleanVar(value=False)

    def create_interface(self):
        """Creează interfața de filtrare"""
        # Header
        self.create_header()

        # Main content
        self.create_main_content()

        # Footer cu butoane
        self.create_footer()

        # Results preview
        self.create_results_preview()

    def create_header(self):
        """Creează header-ul"""
        header_frame = tk.Frame(self.window, bg='#16213e', height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)

        # Titlu
        tk.Label(header_frame,
                text="🔍 Advanced Orders Filter",
                font=('Segoe UI', 16, 'bold'),
                fg='#00d4aa', bg='#16213e').pack(side=tk.LEFT, pady=25, padx=20)

        # Quick filter buttons
        quick_frame = tk.Frame(header_frame, bg='#16213e')
        quick_frame.pack(side=tk.RIGHT, pady=20, padx=20)

        tk.Button(quick_frame, text="🚨 Critical Only",
                 command=self.filter_critical_only,
                 font=('Segoe UI', 9), bg='#ff4757', fg='white',
                 relief='flat', padx=10, pady=5).pack(side=tk.LEFT, padx=2)

        tk.Button(quick_frame, text="⏰ Overdue",
                 command=self.filter_overdue_only,
                 font=('Segoe UI', 9), bg='#ff6b35', fg='white',
                 relief='flat', padx=10, pady=5).pack(side=tk.LEFT, padx=2)

        tk.Button(quick_frame, text="🔄 In Progress",
                 command=self.filter_in_progress_only,
                 font=('Segoe UI', 9), bg='#ffa502', fg='white',
                 relief='flat', padx=10, pady=5).pack(side=tk.LEFT, padx=2)

    def create_main_content(self):
        """Creează conținutul principal cu filtrele"""
        main_frame = tk.Frame(self.window, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas pentru scroll
        canvas = tk.Canvas(main_frame, bg='#1a1a2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a2e')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Container pentru filtre în 2 coloane
        filters_container = tk.Frame(scrollable_frame, bg='#1a1a2e')
        filters_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Coloana stânga
        left_column = tk.Frame(filters_container, bg='#1a1a2e')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Coloana dreapta
        right_column = tk.Frame(filters_container, bg='#1a1a2e')
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Populare coloane
        self.create_left_column_filters(left_column)
        self.create_right_column_filters(right_column)

    def create_left_column_filters(self, parent):
        """Creează filtrele din coloana stânga"""
        # 1. Text Search
        search_frame = tk.LabelFrame(parent, text="🔍 Text Search",
                                   bg='#16213e', fg='#00d4aa',
                                   font=('Segoe UI', 11, 'bold'))
        search_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(search_frame, text="Search in Product Name, Customer, Notes:",
                font=('Segoe UI', 9),
                fg='#ffffff', bg='#16213e').pack(anchor='w', padx=15, pady=(10, 5))

        search_entry = tk.Entry(search_frame, textvariable=self.search_text,
                              font=('Segoe UI', 10),
                              bg='#0f3460', fg='#ffffff', insertbackground='#00d4aa')
        search_entry.pack(fill=tk.X, padx=15, pady=(0, 15))
        search_entry.bind('<KeyRelease>', self.on_search_change)

        # 2. Status Filter
        status_frame = tk.LabelFrame(parent, text="📊 Order Status",
                                   bg='#16213e', fg='#00d4aa',
                                   font=('Segoe UI', 11, 'bold'))
        status_frame.pack(fill=tk.X, pady=(0, 15))

        status_grid = tk.Frame(status_frame, bg='#16213e')
        status_grid.pack(fill=tk.X, padx=15, pady=15)

        status_colors = {
            'Planned': '#0078ff',
            'In Progress': '#ffa502',
            'Completed': '#2ecc71',
            'Critical Delay': '#ff4757',
            'On Hold': '#666666',
            'Queued': '#b0b0b0',
            'Scheduled': '#9b59b6'
        }

        for i, (status, var) in enumerate(self.status_vars.items()):
            row = i // 2
            col = i % 2

            cb_frame = tk.Frame(status_grid, bg='#16213e')
            cb_frame.grid(row=row, column=col, sticky='w', padx=(0, 20), pady=2)

            cb = tk.Checkbutton(cb_frame, text=status,
                               variable=var,
                               font=('Segoe UI', 9),
                               fg=status_colors.get(status, '#ffffff'),
                               bg='#16213e',
                               selectcolor='#0f3460',
                               command=self.update_preview)
            cb.pack(anchor='w')

        # 3. Priority Filter
        priority_frame = tk.LabelFrame(parent, text="🎯 Priority Level",
                                     bg='#16213e', fg='#00d4aa',
                                     font=('Segoe UI', 11, 'bold'))
        priority_frame.pack(fill=tk.X, pady=(0, 15))

        priority_colors = {
            'Critical': '#ff4757',
            'High': '#ff6b35',
            'Medium': '#ffa502',
            'Low': '#2ecc71'
        }

        for priority, var in self.priority_vars.items():
            cb_frame = tk.Frame(priority_frame, bg='#16213e')
            cb_frame.pack(anchor='w', padx=15, pady=2)

            cb = tk.Checkbutton(cb_frame, text=f"● {priority}",
                               variable=var,
                               font=('Segoe UI', 9, 'bold'),
                               fg=priority_colors.get(priority, '#ffffff'),
                               bg='#16213e',
                               selectcolor='#0f3460',
                               command=self.update_preview)
            cb.pack(anchor='w')

        # 4. Progress Range
        progress_frame = tk.LabelFrame(parent, text="📈 Progress Range",
                                     bg='#16213e', fg='#00d4aa',
                                     font=('Segoe UI', 11, 'bold'))
        progress_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(progress_frame, text="Minimum Progress:",
                font=('Segoe UI', 9),
                fg='#ffffff', bg='#16213e').pack(anchor='w', padx=15, pady=(10, 0))

        min_scale = tk.Scale(progress_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                           variable=self.progress_min, resolution=5,
                           bg='#16213e', fg='#ffffff', troughcolor='#0f3460',
                           command=lambda x: self.update_preview())
        min_scale.pack(fill=tk.X, padx=15, pady=(0, 5))

        tk.Label(progress_frame, text="Maximum Progress:",
                font=('Segoe UI', 9),
                fg='#ffffff', bg='#16213e').pack(anchor='w', padx=15)

        max_scale = tk.Scale(progress_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                           variable=self.progress_max, resolution=5,
                           bg='#16213e', fg='#ffffff', troughcolor='#0f3460',
                           command=lambda x: self.update_preview())
        max_scale.pack(fill=tk.X, padx=15, pady=(0, 15))

    def create_right_column_filters(self, parent):
        """Creează filtrele din coloana dreapta"""
        # 1. Customer Filter
        customer_frame = tk.LabelFrame(parent, text="🏢 Customer",
                                     bg='#16213e', fg='#00d4aa',
                                     font=('Segoe UI', 11, 'bold'))
        customer_frame.pack(fill=tk.X, pady=(0, 15))

        customers = ["All"] + list(self.orders_df['CustomerName'].unique()) if not self.orders_df.empty else ["All"]
        customer_combo = ttk.Combobox(customer_frame, textvariable=self.customer_filter,
                                    values=customers, state="readonly")
        customer_combo.pack(fill=tk.X, padx=15, pady=15)
        customer_combo.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

        # 2. Product Type Filter
        product_frame = tk.LabelFrame(parent, text="🎯 Product Type",
                                    bg='#16213e', fg='#00d4aa',
                                    font=('Segoe UI', 11, 'bold'))
        product_frame.pack(fill=tk.X, pady=(0, 15))

        product_types = ["All"] + list(self.orders_df['ProductType'].unique()) if not self.orders_df.empty else ["All"]
        product_combo = ttk.Combobox(product_frame, textvariable=self.product_type_filter,
                                   values=product_types, state="readonly")
        product_combo.pack(fill=tk.X, padx=15, pady=15)
        product_combo.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

        # 3. Assigned Line Filter
        line_frame = tk.LabelFrame(parent, text="🏭 Assigned Line",
                                 bg='#16213e', fg='#00d4aa',
                                 font=('Segoe UI', 11, 'bold'))
        line_frame.pack(fill=tk.X, pady=(0, 15))

        lines = ["All", "Unassigned"] + list(self.production_lines_df['LineID'].unique()) if not self.production_lines_df.empty else ["All", "Unassigned"]
        line_combo = ttk.Combobox(line_frame, textvariable=self.assigned_line_filter,
                                values=lines, state="readonly")
        line_combo.pack(fill=tk.X, padx=15, pady=15)
        line_combo.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

        # 4. Date Range Filter
        date_frame = tk.LabelFrame(parent, text="📅 Date Range",
                                 bg='#16213e', fg='#00d4aa',
                                 font=('Segoe UI', 11, 'bold'))
        date_frame.pack(fill=tk.X, pady=(0, 15))

        # Date range options
        date_options = [
            ("all_time", "All Time"),
            ("today", "Today"),
            ("this_week", "This Week"),
            ("this_month", "This Month"),
            ("overdue", "Overdue Orders"),
            ("custom", "Custom Range")
        ]

        for value, text in date_options:
            tk.Radiobutton(date_frame, text=text,
                          variable=self.date_filter_type, value=value,
                          font=('Segoe UI', 9),
                          fg='#ffffff', bg='#16213e',
                          selectcolor='#0f3460',
                          command=self.update_preview).pack(anchor='w', padx=15, pady=2)

        # Custom date inputs
        custom_frame = tk.Frame(date_frame, bg='#16213e')
        custom_frame.pack(fill=tk.X, padx=15, pady=(5, 15))

        tk.Label(custom_frame, text="From:", font=('Segoe UI', 8),
                fg='#b0b0b0', bg='#16213e').grid(row=0, column=0, sticky='w')
        start_entry = tk.Entry(custom_frame, textvariable=self.custom_start_date, width=12,
                             font=('Segoe UI', 8), bg='#0f3460', fg='#ffffff')
        start_entry.grid(row=0, column=1, padx=5)

        tk.Label(custom_frame, text="To:", font=('Segoe UI', 8),
                fg='#b0b0b0', bg='#16213e').grid(row=0, column=2, sticky='w', padx=(10, 0))
        end_entry = tk.Entry(custom_frame, textvariable=self.custom_end_date, width=12,
                           font=('Segoe UI', 8), bg='#0f3460', fg='#ffffff')
        end_entry.grid(row=0, column=3, padx=5)

        # 5. Special Filters
        special_frame = tk.LabelFrame(parent, text="⚠️ Special Filters",
                                    bg='#16213e', fg='#00d4aa',
                                    font=('Segoe UI', 11, 'bold'))
        special_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Checkbutton(special_frame, text="🚨 Show only overdue orders",
                      variable=self.show_overdue_only,
                      font=('Segoe UI', 9),
                      fg='#ff4757', bg='#16213e',
                      selectcolor='#0f3460',
                      command=self.update_preview).pack(anchor='w', padx=15, pady=10)

    def create_results_preview(self):
        """Creează preview-ul rezultatelor"""
        preview_frame = tk.LabelFrame(self.window, text="📊 Filter Results Preview",
                                    bg='#16213e', fg='#00d4aa',
                                    font=('Segoe UI', 11, 'bold'), height=120)
        preview_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        preview_frame.pack_propagate(False)

        self.results_text = tk.StringVar(value="Ready to filter...")
        results_label = tk.Label(preview_frame, textvariable=self.results_text,
                               font=('Segoe UI', 10),
                               fg='#ffffff', bg='#16213e',
                               justify=tk.LEFT)
        results_label.pack(padx=20, pady=20)

        # Update initial preview
        self.update_preview()

    def create_footer(self):
        """Creează footer-ul cu butoanele de acțiune"""
        footer_frame = tk.Frame(self.window, bg='#16213e', height=60)
        footer_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        footer_frame.pack_propagate(False)

        buttons_frame = tk.Frame(footer_frame, bg='#16213e')
        buttons_frame.pack(expand=True, pady=15)

        tk.Button(buttons_frame, text="🔍 Apply Filter",
                 command=self.apply_filter,
                 font=('Segoe UI', 12, 'bold'), bg='#00d4aa', fg='white',
                 relief='flat', padx=30, pady=8).pack(side=tk.LEFT, padx=10)

        tk.Button(buttons_frame, text="🔄 Reset All",
                 command=self.reset_filters,
                 font=('Segoe UI', 11), bg='#ffa502', fg='white',
                 relief='flat', padx=20, pady=8).pack(side=tk.LEFT, padx=10)

        tk.Button(buttons_frame, text="❌ Cancel",
                 command=self.window.destroy,
                 font=('Segoe UI', 11), bg='#666666', fg='white',
                 relief='flat', padx=20, pady=8).pack(side=tk.LEFT, padx=10)

    def apply_filter(self):
        """Aplică filtrul și închide fereastra - FIXED fără rezultate goale"""
        try:
            filtered_df = self.get_filtered_dataframe()

            print(f"🔍 Filter result: {len(filtered_df)} orders found")

            # VALIDARE: Dacă nu găsește nimic, întreabă utilizatorul
            if len(filtered_df) == 0:
                result = messagebox.askyesno(
                    "No Results Found",
                    "No orders match the selected criteria.\n\n" +
                    "What would you like to do?\n" +
                    "• YES: Keep filter window open to adjust criteria\n" +
                    "• NO: Close filter and keep current view"
                )

                if result:
                    # Utilizatorul a ales YES - păstrează fereastra deschisă pentru ajustări
                    messagebox.showinfo(
                        "Filter Criteria",
                        "Please adjust your filter criteria to find matching orders.\n\n" +
                        "💡 Tip: Try expanding the search criteria or check different status/priority options."
                    )
                    return  # Nu închide fereastra, permite ajustarea criteriilor
                else:
                    # Utilizatorul a ales NO - închide filtrul fără a aplica nimic
                    print("🔍 Filter cancelled - no changes applied")
                    self.window.destroy()
                    return

            # Apelează callback-ul DOAR dacă există rezultate
            if self.on_filter_applied:
                self.on_filter_applied(filtered_df)

            print(f"✅ Filter applied successfully with {len(filtered_df)} orders")
            self.window.destroy()

        except Exception as e:
            print(f"❌ Error applying filter: {e}")
            messagebox.showerror("Error", f"Failed to apply filter:\n{str(e)}")

    # Metodă alternativă cu opțiuni mai clare
    def apply_filter_alternative(self):
        """Versiune alternativă cu opțiuni mai clare"""
        try:
            filtered_df = self.get_filtered_dataframe()

            print(f"🔍 Filter result: {len(filtered_df)} orders found")

            # VALIDARE: Dacă nu găsește nimic
            if len(filtered_df) == 0:
                # Dialog cu 3 opțiuni
                choice = messagebox.askyesnocancel(
                    "No Results Found",
                    "No orders match the selected criteria.\n\n" +
                    "Choose an option:\n" +
                    "• YES: Reset filters and try again\n" +
                    "• NO: Close without applying filter\n" +
                    "• CANCEL: Keep this window open to adjust criteria"
                )

                if choice is True:
                    # YES - Reset filters
                    self.reset_filters()
                    messagebox.showinfo("Filters Reset", "All filters have been reset. Please try again.")
                    return
                elif choice is False:
                    # NO - Close without applying
                    print("🔍 Filter cancelled - no changes applied")
                    self.window.destroy()
                    return
                else:
                    # CANCEL - Keep window open
                    return

            # Apelează callback-ul DOAR dacă există rezultate
            if self.on_filter_applied:
                self.on_filter_applied(filtered_df)

            print(f"✅ Filter applied successfully with {len(filtered_df)} orders")
            self.window.destroy()

        except Exception as e:
            print(f"❌ Error applying filter: {e}")
            messagebox.showerror("Error", f"Failed to apply filter:\n{str(e)}")

    # Adăugați și o metodă pentru a preveni aplicarea filtrelor foarte restrictive
    def validate_filter_criteria(self):
        """Validează criteriile de filtrare pentru a preveni rezultate goale"""
        # Verifică dacă toate status-urile sunt dezactivate
        selected_statuses = [status for status, var in self.status_vars.items() if var.get()]
        if not selected_statuses:
            messagebox.showwarning(
                "Invalid Filter Criteria",
                "Please select at least one order status."
            )
            return False

        # Verifică dacă toate prioritățile sunt dezactivate
        selected_priorities = [priority for priority, var in self.priority_vars.items() if var.get()]
        if not selected_priorities:
            messagebox.showwarning(
                "Invalid Filter Criteria",
                "Please select at least one priority level."
            )
            return False

        # Verifică dacă range-ul de progres este valid
        if self.progress_min.get() > self.progress_max.get():
            messagebox.showwarning(
                "Invalid Progress Range",
                "Minimum progress cannot be greater than maximum progress."
            )
            return False

        return True

    # Versiunea îmbunătățită cu validare
    def apply_filter_with_validation(self):
        """Aplică filtrul cu validare completă"""
        try:
            # Validează criteriile înainte de a filtra
            if not self.validate_filter_criteria():
                return

            filtered_df = self.get_filtered_dataframe()

            print(f"🔍 Filter result: {len(filtered_df)} orders found")

            # Verifică rezultatele
            if len(filtered_df) == 0:
                # Oferă opțiuni utile utilizatorului
                result = messagebox.askyesnocancel(
                    "No Results Found",
                    "No orders match the current criteria.\n\n" +
                    f"Total orders available: {len(self.orders_df)}\n\n" +
                    "Options:\n" +
                    "• YES: Reset all filters and start over\n" +
                    "• NO: Close filter window (keep current view)\n" +
                    "• CANCEL: Adjust current criteria",
                    icon='warning'
                )

                if result is True:
                    # Reset și recomencează
                    self.reset_filters()
                    messagebox.showinfo(
                        "Filters Reset",
                        "All filters have been reset to show all orders.\n" +
                        "You can now adjust the criteria as needed."
                    )
                    return
                elif result is False:
                    # Închide fără modificări
                    print("🔍 Filter window closed without applying changes")
                    self.window.destroy()
                    return
                else:
                    # Rămâne în fereastră pentru ajustări
                    return

            # Confirmă aplicarea pentru rezultate mici
            if len(filtered_df) < 5:
                result = messagebox.askyesno(
                    "Few Results Found",
                    f"Only {len(filtered_df)} orders match your criteria.\n\n" +
                    "Do you want to apply this filter?",
                    icon='question'
                )
                if not result:
                    return

            # Aplică filtrul
            if self.on_filter_applied:
                self.on_filter_applied(filtered_df)

            print(f"✅ Filter applied successfully with {len(filtered_df)} orders")
            self.window.destroy()

        except Exception as e:
            print(f"❌ Error applying filter: {e}")
            messagebox.showerror("Error", f"Failed to apply filter:\n{str(e)}")

    def get_filtered_dataframe(self):
        """Returnează DataFrame-ul filtrat - FIXED SEARCH"""
        if self.orders_df.empty:
            return self.orders_df

        filtered_df = self.orders_df.copy()

        # 1. Status filter
        selected_statuses = [status for status, var in self.status_vars.items() if var.get()]
        if selected_statuses:
            filtered_df = filtered_df[filtered_df['Status'].isin(selected_statuses)]

        # 2. Priority filter
        selected_priorities = [priority for priority, var in self.priority_vars.items() if var.get()]
        if selected_priorities:
            filtered_df = filtered_df[filtered_df['Priority'].isin(selected_priorities)]

        # 3. Text search - FIXED VERSION
        search_term = self.search_text.get().strip()
        if search_term:
            print(f"🔍 Searching for: '{search_term}'")

            # CASE-INSENSITIVE search cu spații îndepărtate
            search_term_clean = search_term.lower().strip()

            try:
                # Convertește toate coloanele la string și face lowercase
                product_search = filtered_df['ProductName'].astype(str).str.lower().str.strip().str.contains(search_term_clean, case=False, na=False, regex=False)
                customer_search = filtered_df['CustomerName'].astype(str).str.lower().str.strip().str.contains(search_term_clean, case=False, na=False, regex=False)
                order_id_search = filtered_df['OrderID'].astype(str).str.lower().str.strip().str.contains(search_term_clean, case=False, na=False, regex=False)

                # Verifică și Notes dacă există coloana
                if 'Notes' in filtered_df.columns:
                    notes_search = filtered_df['Notes'].astype(str).str.lower().str.strip().str.contains(search_term_clean, case=False, na=False, regex=False)
                    search_mask = product_search | customer_search | order_id_search | notes_search
                else:
                    search_mask = product_search | customer_search | order_id_search

                # DEBUG: Afișează rezultatele căutării
                matches_found = search_mask.sum()
                print(f"   Found {matches_found} matches")

                if matches_found == 0:
                    print("   🔍 Debug - Available data:")
                    print(f"   ProductNames: {filtered_df['ProductName'].tolist()}")
                    print(f"   CustomerNames: {filtered_df['CustomerName'].tolist()}")
                    print(f"   OrderIDs: {filtered_df['OrderID'].tolist()}")

                filtered_df = filtered_df[search_mask]

            except Exception as e:
                print(f"❌ Error in search: {e}")
                # Fallback la căutarea simplă
                search_mask = (
                    filtered_df['ProductName'].str.contains(search_term, case=False, na=False) |
                    filtered_df['CustomerName'].str.contains(search_term, case=False, na=False) |
                    filtered_df['OrderID'].str.contains(search_term, case=False, na=False)
                )
                filtered_df = filtered_df[search_mask]

        # 4. Customer filter
        if self.customer_filter.get() != "All":
            filtered_df = filtered_df[filtered_df['CustomerName'] == self.customer_filter.get()]

        # 5. Product type filter
        if self.product_type_filter.get() != "All":
            filtered_df = filtered_df[filtered_df['ProductType'] == self.product_type_filter.get()]

        # 6. Assigned line filter
        line_filter = self.assigned_line_filter.get()
        if line_filter == "Unassigned":
            filtered_df = filtered_df[(filtered_df['AssignedLine'].isna()) | (filtered_df['AssignedLine'] == '')]
        elif line_filter != "All":
            filtered_df = filtered_df[filtered_df['AssignedLine'] == line_filter]

        # 7. Progress range filter
        min_progress = self.progress_min.get()
        max_progress = self.progress_max.get()
        filtered_df = filtered_df[
            (filtered_df['Progress'] >= min_progress) &
            (filtered_df['Progress'] <= max_progress)
        ]

        # 8. Date range filter
        date_filter = self.date_filter_type.get()
        if date_filter != "all_time":
            today = datetime.now()

            try:
                if date_filter == "today":
                    filtered_df = filtered_df[pd.to_datetime(filtered_df['OrderDate']).dt.date == today.date()]
                elif date_filter == "this_week":
                    week_start = today - timedelta(days=today.weekday())
                    filtered_df = filtered_df[pd.to_datetime(filtered_df['OrderDate']) >= week_start]
                elif date_filter == "this_month":
                    month_start = today.replace(day=1)
                    filtered_df = filtered_df[pd.to_datetime(filtered_df['OrderDate']) >= month_start]
                elif date_filter == "overdue":
                    filtered_df = filtered_df[pd.to_datetime(filtered_df['DueDate']) < today]
                elif date_filter == "custom":
                    start_date = datetime.strptime(self.custom_start_date.get(), '%Y-%m-%d')
                    end_date = datetime.strptime(self.custom_end_date.get(), '%Y-%m-%d')
                    filtered_df = filtered_df[
                        (pd.to_datetime(filtered_df['OrderDate']) >= start_date) &
                        (pd.to_datetime(filtered_df['OrderDate']) <= end_date)
                    ]
            except Exception as e:
                print(f"❌ Error in date filtering: {e}")

        # 9. Overdue only filter
        if self.show_overdue_only.get():
            try:
                filtered_df = filtered_df[pd.to_datetime(filtered_df['DueDate']) < datetime.now()]
            except Exception as e:
                print(f"❌ Error in overdue filtering: {e}")

        return filtered_df

    def update_preview(self):
        """Actualizează preview-ul rezultatelor"""
        try:
            filtered_df = self.get_filtered_dataframe()
            total_orders = len(self.orders_df)
            filtered_count = len(filtered_df)

            if filtered_count == 0:
                self.results_text.set("❌ No orders match the selected criteria")
            elif filtered_count == total_orders:
                self.results_text.set(f"✅ All {total_orders} orders will be shown")
            else:
                percentage = (filtered_count / total_orders) * 100

                # Status breakdown
                status_breakdown = filtered_df['Status'].value_counts()
                status_text = " | ".join([f"{status}: {count}" for status, count in status_breakdown.head(3).items()])

                self.results_text.set(
                    f"🔍 {filtered_count} of {total_orders} orders ({percentage:.1f}%)\n"
                    f"📊 {status_text}"
                )

        except Exception as e:
            self.results_text.set(f"❌ Error: {str(e)}")

    def on_search_change(self, event):
        """Handle search text change - cu debounce"""
        # Cancel previous scheduled update
        if hasattr(self, '_search_timer'):
            self.window.after_cancel(self._search_timer)

        # Schedule new update after 500ms delay
        self._search_timer = self.window.after(500, self.update_preview)

    def reset_filters(self):
        """Resetează toate filtrele"""
        # Reset status filters
        for var in self.status_vars.values():
            var.set(True)

        # Reset priority filters
        for var in self.priority_vars.values():
            var.set(True)

        # Reset other filters
        self.search_text.set("")
        self.customer_filter.set("All")
        self.product_type_filter.set("All")
        self.assigned_line_filter.set("All")
        self.date_filter_type.set("all_time")
        self.progress_min.set(0)
        self.progress_max.set(100)
        self.show_overdue_only.set(False)

        self.update_preview()

    # Quick filter methods
    def filter_critical_only(self):
        """Quick filter pentru doar comenzi critice"""
        self.reset_filters()
        for priority, var in self.priority_vars.items():
            var.set(priority == 'Critical')
        self.update_preview()

    def filter_overdue_only(self):
        """Quick filter pentru doar comenzi întârziate"""
        self.reset_filters()
        self.show_overdue_only.set(True)
        self.update_preview()

    def filter_in_progress_only(self):
        """Quick filter pentru doar comenzi în progres"""
        self.reset_filters()
        for status, var in self.status_vars.items():
            var.set(status == 'In Progress')
        self.update_preview()

if __name__ == "__main__":
    # Test standalone
    root = tk.Tk()
    root.withdraw()

    # Date test
    test_orders = pd.DataFrame([
        {'OrderID': 'TEST-001', 'Status': 'In Progress', 'Priority': 'High',
         'CustomerName': 'Test Customer', 'ProductType': 'Electronics',
         'ProductName': 'Test Product', 'Progress': 50, 'AssignedLine': 'LINE-A01',
         'OrderDate': '2025-07-29', 'DueDate': '2025-08-10', 'Notes': 'Test notes'}
    ])

    def test_callback(filtered_df):
        print(f"Filter applied: {len(filtered_df)} orders")

    filter_window = OrdersFilter(root, test_orders, pd.DataFrame(), test_callback)
    root.mainloop()