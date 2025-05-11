from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.ttk as ttk
import matplotlib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

class Data(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="news")
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        
        try:
            self.df_movement_csv = pd.read_csv(r"data_csv\Movement.csv", header=None, names=['data'])
            self.df_level_csv = pd.read_csv(r"data_csv\Level.csv", header=None, names=['data'])
            self.df_gift_csv = pd.read_csv(r"data_csv\Gift.csv", header=None, names=['data'])
            self.df_enemies_csv = pd.read_csv(r"data_csv\Enemy.csv", header=None, names=['data'])
            self.df_bullet_csv = pd.read_csv(r"data_csv\Bullet fired.csv", header=None, names=['data'])
            self.df_time_csv = pd.read_csv(r"data_csv\Time.csv", header=None, names=['data'])
            self.df_score_csv = pd.read_csv(r"data_csv\Score.csv", header=None, names=['data'])
            self.df_whole_time_csv = pd.read_csv(r"data_csv\Time_End.csv", header=None, names=['data'])
            
            # Prepare combined data for some visualizations
            self.prepare_combined_data()
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.df_movement_csv = pd.DataFrame(columns=['data'])
            self.df_level_csv = pd.DataFrame(columns=['data'])
            self.df_gift_csv = pd.DataFrame(columns=['data'])
            self.df_enemies_csv = pd.DataFrame(columns=['data'])
            self.df_bullet_csv = pd.DataFrame(columns=['data'])
            self.df_time_csv = pd.DataFrame(columns=['data'])
            self.df_score_csv = pd.DataFrame(columns=['data'])
            self.df_whole_time_csv = pd.DataFrame(columns=['data'])
            
        self.create_widget()
    
    def prepare_combined_data(self):
        """Prepare combined dataframes for visualizations that need multiple data sources"""
        try:
            # For movement analysis
            self.df_movement = self.df_movement_csv.copy()
            
            # For level vs time analysis
            if not self.df_level_csv.empty and not self.df_time_csv.empty:
                min_len = min(len(self.df_level_csv), len(self.df_time_csv))
                self.df_level_time = pd.DataFrame({
                    'level': self.df_level_csv['data'].iloc[:min_len],
                    'time': pd.to_numeric(self.df_time_csv['data'], errors='coerce').iloc[:min_len]
                })
            
            # For movement vs level analysis
            if not self.df_movement_csv.empty and not self.df_level_csv.empty:
                # We'll count movements per level
                self.df_movement_level = pd.DataFrame({
                    'level': self.df_level_csv['data'],
                    'movement_count': 1  # Each row represents one movement
                }).groupby('level').count().reset_index()
            
            # For enemy vs level analysis
            if not self.df_enemies_csv.empty and not self.df_level_csv.empty:
                min_len = min(len(self.df_enemies_csv), len(self.df_level_csv))
                self.df_enemy_level = pd.DataFrame({
                    'level': self.df_level_csv['data'].iloc[:min_len],
                    'enemies_killed': pd.to_numeric(self.df_enemies_csv['data'], errors='coerce').iloc[:min_len]
                })
            
            # For time vs score analysis
            if not self.df_whole_time_csv.empty and not self.df_score_csv.empty:
                min_len = min(len(self.df_whole_time_csv), len(self.df_score_csv))
                self.df_time_score = pd.DataFrame({
                    'time': pd.to_numeric(self.df_whole_time_csv['data'], errors='coerce').iloc[:min_len],
                    'score': pd.to_numeric(self.df_score_csv['data'], errors='coerce').iloc[:min_len]
                })
                
        except Exception as e:
            print(f"Error preparing combined data: {e}")
    
    def create_widget(self):
        # Create Notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="news", padx=10, pady=10)
        
        # Create frames for each tab
        self.tab_movement = ttk.Frame(self.notebook)
        self.tab_time = ttk.Frame(self.notebook)
        self.tab_level = ttk.Frame(self.notebook)
        self.tab_score = ttk.Frame(self.notebook)
        self.tab_enemy = ttk.Frame(self.notebook)
        self.tab_bullet = ttk.Frame(self.notebook)
        self.tab_gift = ttk.Frame(self.notebook)
        
        # New tabs for additional visualizations
        self.tab_movement_hist = ttk.Frame(self.notebook)  # Movement histogram
        self.tab_level_time = ttk.Frame(self.notebook)     # Level vs time
        self.tab_movement_level = ttk.Frame(self.notebook) # Movement vs level
        self.tab_enemy_level = ttk.Frame(self.notebook)    # Enemy vs level
        self.tab_time_score = ttk.Frame(self.notebook)     # Time vs score
        
        # Add tabs to notebook
        self.notebook.add(self.tab_movement, text="Movement")
        self.notebook.add(self.tab_time, text="Time")
        self.notebook.add(self.tab_level, text="Level")
        self.notebook.add(self.tab_score, text="Score")
        self.notebook.add(self.tab_enemy, text="Enemy")
        self.notebook.add(self.tab_bullet, text="Bullet Fired")
        self.notebook.add(self.tab_gift, text="Gift")
        
        # Add new tabs
        self.notebook.add(self.tab_movement_hist, text="Movement Analysis")
        self.notebook.add(self.tab_level_time, text="Level vs Time")
        self.notebook.add(self.tab_movement_level, text="Movement vs Level")
        self.notebook.add(self.tab_enemy_level, text="Enemy vs Level")
        self.notebook.add(self.tab_time_score, text="Time vs Score")
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Create Treeview for Movement tab
        self.create_movement_treeview()
        
        # Create figures for all tabs
        self.create_figures()
        
        # Show initial tab
        self.show_tab("Movement")
    
    def create_movement_treeview(self):
        # Create Treeview frame
        self.tree_frame = ttk.Frame(self.tab_movement)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create Treeview with explicit columns
        self.tree = ttk.Treeview(self.tree_frame, columns=('movement', 'count', 'mode'), show='headings')

        # Define headings
        self.tree.heading('movement', text='Movement')
        self.tree.heading('count', text='Count')
        self.tree.heading('mode', text='Mode')

        # Define columns widths and alignment
        self.tree.column('movement', width=150, anchor='center')
        self.tree.column('count', width=100, anchor='center')
        self.tree.column('mode', width=100, anchor='center')

        # Add scrollbar
        tree_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        tree_scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(fill="both", expand=True)

        # Populate Treeview
        self.update_movement_tree()
    
    def create_figures(self):
        # Create figures for each original tab
        self.fig_time = Figure(figsize=(6, 4), dpi=100)
        self.ax_time = self.fig_time.add_subplot(111)
        self.canvas_time = FigureCanvasTkAgg(self.fig_time, master=self.tab_time)
        self.canvas_time.get_tk_widget().pack(fill="both", expand=True)
        
        self.fig_level = Figure(figsize=(6, 4), dpi=100)
        self.ax_level = self.fig_level.add_subplot(111)
        self.canvas_level = FigureCanvasTkAgg(self.fig_level, master=self.tab_level)
        self.canvas_level.get_tk_widget().pack(fill="both", expand=True)
        
        self.fig_score = Figure(figsize=(6, 4), dpi=100)
        self.ax_score = self.fig_score.add_subplot(111)
        self.canvas_score = FigureCanvasTkAgg(self.fig_score, master=self.tab_score)
        self.canvas_score.get_tk_widget().pack(fill="both", expand=True)
        
        self.fig_enemy = Figure(figsize=(6, 4), dpi=100)
        self.ax_enemy = self.fig_enemy.add_subplot(111)
        self.canvas_enemy = FigureCanvasTkAgg(self.fig_enemy, master=self.tab_enemy)
        self.canvas_enemy.get_tk_widget().pack(fill="both", expand=True)
        
        self.fig_bullet = Figure(figsize=(6, 4), dpi=100)
        self.ax_bullet = self.fig_bullet.add_subplot(111)
        self.canvas_bullet = FigureCanvasTkAgg(self.fig_bullet, master=self.tab_bullet)
        self.canvas_bullet.get_tk_widget().pack(fill="both", expand=True)
        
        self.fig_gift = Figure(figsize=(6, 4), dpi=100)
        self.ax_gift = self.fig_gift.add_subplot(111)
        self.canvas_gift = FigureCanvasTkAgg(self.fig_gift, master=self.tab_gift)
        self.canvas_gift.get_tk_widget().pack(fill="both", expand=True)
        
        # Create figures for new tabs
        # Movement histogram
        self.fig_movement_hist = Figure(figsize=(6, 4), dpi=100)
        self.ax_movement_hist = self.fig_movement_hist.add_subplot(111)
        self.canvas_movement_hist = FigureCanvasTkAgg(self.fig_movement_hist, master=self.tab_movement_hist)
        self.canvas_movement_hist.get_tk_widget().pack(fill="both", expand=True)
        
        # Level vs Time
        self.fig_level_time = Figure(figsize=(6, 4), dpi=100)
        self.ax_level_time = self.fig_level_time.add_subplot(111)
        self.canvas_level_time = FigureCanvasTkAgg(self.fig_level_time, master=self.tab_level_time)
        self.canvas_level_time.get_tk_widget().pack(fill="both", expand=True)
        
        # Movement vs Level
        self.fig_movement_level = Figure(figsize=(6, 4), dpi=100)
        self.ax_movement_level = self.fig_movement_level.add_subplot(111)
        self.canvas_movement_level = FigureCanvasTkAgg(self.fig_movement_level, master=self.tab_movement_level)
        self.canvas_movement_level.get_tk_widget().pack(fill="both", expand=True)
        
        # Enemy vs Level
        self.fig_enemy_level = Figure(figsize=(6, 4), dpi=100)
        self.ax_enemy_level = self.fig_enemy_level.add_subplot(111)
        self.canvas_enemy_level = FigureCanvasTkAgg(self.fig_enemy_level, master=self.tab_enemy_level)
        self.canvas_enemy_level.get_tk_widget().pack(fill="both", expand=True)
        
        # Time vs Score
        self.fig_time_score = Figure(figsize=(6, 4), dpi=100)
        self.ax_time_score = self.fig_time_score.add_subplot(111)
        self.canvas_time_score = FigureCanvasTkAgg(self.fig_time_score, master=self.tab_time_score)
        self.canvas_time_score.get_tk_widget().pack(fill="both", expand=True)
    
    def on_tab_changed(self, event):
        tab_name = self.notebook.tab(self.notebook.select(), "text")
        self.show_tab(tab_name)
    
    def show_tab(self, tab_name):
        if tab_name == "Movement":
            self.update_movement_tree()
        elif tab_name == "Time":
            self.update_time_plot()
        elif tab_name == "Level":
            self.update_level_plot()
        elif tab_name == "Score":
            self.update_score_plot()
        elif tab_name == "Enemy":
            self.update_enemy_plot()
        elif tab_name == "Bullet Fired":
            self.update_bullet_plot()
        elif tab_name == "Gift":
            self.update_gift_plot()
        elif tab_name == "Movement Analysis":
            self.update_movement_hist()
        elif tab_name == "Level vs Time":
            self.update_level_time_plot()
        elif tab_name == "Movement vs Level":
            self.update_movement_level_plot()
        elif tab_name == "Enemy vs Level":
            self.update_enemy_level_plot()
        elif tab_name == "Time vs Score":
            self.update_time_score_plot()
    
    def update_movement_tree(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Count occurrences of each movement
        movement_counts = self.df_movement_csv['data'].value_counts()

        # Find the mode (movement with max count)
        if not movement_counts.empty:
            mode_movement = movement_counts.idxmax()
        else:
            mode_movement = None

        # Add data to Treeview
        for movement, count in movement_counts.items():
            is_mode = '✓' if movement == mode_movement else ''
            self.tree.insert('', 'end', values=(movement, count, is_mode))
    
    def update_time_plot(self):
        self.df_time_csv['data'] = pd.to_numeric(self.df_time_csv['data'], errors='coerce')
        self.ax_time.clear()
        self.df_time_csv.hist(ax=self.ax_time, bins=20)
        self.ax_time.set_title("Time Distribution")
        self.ax_time.set_xlabel('Time')
        self.ax_time.set_ylabel('Frequency')
        self.canvas_time.draw()
    
    def update_level_plot(self):
        self.ax_level.clear()
        data = self.df_level_csv['data'].value_counts().sort_index()
        data.plot(kind='bar', ax=self.ax_level)
        self.ax_level.set_title("Level Distribution")
        self.ax_level.set_xlabel('Level')
        self.ax_level.set_ylabel('Count')
        self.canvas_level.draw()
    
    def update_score_plot(self):
        self.ax_score.clear()
        sns.boxplot(data=self.df_score_csv, x='data', ax=self.ax_score)
        self.ax_score.set_title("Score Distribution")
        self.ax_score.set_xlabel('Score')
        self.canvas_score.draw()
    
    def update_enemy_plot(self):
        self.ax_enemy.clear()
        data = self.df_enemies_csv['data'].value_counts().sort_index()
        data.plot(kind='bar', ax=self.ax_enemy)
        self.ax_enemy.set_title("Enemies Killed Distribution")
        self.ax_enemy.set_xlabel('Enemies Killed')
        self.ax_enemy.set_ylabel('Count')
        self.canvas_enemy.draw()
    
    def update_bullet_plot(self):
        self.ax_bullet.clear()
        sns.histplot(data=self.df_bullet_csv, x='data', ax=self.ax_bullet)
        self.ax_bullet.set_title("Bullets Fired Distribution")
        self.ax_bullet.set_xlabel('Bullets Fired')
        self.canvas_bullet.draw()
    
    def update_gift_plot(self):
        self.ax_gift.clear()
        data = self.df_gift_csv['data'].value_counts().sort_index()
        data.plot(kind='pie', autopct='%1.1f%%', ax=self.ax_gift)
        self.ax_gift.set_title("Gifts Collected Distribution")
        self.ax_gift.set_ylabel('')
        self.canvas_gift.draw()
    
    # New visualization methods
    def update_movement_hist(self):
        """Show histogram of movement directions"""
        self.ax_movement_hist.clear()
        if not self.df_movement_csv.empty:
            movement_counts = self.df_movement_csv['data'].value_counts()
            movement_counts.plot(kind='bar', ax=self.ax_movement_hist, color='skyblue')
            self.ax_movement_hist.set_title("Movement Direction Analysis")
            self.ax_movement_hist.set_xlabel('Direction')
            self.ax_movement_hist.set_ylabel('Count')
            self.ax_movement_hist.tick_params(axis='x', rotation=45)
        else:
            self.ax_movement_hist.text(0.5, 0.5, 'No movement data available', 
                                     ha='center', va='center')
        self.canvas_movement_hist.draw()
    
    def update_level_time_plot(self):
        """Show relationship between level and time spent"""
        self.ax_level_time.clear()
        if hasattr(self, 'df_level_time') and not self.df_level_time.empty:
            # Calculate average time per level
            avg_time = self.df_level_time.groupby('level')['time'].mean().reset_index()
            
            # Plot bar chart
            sns.barplot(data=avg_time, x='level', y='time', ax=self.ax_level_time, palette='viridis')
            self.ax_level_time.set_title("Average Time Spent per Level")
            self.ax_level_time.set_xlabel('Level')
            self.ax_level_time.set_ylabel('Average Time (seconds)')
        else:
            self.ax_level_time.text(0.5, 0.5, 'No level/time data available', 
                                  ha='center', va='center')
        self.canvas_level_time.draw()
    
    def update_movement_level_plot(self):
        """Show how movement count changes with level"""
        self.ax_movement_level.clear()
        if hasattr(self, 'df_movement_level') and not self.df_movement_level.empty:
            sns.lineplot(data=self.df_movement_level, x='level', y='movement_count', 
                        ax=self.ax_movement_level, marker='o')
            self.ax_movement_level.set_title("Movement Count by Level")
            self.ax_movement_level.set_xlabel('Level')
            self.ax_movement_level.set_ylabel('Total Movements')
        else:
            self.ax_movement_level.text(0.5, 0.5, 'No movement/level data available', 
                                       ha='center', va='center')
        self.canvas_movement_level.draw()
    
    def update_enemy_level_plot(self):
        """Show how enemies killed changes with level"""
        self.ax_enemy_level.clear()
        if hasattr(self, 'df_enemy_level') and not self.df_enemy_level.empty:
            # Calculate average enemies killed per level
            avg_enemies = self.df_enemy_level.groupby('level')['enemies_killed'].mean().reset_index()
            
            # Plot bar chart
            sns.barplot(data=avg_enemies, x='level', y='enemies_killed', 
                       ax=self.ax_enemy_level, palette='rocket')
            self.ax_enemy_level.set_title("Average Enemies Killed per Level")
            self.ax_enemy_level.set_xlabel('Level')
            self.ax_enemy_level.set_ylabel('Average Enemies Killed')
        else:
            self.ax_enemy_level.text(0.5, 0.5, 'No enemy/level data available', 
                                    ha='center', va='center')
        self.canvas_enemy_level.draw()
    
    def update_time_score_plot(self):
        """Show relationship between play time and score"""
        self.ax_time_score.clear()
        if hasattr(self, 'df_time_score') and not self.df_time_score.empty:
            sns.scatterplot(data=self.df_time_score, x='time', y='score', 
                           ax=self.ax_time_score, hue='score', palette='coolwarm')
            self.ax_time_score.set_title("Score vs Play Time")
            self.ax_time_score.set_xlabel('Play Time (seconds)')
            self.ax_time_score.set_ylabel('Score')
            
            # Add trend line if enough data points
            if len(self.df_time_score) > 1:
                sns.regplot(data=self.df_time_score, x='time', y='score', 
                           ax=self.ax_time_score, scatter=False, color='red')
        else:
            self.ax_time_score.text(0.5, 0.5, 'No time/score data available', 
                                  ha='center', va='center')
        self.canvas_time_score.draw()