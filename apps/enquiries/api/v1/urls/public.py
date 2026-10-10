from django.urls import path

from apps.enquiries.api.v1 import views

app_name = "enquiries_public"

urlpatterns = [
    path("", views.EnquiryCreateView.as_view(), name="enquiry-create"),
    path("my/", views.MyEnquiriesView.as_view(), name="my-enquiries"),
]
