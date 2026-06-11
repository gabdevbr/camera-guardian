from state import GuardianState


def test_comeca_limpo():
    s = GuardianState(debounce_frames=3)
    assert s.alert_active is False


def test_desconhecido_dispara_apos_debounce():
    s = GuardianState(debounce_frames=3)
    assert s.update(known=0, unknown=1) is False   # quadro 1
    assert s.update(known=0, unknown=1) is False   # quadro 2
    assert s.update(known=0, unknown=1) is True    # quadro 3 -> dispara


def test_desconhecido_tem_prioridade_sobre_dono():
    s = GuardianState(debounce_frames=1)
    # dono + intruso no mesmo quadro -> intruso ganha
    assert s.update(known=1, unknown=1) is True


def test_dono_limpa_apos_debounce():
    s = GuardianState(debounce_frames=2, start_alert=True)
    assert s.update(known=1, unknown=0) is True    # quadro 1 (ainda alerta)
    assert s.update(known=1, unknown=0) is False   # quadro 2 -> limpa


def test_quadro_vazio_mantem_estado_de_alerta():
    s = GuardianState(debounce_frames=1, start_alert=True)
    # ninguém no quadro: continua vermelho até o dono voltar
    assert s.update(known=0, unknown=0) is True
    assert s.update(known=0, unknown=0) is True


def test_quadro_vazio_mantem_estado_limpo():
    s = GuardianState(debounce_frames=1, start_alert=False)
    assert s.update(known=0, unknown=0) is False


def test_quadro_isolado_nao_troca_estado():
    s = GuardianState(debounce_frames=3)
    s.update(known=0, unknown=1)   # 1 quadro rumo a alerta
    s.update(known=1, unknown=0)   # dono aparece -> reseta o streak
    assert s.update(known=0, unknown=1) is False  # recomeça do zero, não dispara


def test_intruso_sai_continua_vermelho_ate_dono_voltar():
    s = GuardianState(debounce_frames=1)
    assert s.update(known=0, unknown=1) is True    # intruso dispara
    assert s.update(known=0, unknown=0) is True    # intruso saiu, vazio -> latch
    assert s.update(known=1, unknown=0) is False   # dono volta -> limpa
