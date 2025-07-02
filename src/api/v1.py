from ninja import NinjaAPI
from contacts.views import router as contacts_router

api = NinjaAPI()

api.add_router('', contacts_router)
