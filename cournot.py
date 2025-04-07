import tkinter as tk
from tkinter import ttk

import sympy
import numpy as np
import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class CournotApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Cournot Competition Interactive App")

        ################################################################
        # 1) define variables
        ################################################################
        self.q1_sym, self.q2_sym = sympy.symbols("q1 q2", real=True, nonnegative=True)

        # Default linear best responses
        self.default_br1_text = "(100 - q2)/2"
        self.default_br2_text = "(100 - q1)/2"


        # Scenario choice
        self.scenario_var = tk.StringVar(value="Cournot")

        # Toggles for iso-profit lines and cartel shading
        self.show_iso_profit_var = tk.BooleanVar(value=True)
        self.show_cartel_var = tk.BooleanVar(value=True)

        # Slider to pick how many iso-profit contours to show
        self.iso_num_var = tk.IntVar(value=3)  # e.g. 3 lines per firm

        # Store Sympy expressions for best-responses
        self.br1_expr = None
        self.br2_expr = None

        # Animation / iterative best-response
        self.animation_running = False
        self.animation_steps = []
        self.animation_index = 0

        ################################################################
        # 2) build the tkinter gui
        ################################################################

        # ========== top frame: scenario, toggles, animation, reset ==========
        top_frame = tk.Frame(self.master)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(top_frame, text="Scenario:").pack(side=tk.LEFT)
        scenario_menu = ttk.OptionMenu(
            top_frame,
            self.scenario_var,
            "Cournot",
            "Cournot",
            "Stackelberg (Firm 1 leads)",
            "Stackelberg (Firm 2 leads)"
        )
        scenario_menu.pack(side=tk.LEFT)
        self.scenario_var.trace_add("write", self.on_scenario_change)

        iso_check = ttk.Checkbutton(
            top_frame, text="Show Iso-Profit",
            variable=self.show_iso_profit_var, command=self.update_plot
        )
        iso_check.pack(side=tk.LEFT, padx=5)

        cartel_check = ttk.Checkbutton(
            top_frame, text="Show Potential Gains from Cooperation",
            variable=self.show_cartel_var, command=self.update_plot
        )
        cartel_check.pack(side=tk.LEFT, padx=5)

        anim_button = ttk.Button(top_frame, text="Animate", command=self.toggle_animation)
        anim_button.pack(side=tk.LEFT, padx=5)

        reset_button = ttk.Button(top_frame, text="Reset", command=self.reset_app)
        reset_button.pack(side=tk.LEFT, padx=5)

        # ========== Middle Frame: text inputs, sliders ==========
        middle_frame = tk.Frame(self.master)
        middle_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(middle_frame, text="Firm 1's BR (q1 as function of q2):").pack(anchor=tk.W)
        self.br1_entry = tk.Entry(middle_frame, width=30)
        self.br1_entry.pack(padx=5, pady=2)
        self.br1_entry.insert(0, self.default_br1_text)

        tk.Label(middle_frame, text="Firm 2's BR (q2 as function of q1):").pack(anchor=tk.W)
        self.br2_entry = tk.Entry(middle_frame, width=30)
        self.br2_entry.pack(padx=5, pady=2)
        self.br2_entry.insert(0, self.default_br2_text)

        update_br_button = ttk.Button(middle_frame, text="Update BR Functions", command=self.on_br_text_update)
        update_br_button.pack(pady=5)


        iso_frame = ttk.LabelFrame(middle_frame, text="Iso-Profit Lines")
        iso_frame.pack(padx=5, pady=5, fill=tk.X)

        tk.Label(iso_frame, text="Number of iso-lines for each firm:").pack()
        iso_scale = tk.Scale(iso_frame, from_=1, to=7, resolution=1, orient=tk.HORIZONTAL,
                             variable=self.iso_num_var, command=lambda e: self.update_plot())
        iso_scale.pack(fill=tk.X)

        # ==========  plot frame
        plot_frame = tk.Frame(self.master)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Parse defaults
        self.on_br_text_update()
        self.update_plot()

    ################################################################
    # parsing
    ################################################################
    def on_br_text_update(self):
        txt1 = self.br1_entry.get().strip()
        txt2 = self.br2_entry.get().strip()
        try:
            self.br1_expr = sympy.sympify(txt1, {"q2": self.q2_sym})
            self.br2_expr = sympy.sympify(txt2, {"q1": self.q1_sym})
        except sympy.SympifyError:
            # revert to default
            self.br1_expr = sympy.sympify(self.default_br1_text, {"q2": self.q2_sym})
            self.br2_expr = sympy.sympify(self.default_br2_text, {"q1": self.q1_sym})

        self.update_plot()


    def on_scenario_change(self, *args):
        self.update_plot()

    ################################################################
    # animation
    ################################################################
    def toggle_animation(self):
        if not self.animation_running:
            self.animation_running = True
            self.start_animation()
        else:
            self.animation_running = False

    def start_animation(self):
        self.build_cobweb_path()
        self.animation_index = 0
        self.animate_step()

    def build_cobweb_path(self):
        # Start from (5,0), do ~10 updates
        q1_curr = 5.0
        q2_curr = 0.0
        steps = [(q1_curr, q2_curr)]
        for _ in range(10):
            q1_next = self.evaluate_br1(q2_curr)
            steps.append((q1_next, q2_curr))
            q2_next = self.evaluate_br2(q1_next)
            steps.append((q1_next, q2_next))
            q1_curr, q2_curr = q1_next, q2_next
        self.animation_steps = steps

    def animate_step(self):
        if not self.animation_running:
            return
        if self.animation_index >= len(self.animation_steps) - 1:
            self.animation_running = False
            return

        x_old, y_old = self.animation_steps[self.animation_index]
        x_new, y_new = self.animation_steps[self.animation_index + 1]

        # Draw an arrow with a subdued color
        self.ax.arrow(
            x_old, y_old,
            x_new - x_old, y_new - y_old,
            length_includes_head=True,
            head_width=0.5,
            color="darkgoldenrod"  # more subtle arrow
        )
        self.canvas.draw()

        self.animation_index += 1
        self.master.after(700, self.animate_step)

    ################################################################
    # evaluate best responses
    ################################################################
    def evaluate_br1(self, q2_val):
        if self.br1_expr is None:
            return 0.0
        return float(self.br1_expr.subs(self.q2_sym, q2_val))

    def evaluate_br2(self, q1_val):
        if self.br2_expr is None:
            return 0.0
        return float(self.br2_expr.subs(self.q1_sym, q1_val))

    ################################################################
    # reset
    ################################################################
    def reset_app(self):
        self.br1_entry.delete(0, tk.END)
        self.br1_entry.insert(0, self.default_br1_text)
        self.br2_entry.delete(0, tk.END)
        self.br2_entry.insert(0, self.default_br2_text)

        self.a1.set(100.0)
        self.b1.set(1.0)
        self.a2.set(100.0)
        self.b2.set(1.0)

        self.scenario_var.set("Cournot")

        self.show_iso_profit_var.set(False)
        self.show_cartel_var.set(False)
        self.iso_num_var.set(3)

        self.animation_running = False
        self.animation_steps = []
        self.animation_index = 0

        self.on_br_text_update()

    ################################################################
    # plot update
    ################################################################
    def update_plot(self):
        self.ax.clear()
        self.ax.set_xlabel("Firm 1 output (q1)")
        self.ax.set_ylabel("Firm 2 output (q2)")
        self.ax.set_xlim(0, 120)
        self.ax.set_ylim(0, 120)
        self.ax.set_title(self.scenario_var.get())

        # br curves with toned-down colors
        q_vals = np.linspace(0, 120, 200)

        # q2 = BR2(q1)
        br2_x, br2_y = [], []
        for q1v in q_vals:
            q2v = self.evaluate_br2(q1v)
            if 0 <= q2v < 99999:
                br2_x.append(q1v)
                br2_y.append(q2v)
        self.ax.plot(br2_x, br2_y, color="royalblue", linewidth=2, label="q2 = BR2(q1)")

        # q1 = BR1(q2)
        br1_x, br1_y = [], []
        for q2v in q_vals:
            q1v = self.evaluate_br1(q2v)
            if 0 <= q1v < 99999:
                br1_x.append(q1v)
                br1_y.append(q2v)
        self.ax.plot(br1_x, br1_y, color="darkorchid", linewidth=2, label="q1 = BR1(q2)")

        # solve scenario equilibrium
        scenario = self.scenario_var.get()
        eq_point = (None, None)
        if scenario == "Cournot":
            eq_point = self.solve_cournot()
        elif scenario == "Stackelberg (Firm 1 leads)":
            eq_point = self.solve_stackelberg(leader=1)
        elif scenario == "Stackelberg (Firm 2 leads)":
            eq_point = self.solve_stackelberg(leader=2)
        elif scenario == "Collusion":
            eq_point = self.solve_collusion()

        if eq_point is not None:
            q1_star, q2_star = eq_point
            if q1_star is not None and q2_star is not None:
                self.ax.plot([q1_star], [q2_star], 'o', color="red", markersize=8, label="Equilibrium")

        # iso-profit lines (no numeric labels)
        if self.show_iso_profit_var.get():
            self.draw_iso_profit_curves(label_curves=False)

        # cartel region
        if self.show_cartel_var.get():
            self.draw_cartel_region()

        self.ax.legend()
        self.canvas.draw()

    def solve_cournot(self):
        eqs = [
            sympy.Eq(self.q1_sym, self.br1_expr),
            sympy.Eq(self.q2_sym, self.br2_expr)
        ]
        try:
            sol = sympy.solve(eqs, [self.q1_sym, self.q2_sym], dict=True)
            if sol:
                s = sol[0]
                q1_star = float(s[self.q1_sym])
                q2_star = float(s[self.q2_sym])
                return (max(0, q1_star), max(0, q2_star))
        except:
            pass
        return (None, None)

    def solve_stackelberg(self, leader=1):
        if leader == 1:
            best_q1 = 0
            best_pi1 = -1e9
            for q1v in np.linspace(0, 120, 121):
                q2v = self.evaluate_br2(q1v)
                pi1 = self.simple_profit(1, q1v, q2v)
                if pi1 > best_pi1:
                    best_pi1 = pi1
                    best_q1 = q1v
            best_q2 = self.evaluate_br2(best_q1)
            return (best_q1, best_q2)
        else:
            best_q2 = 0
            best_pi2 = -1e9
            for q2v in np.linspace(0, 120, 121):
                q1v = self.evaluate_br1(q2v)
                pi2 = self.simple_profit(2, q1v, q2v)
                if pi2 > best_pi2:
                    best_pi2 = pi2
                    best_q2 = q2v
            best_q1 = self.evaluate_br1(best_q2)
            return (best_q1, best_q2)

    def solve_collusion(self):
        best_q1, best_q2 = 0, 0
        best_sum = -1e9
        for q1v in np.linspace(0, 120, 31):
            for q2v in np.linspace(0, 120, 31):
                pi_sum = self.simple_profit(1, q1v, q2v) + self.simple_profit(2, q1v, q2v)
                if pi_sum > best_sum:
                    best_sum = pi_sum
                    best_q1 = q1v
                    best_q2 = q2v
        return (best_q1, best_q2)

    def simple_profit(self, firm_id, q1v, q2v):
        price = max(0, 100 - (q1v + q2v))
        return price*q1v if firm_id == 1 else price*q2v

    def draw_iso_profit_curves(self, label_curves=False):
        eq_c = self.solve_cournot()
        if eq_c == (None, None):
            return
        qc1, qc2 = eq_c
        pi1_c = self.simple_profit(1, qc1, qc2)
        pi2_c = self.simple_profit(2, qc1, qc2)

        n = self.iso_num_var.get()
        levels_1 = np.linspace(0.5*pi1_c, 1.5*pi1_c, n)
        levels_2 = np.linspace(0.5*pi2_c, 1.5*pi2_c, n)

        X = np.linspace(0, 120, 60)
        Y = np.linspace(0, 120, 60)
        Xg, Yg = np.meshgrid(X, Y)
        pi1_vals = np.zeros_like(Xg)
        pi2_vals = np.zeros_like(Xg)

        for i in range(Xg.shape[0]):
            for j in range(Xg.shape[1]):
                q1v = Xg[i, j]
                q2v = Yg[i, j]
                pi1_vals[i, j] = self.simple_profit(1, q1v, q2v)
                pi2_vals[i, j] = self.simple_profit(2, q1v, q2v)

        cset1 = self.ax.contour(Xg, Yg, pi1_vals, levels=levels_1, colors="darkgreen", alpha=0.4)
        cset2 = self.ax.contour(Xg, Yg, pi2_vals, levels=levels_2, colors="darkorange", alpha=0.4)

        # if user wants numeric labels, we call clabel, but we skip it here
        # to remove the "F1=xxx" text on the curves.

    def draw_cartel_region(self):
        """
        shaded region where pi1 > pi1_c and pi2 > pi2_c.
        do a 0/1 mask and contourf for shading.
        """
        eq_c = self.solve_cournot()
        if eq_c == (None, None):
            return
        qc1, qc2 = eq_c
        pi1_c = self.simple_profit(1, qc1, qc2)
        pi2_c = self.simple_profit(2, qc1, qc2)

        X = np.linspace(0, 120, 60)
        Y = np.linspace(0, 120, 60)
        Xg, Yg = np.meshgrid(X, Y)

        mask = np.zeros_like(Xg)
        for i in range(Xg.shape[0]):
            for j in range(Xg.shape[1]):
                q1v = Xg[i, j]
                q2v = Yg[i, j]
                p1 = self.simple_profit(1, q1v, q2v)
                p2 = self.simple_profit(2, q1v, q2v)
                if p1 > pi1_c and p2 > pi2_c:
                    mask[i, j] = 1.0

        # shade the region where mask=1
        self.ax.contourf(Xg, Yg, mask, levels=[0.5, 1.5], alpha=0.4, colors=["khaki"], antialiased=True)
        # We still label it in the legend with an invisible handle:
        self.ax.plot([], [], color="khaki", label="Potential Gains from Cooperation")


###########################################################
# run the app, plus a short explanation of each equilibrium
###########################################################
if __name__ == "__main__":
    root = tk.Tk()
    app = CournotApp(root)
    root.mainloop()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Explanation of Equilibria:
    # 1) Cournot: Both firms choose output simultaneously, each believing
    #    the other's output is fixed. The equilibrium is where each firm's
    #    output equals its best response to the other's.
    #
    # 2) Stackelberg: One firm (the leader) chooses first, anticipating
    #    that the follower will best-respond. The leader's output is higher,
    #    and the follower's is lower, than in the Cournot solution.
    #
    # 3) Collusion: Firms coordinate to maximize their joint profits
    #    by restricting total output (like a monopoly). This generally
    #    yields lower output and higher price than Cournot, giving higher
    #    joint profit but also incentive for each to deviate.
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~