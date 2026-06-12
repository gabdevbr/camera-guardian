# overlay.py — alerta vermelho fullscreen em TODOS os monitores; polling de um callback bool.
import tkinter as tk
import config

try:
    from screeninfo import get_monitors
except Exception:  # screeninfo ausente ou sem backend → cai pra tela única
    get_monitors = None


class Overlay:
    def __init__(self, get_alert, poll_ms):
        self.get_alert = get_alert  # callable() -> bool
        self.poll_ms = poll_ms
        self.root = tk.Tk()
        self.root.withdraw()  # root invisível; cada monitor é um Toplevel
        self.root.bind("<Escape>", lambda e: self._hide())
        self.windows = [self._make_window(geom) for geom in self._monitor_geometries()]
        self._visible = False

    def _monitor_geometries(self):
        """Lista de (w, h, x, y) por monitor. Cai pra tela primária se não der."""
        if get_monitors is not None:
            try:
                mons = get_monitors()
                if mons:
                    return [(m.width, m.height, m.x, m.y) for m in mons]
            except Exception:
                pass
        return [(self.root.winfo_screenwidth(), self.root.winfo_screenheight(), 0, 0)]

    def _make_window(self, geom):
        w, h, x, y = geom
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)          # sem barra de título
        win.geometry(f"{w}x{h}+{x}+{y}")    # posiciona no monitor certo
        win.configure(bg=config.ALERT_BG)
        win.attributes("-topmost", True)
        win.bind("<Escape>", lambda e: self._hide())
        tk.Label(
            win, text=config.ALERT_TEXT, fg=config.ALERT_FG, bg=config.ALERT_BG,
            font=("Helvetica", config.ALERT_FONT_SIZE, "bold"),
            wraplength=max(1, w - 80),
        ).pack(expand=True, fill="both")
        win.withdraw()
        return win

    def _show(self):
        for win in self.windows:
            win.deiconify()
            win.lift()
            win.attributes("-topmost", True)
        if self.windows:
            self.windows[0].focus_force()  # garante que o ESC funcione
        self._visible = True

    def _hide(self):
        for win in self.windows:
            win.withdraw()
        self._visible = False

    def _poll(self):
        alert = self.get_alert()
        if alert and not self._visible:
            self._show()
        elif not alert and self._visible:
            self._hide()
        self.root.after(self.poll_ms, self._poll)

    def run(self):
        self.root.after(self.poll_ms, self._poll)
        self.root.mainloop()
