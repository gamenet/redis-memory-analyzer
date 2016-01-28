import sys
import statistics

from rma.RmaApplication import RmaApplication

app = RmaApplication()
app.run({'host': '192.168.1.133', 'port': 6379, 'match': '*'})
