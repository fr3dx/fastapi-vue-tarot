from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from tortoise.contrib.fastapi import register_tortoise
from admin.settings import settings
from models.admin_user import AdminUser
from admin.resources.tarot_card import TarotCardResource

app = FastAPI()
app.mount("/admin", admin_app)

@app.on_event("startup")
async def startup():
    await admin_app.configure(
        logo_url="https://yourlogo.png",
        template_folders=[],
        providers=[
            UsernamePasswordProvider(
                admin_model=AdminUser,
                login_logo_url="https://yourlogo.png"
            )
        ],
        resources=[TarotCardResource]
    )

register_tortoise(
    app,
    db_url=settings.DATABASE_URL,
    modules={"models": ["models.admin_user", "models.tarot_card"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
