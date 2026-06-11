# overlay.py — janela Tkinter fullscreen vermelha; polling de um callback bool.
import tkinter as tk
import config


class Overlay:
    def __init__(self, get_alert, poll_ms):
        self.get_alert = get_alert  # callable() -> bool
        self.poll_ms = poll_ms
        self.root = tk.Tk()
        self.root.title("Camera Guardian")
        self.root.configure(bg=config.ALERT_BG)
        self.label = tk.Label(
            self.root,
            text=config.ALERT_TEXT,
            fg=config.ALERT_FG,
            bg=config.ALERT_BG,
            font=("Helvetica", config.ALERT_FONT_SIZE, "bold"),
            wraplength=1,
        )
        self.label.pack(expand=True, fill="both")
        # ESC esconde manualmente (failsafe durante testes)
        self.root.bind("<Escape>", lambda e: self._hide())
        self.root.withdraw()
        self._visible = False

    def _show(self):
        self.root.deiconify()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.label.config(wraplength=self.root.winfo_screenwidth() - 80)
        self.root.lift()
        self._visible = True

    def _hide(self):
        self.root.withdraw()
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
