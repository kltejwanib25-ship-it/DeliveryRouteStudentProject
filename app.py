import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from optimizer import optimize

BACKGROUND = '#f4f6fa'
NAVY = '#17253d'
BLUE = '#2563eb'
MUTED = '#5a667a'

SAMPLE = [
    ('Delivery Office', 0.0, 0.0),
    ('Book Shop', 2.0, 6.0),
    ('Grocery Store', 7.0, 1.0),
    ('Customer A', 3.0, 3.0),
    ('Customer B', 8.0, 7.0),
    ('Medical Store', 5.0, 5.0),
]


class DeliveryApp:
    def __init__(self, root):
        self.root = root
        root.title('Smart Delivery Route Planner | DAA Mini Project')
        root.geometry('1060x710')
        root.minsize(850, 620)
        root.configure(bg=BACKGROUND)
        self.stops = list(SAMPLE)
        self.result = None
        self.build_ui()
        self.refresh_table()
        self.draw_map()

    def make_label(self, parent, text, size=11, bold=False, color=NAVY, bg=BACKGROUND):
        return tk.Label(parent, text=text, font=('Segoe UI', size, 'bold' if bold else 'normal'), fg=color, bg=bg)

    def build_ui(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=18)
        header.pack(fill='x')
        self.make_label(header, 'Smart Delivery Route Planner', 20, True, 'white', NAVY).pack(anchor='w')
        self.make_label(header, 'DAA Mini Project  •  Nearest Neighbor + 2-opt  •  Fictional map coordinates', 10, False, '#d2dbec', NAVY).pack(anchor='w', pady=(4,0))

        body = tk.Frame(self.root, bg=BACKGROUND, padx=18, pady=16)
        body.pack(fill='both', expand=True)
        left = tk.Frame(body, bg='white', padx=15, pady=14, highlightbackground='#dce3ef', highlightthickness=1)
        left.pack(side='left', fill='y', padx=(0,12))
        right = tk.Frame(body, bg=BACKGROUND)
        right.pack(side='left', fill='both', expand=True)

        self.make_label(left, 'Delivery stops', 14, True, bg='white').pack(anchor='w')
        self.make_label(left, 'First row is the depot (start/end).', 9, color=MUTED, bg='white').pack(anchor='w', pady=(2,10))
        columns = ('name','x','y')
        self.tree = ttk.Treeview(left, columns=columns, show='headings', height=13, selectmode='browse')
        for key,title,width in [('name','Location',145),('x','X (km)',67),('y','Y (km)',67)]:
            self.tree.heading(key,text=title)
            self.tree.column(key,width=width,anchor='w' if key=='name' else 'center',stretch=False)
        self.tree.pack()
        self.tree.bind('<<TreeviewSelect>>', self.fill_selection)
        form = tk.Frame(left, bg='white')
        form.pack(fill='x', pady=(12,4))
        self.name_entry = self.entry(form, 'Location name', 0, 24)
        self.x_entry = self.entry(form, 'X (km)', 1, 10)
        self.y_entry = self.entry(form, 'Y (km)', 2, 10)
        buttons = tk.Frame(left, bg='white')
        buttons.pack(fill='x', pady=8)
        self.button(buttons,'Add stop',self.add_stop,BLUE,'white').pack(side='left',padx=(0,5))
        self.button(buttons,'Update',self.update_stop,'#e9eef9',NAVY).pack(side='left',padx=(0,5))
        self.button(buttons,'Remove',self.remove_stop,'#fce8e7','#a52a22').pack(side='left')
        self.button(left,'Optimize route',self.run_optimization,BLUE,'white',fill='x').pack(fill='x',pady=(9,6))
        row = tk.Frame(left,bg='white');row.pack(fill='x')
        self.button(row,'Load example',self.load_sample,'#e9eef9',NAVY).pack(side='left',padx=(0,5))
        self.button(row,'Export CSV',self.export_csv,'#e9eef9',NAVY).pack(side='left')
        self.make_label(left,'Tip: Coordinates use a simple 2D grid, not GPS.',9,color=MUTED,bg='white').pack(anchor='w',pady=(14,0))

        map_card = tk.Frame(right,bg='white',padx=13,pady=12,highlightbackground='#dce3ef',highlightthickness=1)
        map_card.pack(fill='both',expand=True)
        self.make_label(map_card,'Route visualization',14,True,bg='white').pack(anchor='w')
        self.canvas = tk.Canvas(map_card,bg='#f8fbff',highlightthickness=0,height=350)
        self.canvas.pack(fill='both',expand=True,pady=(12,5))
        self.canvas.bind('<Configure>',lambda e:self.draw_map())
        self.make_label(map_card,'Blue = delivery route    ● Depot = starting and ending point',9,color=MUTED,bg='white').pack(anchor='w')

        results = tk.Frame(right,bg='white',padx=15,pady=12,highlightbackground='#dce3ef',highlightthickness=1)
        results.pack(fill='x',pady=(12,0))
        self.make_label(results,'Route results',14,True,bg='white').pack(anchor='w')
        self.summary = self.make_label(results,'Click “Optimize route” to calculate a route.',11,color=MUTED,bg='white')
        self.summary.pack(anchor='w',pady=(7,5))
        self.sequence = self.make_label(results,'',10,color=NAVY,bg='white')
        self.sequence.pack(anchor='w')

    def entry(self,parent,label,row,width):
        frame = tk.Frame(parent,bg='white')
        frame.pack(fill='x',pady=3)
        self.make_label(frame,label,10,bg='white').pack(side='left')
        e=ttk.Entry(frame,width=width)
        e.pack(side='right')
        return e

    def button(self,parent,text,command,bg,fg,fill=None):
        return tk.Button(parent,text=text,command=command,bg=bg,fg=fg,font=('Segoe UI',10,'bold'),
                         relief='flat',padx=11,pady=8,cursor='hand2',activebackground='#d8e5ff')

    def refresh_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for idx,(name,x,y) in enumerate(self.stops):
            self.tree.insert('','end',iid=str(idx),values=(name,f'{x:g}',f'{y:g}'))

    def fill_selection(self,_event=None):
        selection=self.tree.selection()
        if not selection: return
        name,x,y=self.stops[int(selection[0])]
        for entry,text in ((self.name_entry,name),(self.x_entry,str(x)),(self.y_entry,str(y))):
            entry.delete(0,'end');entry.insert(0,text)

    def read_form(self):
        name=self.name_entry.get().strip()
        if not name or len(name)>40: raise ValueError('Enter a location name (1–40 characters).')
        try:
            x=float(self.x_entry.get());y=float(self.y_entry.get())
        except ValueError: raise ValueError('X and Y must be numbers.')
        from math import isfinite
        if not isfinite(x) or not isfinite(y) or abs(x)>1000 or abs(y)>1000:
            raise ValueError('Enter coordinates between -1000 and 1000.')
        return (name,x,y)

    def clear_result(self):
        self.result=None
        self.summary.config(text='Click “Optimize route” to calculate a route.')
        self.sequence.config(text='')
        self.draw_map()

    def add_stop(self):
        try:
            if len(self.stops)>=16: raise ValueError('Maximum 15 deliveries plus one depot.')
            self.stops.append(self.read_form())
            self.refresh_table();self.clear_result()
        except ValueError as e: messagebox.showerror('Invalid stop',str(e))

    def update_stop(self):
        selection=self.tree.selection()
        if not selection: return messagebox.showinfo('Select a stop','Choose a row to update.')
        try:
            self.stops[int(selection[0])]=self.read_form()
            self.refresh_table();self.clear_result()
        except ValueError as e: messagebox.showerror('Invalid stop',str(e))

    def remove_stop(self):
        selection=self.tree.selection()
        if not selection: return messagebox.showinfo('Select a stop','Choose a row to remove.')
        idx=int(selection[0])
        if idx==0: return messagebox.showwarning('Depot required','The depot cannot be removed. You can update it.')
        del self.stops[idx]
        self.refresh_table();self.clear_result()

    def load_sample(self):
        self.stops=list(SAMPLE);self.refresh_table();self.clear_result()

    def run_optimization(self):
        try:
            self.result=optimize(self.stops)
        except ValueError as e: return messagebox.showerror('Cannot optimize',str(e))
        r=self.result
        savings=r['original_km']-r['optimized_km']
        self.summary.config(text=f"Original: {r['original_km']:.2f} km    |    Optimized: {r['optimized_km']:.2f} km    |    Saved: {savings:.2f} km")
        names=[self.stops[0][0]]+[self.stops[i][0] for i in r['optimized_order']]+[self.stops[0][0]]
        self.sequence.config(text='  →  '.join(names),wraplength=max(self.canvas.winfo_width()-35,280),justify='left')
        self.draw_map()

    def draw_map(self):
        if not hasattr(self,'canvas'):return
        c=self.canvas;c.delete('all')
        w=max(300,c.winfo_width());h=max(200,c.winfo_height())
        for gx in range(25,w,35): c.create_line(gx,0,gx,h,fill='#eaf0f8')
        for gy in range(25,h,35): c.create_line(0,gy,w,gy,fill='#eaf0f8')
        if not self.stops:return
        xs=[p[1] for p in self.stops];ys=[p[2] for p in self.stops]
        dx=max(max(xs)-min(xs),1);dy=max(max(ys)-min(ys),1)
        scale=min((w-120)/dx,(h-100)/dy)
        coords=[(60+(x-min(xs))*scale,h-55-(y-min(ys))*scale) for _,x,y in self.stops]
        if self.result:
            path=[0]+self.result['optimized_order']+[0]
            for a,b in zip(path,path[1:]):
                c.create_line(*coords[a],*coords[b],fill=BLUE,width=3,arrow=tk.LAST,arrowshape=(10,12,5))
        for i,(name,x,y) in enumerate(self.stops):
            px,py=coords[i]
            col='#16a34a' if i==0 else BLUE
            c.create_oval(px-7,py-7,px+7,py+7,fill=col,outline='white',width=2)
            c.create_text(px,py-17,text=name[:18],font=('Segoe UI',9,'bold'),fill=NAVY)
            c.create_text(px,py,text='D' if i==0 else str(i),font=('Segoe UI',7,'bold'),fill='white')

    def export_csv(self):
        if self.result is None:
            return messagebox.showinfo('Generate a route first','Click Optimize route before exporting.')
        filename=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV files','*.csv')],initialfile='delivery_route.csv')
        if not filename:return
        order=[0]+self.result['optimized_order']+[0]
        try:
            with open(filename,'w',newline='',encoding='utf-8-sig') as f:
                writer=csv.writer(f)
                writer.writerow(['Visit order','Location','X (km)','Y (km)'])
                for step,i in enumerate(order): writer.writerow([step,*self.stops[i]])
                writer.writerow([])
                writer.writerow(['Total round-trip distance (km)',f"{self.result['optimized_km']:.2f}"])
        except OSError as e: return messagebox.showerror('Export failed',str(e))
        messagebox.showinfo('Saved','Route exported successfully.')


if __name__=='__main__':
    root=tk.Tk()
    DeliveryApp(root)
    root.mainloop()
