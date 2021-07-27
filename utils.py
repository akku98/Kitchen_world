# Random id generator

from .models import OrdersModel
import string
import random

def IdGenerator(size = 6,char = string.ascii_uppercase + string.digits):
    the_id =  "".join(random.choice(char) for x in range(size))
    try:
        order = OrdersModel.objects.get(ord_id = the_id)    # if the_id exists , again create the new id
        IdGenerator()
    except OrdersModel.DoesNotExist:
        return the_id                   # if ord_id != the_id then return the generated id
