import altair as alt
from altair import Chart, datum


def plot_volume_window(df, window):
    base = (
        Chart(df)
        .mark_line(color="black", strokeWidth=1)
        .encode(
            x=alt.X("date:T").scale(domain=window).axis(title="Date"),
            y=alt.Y("flow").axis(title="Flow [cfs]").scale(domain=[0, df.flow.max()]),
        )
        .transform_filter(datum.metric == "flow")
    )

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

    return (base + rule + tex).interactive()