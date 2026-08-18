import socket

from foxhubclaw.desktop import choose_port


def test_choose_port_falls_back_when_preferred_is_busy():
    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.bind(("127.0.0.1", 0))
    busy = int(blocker.getsockname()[1])
    try:
        chosen = choose_port("127.0.0.1", busy)
        assert chosen != busy
        assert chosen > 0
    finally:
        blocker.close()
