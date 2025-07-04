from ninja import NinjaAPI

from contacts.views import router as contacts_router

api_v1 = NinjaAPI()

api_v1.add_router('v1/', contacts_router)
