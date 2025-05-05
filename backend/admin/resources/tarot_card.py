from fastapi_admin.resources import Model as AdminModel
from fastapi_admin.widgets import displays, inputs
from models.db_models import TarotCard

class TarotCardResource(AdminModel):
    label = "Tarot Cards"
    model = TarotCard
    page_size = 20

    filters = [
        "name",
    ]

    fields = [
        "id",
        displays.Input(display="Name"),
        inputs.Text(name="name", input_type="text"),
        displays.Input(display="Meaning"),
        inputs.TextArea(name="description"),
    ]
