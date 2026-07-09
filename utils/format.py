def format_aed(val) -> str:
    """Abbreviate AED values consistently everywhere (K/M/B) so metrics never truncate."""
    if val is None:
        return "AED 0"
    val = float(val)
    if val >= 1_000_000_000:
        return f"AED {val / 1_000_000_000:.2f}B"
    if val >= 1_000_000:
        return f"AED {val / 1_000_000:.2f}M"
    if val >= 1_000:
        return f"AED {val / 1_000:.1f}K"
    return f"AED {val:,.0f}"