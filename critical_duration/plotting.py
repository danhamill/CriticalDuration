import altair as alt
from altair import Chart, datum

# Disable maximum row limit for Altair and enable browser rendering
alt.data_transformers.disable_max_rows()
alt.renderers.enable("browser")

def plot_volume_window(df, window):
    """
    Creates an interactive Altair plot to visualize flow data and n-day rolling volumes.

    Args:
        df (pd.DataFrame): DataFrame containing flow data and rolling volume metrics.
                           Expected columns:
                           - 'date': Timestamps for the data points.
                           - 'flow': Flow values (cfs).
                           - 'metric': Metric type (e.g., 'flow', '1-day', '2-day', etc.).
                           - 'text': Normalized volume values for display.
        window (Tuple[str, str]): Time window for the x-axis (start, end).

    Returns:
        alt.LayerChart: An interactive Altair chart combining:
                        - A line plot for flow data.
                        - Bar plots for n-day rolling volumes.
                        - Text annotations for normalized volume values.

    Notes:
        - The function uses Altair's `Chart` to create layered visualizations.
        - The `datum.metric` field is used to differentiate between flow data and rolling volumes.
        - The plot is interactive, allowing zooming and panning.
    """
    # Base line chart for flow data
    base = (
        Chart(df)
        .mark_line(color="black", strokeWidth=1)
        .encode(
            x=alt.X("date:T").scale(domain=window).axis(title="Date"),
            y=alt.Y("flow").axis(title="Flow [cfs]").scale(domain=[0, df.flow.max()]),
        )
        .transform_filter(datum.metric == "flow")
    )

    # Bar chart for n-day rolling volumes
    rule = (
        Chart(df)
        .mark_bar(height=2)
        .encode(
            x="min(date):T",
            x2="max(date):T",
            y=alt.Y("flow").scale(domain=[0, df.flow.max()]),
            color="metric",
        )
        .transform_filter(datum.metric != "flow")
    )

    # Text annotations for normalized volume values
    tex = (
        Chart(df)
        .mark_text(align="left", baseline="middle", dx=10)
        .encode(
            x="max(date):T",
            y=alt.Y(
                "flow",
                aggregate={"argmax": "date"},
            ).scale(domain=[0, df.flow.max()]),
            color="metric",
            text=alt.Text("text", format=".1%"),
        )
        .transform_filter(datum.metric != "flow")
    )

    # Combine all layers and make the chart interactive
    return (base + rule + tex).interactive()