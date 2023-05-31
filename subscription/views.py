import json
import stripe
import djstripe
from djstripe.models import Product, Price, Plan
from .models import *
from .serializers import *
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    GenericAPIView,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)

class PlansListApiView(GenericAPIView):
    
    def post(self, request, format=None):
        arr = []
        product = Product.objects.filter()
        for i in product:
            data = {}
            data['id'] = i.id
            for j in Plan.objects.filter(product=i.id):
                data['price'] = j.amount
                data['plan_id'] = j.id
            # for k in i.plan_set.all:
            #     print(k)
            data['name'] = i.name
            data['description'] = i.description
            arr.append(data)
        return Response({"Response": arr})
    
class SubscriptionUserApiView(GenericAPIView):
    
    def post(self, request, format=None):
        data = json.loads(request.body)
        payment_method = data['payment_method']
        stripe.api_key = djstripe.settings.STRIPE_SECRET_KEY

        payment_method_obj = stripe.PaymentMethod.retrieve(payment_method)
        djstripe.models.PaymentMethod.sync_from_stripe_data(payment_method_obj)


        try:
            # This creates a new Customer and attaches the PaymentMethod in one API call.
            customer = stripe.Customer.create(
                payment_method=payment_method,
                email=request.user.email,
                invoice_settings={
                    'default_payment_method': payment_method
                }
            )

            djstripe_customer = djstripe.models.Customer.sync_from_stripe_data(customer)
            # request.user.customer = djstripe_customer
            

            # At this point, associate the ID of the Customer object with your
            # own internal representation of a customer, if you have one.
            # print(customer)

            # Subscribe the user to the subscription created
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[
                    {
                        "price": data["price_id"],
                    },
                ],
                expand=["latest_invoice.payment_intent"]
            )

            djstripe_subscription = djstripe.models.Subscription.sync_from_stripe_data(subscription)

            # request.user.subscription = djstripe_subscription
            # request.user.save()
            SubscriptionPlans.objects.create(organisation=request.user, plan=djstripe_subscription, customer=djstripe_customer)

            return Response(subscription)
        except Exception as e:
            return Response({'error': (e.args[0])}, status =403)


class SubscriptionDeleteApiView(GenericAPIView):
    
    def post(self, request, format=None):
        # sub_id = request.user.subscription.id
        sub_id = SubscriptionPlans.objects.filter(organisation=request.user)

        stripe.api_key = djstripe.settings.STRIPE_SECRET_KEY

        try:
            stripe.Subscription.delete(sub_id)
            return Response({'Response': "Successfully Deleted"})
        except Exception as e:
            return Response({'error': (e.args[0])}, status =403)