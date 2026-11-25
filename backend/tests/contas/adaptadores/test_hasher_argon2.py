from motoriz.contas.adaptadores.hasher_argon2 import HasherArgon2


def test_gerar_e_verificar():
    hasher = HasherArgon2()
    hash_ = hasher.gerar("senha-çom-acento-🚗")
    assert hash_.startswith("$argon2id$")
    assert hasher.verificar("senha-çom-acento-🚗", hash_) is True


def test_senha_errada():
    hasher = HasherArgon2()
    assert hasher.verificar("outra-senha", hasher.gerar("senha-correta")) is False


def test_hash_invalido():
    assert HasherArgon2().verificar("qualquer", "nao-e-um-hash") is False
