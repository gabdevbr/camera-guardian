from liveness import eye_aspect_ratio, BlinkTracker


# ---- eye_aspect_ratio ----

OPEN_EYE = [(0, 0), (1, 1), (4, 1), (6, 0), (4, -1), (1, -1)]    # EAR ~0.33
CLOSED_EYE = [(0, 0), (1, 0.2), (4, 0.2), (6, 0), (4, -0.2), (1, -0.2)]  # EAR ~0.07


def test_ear_olho_aberto_alto():
    assert eye_aspect_ratio(OPEN_EYE) > 0.30


def test_ear_olho_fechado_baixo():
    assert eye_aspect_ratio(CLOSED_EYE) < 0.10


def test_ear_degenerado_nao_explode():
    flat = [(0, 0), (1, 0), (2, 0), (0, 0), (2, 0), (1, 0)]  # horiz = 0
    assert eye_aspect_ratio(flat) == 0.0


# ---- BlinkTracker ----

def tracker(window=3, reset=2):
    return BlinkTracker(ear_threshold=0.21, consec_frames=1,
                        window_frames=window, reset_absent_frames=reset)


def test_comeca_nao_vivo():
    assert tracker().is_live() is False


def test_olho_sempre_aberto_nunca_fica_vivo():
    t = tracker()
    for _ in range(10):
        assert t.update(0.30) is False


def test_piscada_torna_vivo():
    t = tracker()
    assert t.update(0.30) is False   # aberto
    assert t.update(0.05) is False   # fechado
    assert t.update(0.30) is True    # abriu -> piscou -> vivo


def test_vivacidade_expira_apos_janela():
    t = tracker(window=3)
    t.update(0.30); t.update(0.05); t.update(0.30)  # piscou (since_blink=1)
    assert t.update(0.30) is True    # 2
    assert t.update(0.30) is True    # 3
    assert t.update(0.30) is False   # 4 > janela


def test_ausencia_zera_vivacidade():
    t = tracker(window=10, reset=2)
    t.update(0.30); t.update(0.05); t.update(0.30)  # vivo
    assert t.update(None) is True    # ausente 1 (ainda dentro da janela)
    assert t.update(None) is False   # ausente 2 >= reset -> zera
