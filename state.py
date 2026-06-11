# state.py — decisão pura: dadas as contagens de rostos por quadro, liga/desliga o alerta.
class GuardianState:
    """Máquina de estados do guardião.

    Prioridade por quadro: UNKNOWN > KNOWN > (vazio = mantém estado / latch).
    Debounce: só troca de estado após `debounce_frames` quadros consecutivos
    concordando com o novo alvo (mata o flicker da detecção).
    """

    def __init__(self, debounce_frames=3, start_alert=False):
        self.debounce_frames = debounce_frames
        self.alert_active = start_alert
        self._pending = start_alert
        self._count = 0

    def update(self, known, unknown):
        if unknown > 0:
            target = True
        elif known > 0:
            target = False
        else:
            target = self.alert_active  # quadro vazio: latch no estado atual

        if target == self.alert_active:
            self._pending = target
            self._count = 0
            return self.alert_active

        if target == self._pending:
            self._count += 1
        else:
            self._pending = target
            self._count = 1

        if self._count >= self.debounce_frames:
            self.alert_active = target
            self._count = 0
        return self.alert_active
