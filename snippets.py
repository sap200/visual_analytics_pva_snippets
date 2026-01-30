# Incident tracking histogram
# The scheduler is controlled using progressivis aio class
# aio class returns control and takes control from the scheduler at certain time interval
# data is received through input_module and inpult_slots combination with data function.
# Most of the things are sorted 

# progressivis-snippet
from ipyprogressivis.widgets.chaining.custom import register_snippet, SnippetResult
from ipywidgets import Output, VBox, HBox, Dropdown, IntSlider, Label
import plotly.graph_objects as go
import progressivis.core.aio as aio
import re

@register_snippet
def progressive_incident_histogram(input_module, input_slot, columns):
    table = input_module.output[input_slot].data()
    out = Output()

    # Create persistent state if not already
    if not hasattr(progressive_incident_histogram, "_state"):
        fig = go.FigureWidget(go.Bar(x=[], y=[], marker_color='lightgreen'))

        state = {
            "cursor": 0,
            "incident_latest_state": {},    # Latest state per incident
            "incident_latest_priority": {}, # Latest priority per incident
            "counts": {},                   # Counts for visualization
            "out": out,
            "fig": fig,
            "running": True,
            "filters": {"state": "All", "priority": 5},
            "unique_states": set()
        }
        progressive_incident_histogram._state = state

        # ---- Create interactive widgets ----
        state_dropdown = Dropdown(options=["All"], value="All", description="State:")
        priority_slider = IntSlider(value=5, min=1, max=5, step=1, description="Max Priority:")
        label_info = Label(value="Filtering: All / Priority <= 5")

        controls = VBox([HBox([state_dropdown, priority_slider]), label_info])

        # ---- Function to update histogram based on filters ----
        def update_histogram():
            filtered_counts = {}
            for inc, st in state["incident_latest_state"].items():
                pr = state["incident_latest_priority"].get(inc, 5)
                if state["filters"]["state"] != "All" and st != state["filters"]["state"]:
                    continue
                if pr > state["filters"]["priority"]:
                    continue
                filtered_counts[st] = filtered_counts.get(st, 0) + 1

            # Ensure all known states are shown (even zero)
            for s in state["unique_states"]:
                if s not in filtered_counts:
                    filtered_counts[s] = 0

            # Sort by state name
            filtered_counts = dict(sorted(filtered_counts.items()))
            state["fig"].data[0].x = list(filtered_counts.keys())
            state["fig"].data[0].y = list(filtered_counts.values())

        # ---- Widget callbacks ----
        def on_state_change(change):
            state["filters"]["state"] = change["new"]
            label_info.value = f"Filtering: {state['filters']['state']} / Priority <= {state['filters']['priority']}"
            update_histogram()

        def on_priority_change(change):
            state["filters"]["priority"] = change["new"]
            label_info.value = f"Filtering: {state['filters']['state']} / Priority <= {state['filters']['priority']}"
            update_histogram()

        state_dropdown.observe(on_state_change, names="value")
        priority_slider.observe(on_priority_change, names="value")

        # ---- Display output ----
        display(out)
        with out:
            display(controls)
            display(fig)

        # ---- Async progressive processing ----
        async def process_rows():
            batch_size = 5
            while state["cursor"] < table.nrow:
                start = state["cursor"]
                end = min(start + batch_size, table.nrow)
                for i in range(start, end):
                    row = table.row(i)
                    inc = row["number"]
                    st = row["incident_state"]
                    pr = row.get("priority", 5)
                    if isinstance(pr, str):
                        m = re.search(r"\d+", pr)
                        pr = int(m.group(0)) if m else 5

                    # Update latest state and priority
                    prev_state = state["incident_latest_state"].get(inc)
                    state["incident_latest_state"][inc] = st
                    state["incident_latest_priority"][inc] = pr

                    # Track all unique states
                    if st not in state["unique_states"]:
                        state["unique_states"].add(st)
                        state_dropdown.options = ["All"] + sorted(state["unique_states"])

                state["cursor"] = end
                update_histogram()  # Update histogram live
                await aio.sleep(0.05)  # Yield control

            state["running"] = False

        aio.create_task(process_rows())

    return SnippetResult(
        output_module=input_module,
        output_slot=input_slot,
        widget=out
    )
