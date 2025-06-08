from src.hello_world import hello_world


def test_hello_world() -> None:
    """Test that the hello_world function returns the expected greeting."""
    assert hello_world() == "Hello, World!"
