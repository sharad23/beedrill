from rest_framework import routers
from experiment import views

router = routers.SimpleRouter()

router.register(r"api", views.TestViewSet)
urlpatterns = router.urls
