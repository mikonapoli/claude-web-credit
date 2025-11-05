"""Test that SpellLoader works with default package resource."""

from roguelike.data.spell_loader import SpellLoader


def test_spell_loader_default_uses_package_resource():
    """SpellLoader() with no args loads from package resource."""
    loader = SpellLoader()

    # Should load spells from package
    assert len(loader.spells) > 0
    assert "magic_missile" in loader.spells
    assert "fireball" in loader.spells


if __name__ == "__main__":
    test_spell_loader_default_uses_package_resource()
    print("✓ Default SpellLoader() works with packaged resource!")
