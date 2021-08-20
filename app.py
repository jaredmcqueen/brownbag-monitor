from datetime import datetime
from rich.console import Group
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
import time
from collections import deque, defaultdict
import requests

layout = Layout(name="main")

URL = "https://brownbag.mcqueensolutions.com"
BUFFER = deque(maxlen=25)


def gen_table():
    table = Table(title=f"last {len(BUFFER)} requests")
    table.add_column("timestamp")
    table.add_column("status")
    table.add_column("url")
    table.add_column("response")
    table.add_column("latency")

    lookup = {"200": "green", "502": "yellow", "404": "red"}
    for resp in BUFFER:
        highlight = lookup.get(resp.get("status"), "white")
        table.add_row(
            resp.get("timestamp"),
            f"[{highlight}]{resp.get('status')}",
            resp.get("url"),
            f"{resp.get('response')}",
            resp.get("time"),
        )

    return table


def percentages():
    results = defaultdict(int)
    for resp in BUFFER:
        results[resp.get("response")] += 1

    grid = Table(title="overall percentages")
    grid.add_column("response")
    grid.add_column("percentage")

    for k, v in results.items():
        grid.add_row(f"{k}", f"[magenta]{v / len(BUFFER) * 100:.2f}%")

    return grid


with Live(layout, refresh_per_second=4, screen=True):
    while True:
        try:
            resp = requests.get(URL, timeout=0.1)

            try:
                value = resp.json()
            except:
                value = None
            BUFFER.append(
                {
                    "timestamp": str(datetime.now().time()),
                    "status": str(resp.status_code),
                    "url": resp.url,
                    "response": str(value),
                    "time": f"{resp.elapsed.total_seconds() * 1000:.2f}",
                }
            )
        except:
            continue

        layout["main"].update(Group(percentages(), gen_table()))
        time.sleep(0.2)
