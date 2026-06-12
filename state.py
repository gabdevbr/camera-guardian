# state.py — decisão pura: dadas as contagens de rostos por quadro, liga/desliga o alerta.
class GuardianState:
    """Máquina de estados do guardião.

    Entradas por quadro (vindas do detector, já com liveness aplicado):
      - `known`   = dono VIVO presente? (1/0)
      - `unknown` = ameaça presente? desconhecido OU dono-não-vivo/foto (1/0)

    Prioridade: KNOWN (dono vivo) > UNKNOWN (ameaça) > (vazio = mantém / latch).
    Ou seja: se o dono vivo está na tela, NÃO dispara — nem com gente passando
    atrás. O alerta só sobe quando o dono está ausente e há ameaça.

    Debounce: só troca de estado após `debounce_frames` quadros consecutivos
    concordando com o novo alvo (mata o flicker da detecção).
    """

    def __init__(self, debounce_frames=3, start_alert=False):
        self.debounce_frames = debounce_frames
        self.alert_active = start_alert
        self._pending = start_alert
        self._count = 0

    def update(self, known, unknown):
        if known > 0:
            target = False        # dono vivo presente -> limpa (prioridade máxima)
        elif unknown > 0:
            target = True         # dono ausente + ameaça -> alerta
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
