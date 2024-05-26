from object_gay.utils import create_app

from .zipline import app as zipline_app

app = create_app()
app.mount("/zipline", zipline_app)
