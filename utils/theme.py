import plotly.io as pio
import plotly.graph_objects as go

# A muted, professional palette — sand/gold/teal tones nod to Dubai without being kitschy.
# Used consistently across every chart so the same category (e.g. a property type)
# reads the same color on every page.
PALETTE = [
    "#0E4C63",  # deep teal
    "#C9A24B",  # gold/sand
    "#4C8577",  # muted sage
    "#8C5E3C",  # warm brown
    "#3A6B8A",  # steel blue
    "#B0763B",  # burnt sand
    "#5C8A8A",  # dusty teal
    "#A6784C",  # clay
]

_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        colorway=PALETTE,
        font=dict(family="Helvetica, Arial, sans-serif", size=13, color="#2B2B2B"),
        plot_bgcolor="#FAFAF8",
        paper_bgcolor="#FFFFFF",
        title=dict(font=dict(size=17, color="#1A1A1A")),
        xaxis=dict(gridcolor="#E8E6E1", zerolinecolor="#E8E6E1"),
        yaxis=dict(gridcolor="#E8E6E1", zerolinecolor="#E8E6E1"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
)
pio.templates["dubai_dashboard"] = _TEMPLATE


def apply_theme(fig):
    """Apply the shared dashboard theme to a Plotly figure. Call right before st.plotly_chart()."""
    fig.update_layout(template="dubai_dashboard")
    return fig