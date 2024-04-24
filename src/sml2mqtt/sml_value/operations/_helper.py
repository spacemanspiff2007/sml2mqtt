
def format_period(period: int | float) -> str:
    period = period
    h = int(period) // 3600
    period %= 3600
    m = int(period) // 60
    s = period % 60

    parts = []
    for part, unit in ((h, 'hour'), (m, 'minute'), (s, 'second')):
        if not part:
            continue
        if part != 1:
            unit += 's'
        parts.append(f'{part:d} {unit:s}' if isinstance(part, int) else f'{part:.1f} {unit:s}')
    return ' '.join(parts)
