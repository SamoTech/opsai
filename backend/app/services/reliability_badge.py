def generate_badge_svg(score: float) -> str:
    """Generate a shields.io-style SVG badge for reliability score."""
    if score >= 80:
        color = "#22c55e"  # green
        label_color = "#166534"
    elif score >= 60:
        color = "#eab308"  # yellow
        label_color = "#713f12"
    else:
        color = "#ef4444"  # red
        label_color = "#7f1d1d"

    score_text = f"{score:.0f}/100"
    width = 160
    label_width = 80
    value_width = 80

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" role="img">
  <title>OpsAI Reliability: {score_text}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <rect rx="3" width="{width}" height="20" fill="#555"/>
  <rect rx="3" x="{label_width}" width="{value_width}" height="20" fill="{color}"/>
  <rect x="{label_width}" width="4" height="20" fill="{color}"/>
  <rect rx="3" width="{width}" height="20" fill="url(#s)"/>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{label_width // 2}" y="15" fill="#010101" fill-opacity=".3">OpsAI</text>
    <text x="{label_width // 2}" y="14">OpsAI</text>
    <text x="{label_width + value_width // 2}" y="15" fill="#010101" fill-opacity=".3">{score_text}</text>
    <text x="{label_width + value_width // 2}" y="14">{score_text}</text>
  </g>
</svg>"""
