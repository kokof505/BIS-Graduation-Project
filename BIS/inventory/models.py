from django.db import models
from sole_proprietorship.models import Accounts
from django.contrib.auth import get_user_model
from suppliers.models import Supplier
from django.utils.translation import gettext as _
from  django.core.validators import MaxValueValidator
from django.utils import timezone
from django.db.models import Sum , ExpressionWrapper , F , FloatField
import calendar
from django.core.exceptions import ValidationError
# Create your models here.
class PaymentSalesTerm(models.Model):
    class Term(models.IntegerChoices):
        CASH = 0 , _("Pay CASH")
        ON_DEMAND = 1 , _("Cash On Demand")
        DAYS = 2, _("Due in number of days")
        END_OF_MONTH = 3,_("Due at the end of month")
        NEXT_MONTH = 4,_("Due on the next Month")
        OTHER = 5, _("let me specify the due date DD-MM-YYY")


    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    config = models.CharField(
        max_length=100,
        help_text="Specify name for this setting"
        )
    terms = models.IntegerField(choices=Term.choices , default=Term.CASH , blank=False)
    num_of_days_due = models.PositiveSmallIntegerField(
        help_text="in case of you want to specify number of days due"
    )
    discount_in_days = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(32)] ,
        null = True,
        blank = True
    )
    discount_percentage = models.FloatField(
        help_text="Enter discount like this 5%>>will be  5 not 0.05",
  
    )
    general_ledeger_account = models.ForeignKey(Accounts,on_delete=models.CASCADE)

    def __str__(self):
        return self.config

class Inventory(models.Model):
    """
    Create Inventory table in db.
    we will use this table to save inventory item and related account inventory for this item 
    i can use just one inventrory account for all item in inventory but i created one - to many relation 
    in order to make it's dynamic in other meaning we can have many inventory account so there is FK
    """
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    item_name = models.CharField(max_length=250)
    description = models.TextField(
        null= True,
        blank= True
    )
    general_ledeger_account = models.ForeignKey(Accounts,on_delete=models.CASCADE)

    def __str__(self):
        return self.item_name


def inventory_imag_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'inventory/inventory_imgs/user_{0}/{3}/{2}{1}'.format(instance.inventory.owner,
     filename ,
     timezone.now() , 
     instance.inventory.item_name
      )

class InventoryImag(models.Model):
    """
    this is table hold images for the inventory item each inventory can has many image
    """
    class Meta:
        verbose_name = 'Inventory Image'
        verbose_name_plural = 'Inventory Images'

    inventory  = models.ForeignKey(Inventory , on_delete=models.CASCADE , related_name="imgs" )
    img = models.ImageField(upload_to=inventory_imag_directory_path,
                                null=True,
                                blank=True,
                                editable=True,
                                help_text="Inventory image")
    
    def __str__(self):
        return f"img:{self.inventory.item_name}"



# class PurchaseManager(models.Manager):
    

class PurchaseInventory(models.Model):
    """
    Note freight in cost which inccure when you purchase your inventory will charge only on the first
    form inventory in formset
    """
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    # a unique identifyer for youe purchase tansaction
    num = models.IntegerField()
    purchase_date = models.DateTimeField()
    due_date = models.DateField(
        help_text="optional if you want to specify it by yourself",
        null = True ,
        blank = True,
    )

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    term = models.ForeignKey(PaymentSalesTerm, on_delete=models.CASCADE)
    frieght_in = models.FloatField(default=0)

    def check_status(self):
        """
        Check if this invoice PAID or UNPAID
        """
        if self.term.terms == 0:
            return "PAID"
        else:
            return  "UNPAID"

    
    def check_due_date(self):
        """
        retrun due date if user don't specify it's directly and used terms instead
        """
        if self.due_date:
            return self.due_date
        else:
            # Due in number of days
            if self.term.terms == PaymentSalesTerm.Term.DAYS.value:
                return self.purchase_date + timezone.timedelta(days=self.term.num_of_days_due)
            elif self.term.terms == PaymentSalesTerm.Term.END_OF_MONTH.value:
                return timezone.datetime(
                    year = self.purchase_date.year , 
                    month = self.purchase_date.month , 
                    day = calendar.monthrange(
                            year= self.purchase_date.year ,
                            month = self.purchase_date.month
                    )[1]
                )
            # we mean by next month ex purchase date was feb-02-2021 so due date march-02-2021
            elif self.term.terms == PaymentSalesTerm.Term.NEXT_MONTH.value:
                if self.purchase_date.month == 12:
                    return timezone.datetime(
                            year = self.purchase_date.year + 1 , 
                            month = 1 , 
                            day = self.purchase_date.day
                )
                else:
                    return timezone.datetime(
                        year = self.purchase_date.year , 
                        month = self.purchase_date.month + 1, 
                        day = self.purchase_date.day
                    )





    @property
    def num_cost_of_returned_inventory(self) -> tuple:
        """
        return a tuble of  total number of returned and it's cost
        # take into account if we return inventory so we accumulate this cost
        # for now we do it on reqular python insted of db for simplicity by in 
        # future should do in database level for speed and performance
        """
        cost_of_returned_inventory = 0
        total_returned = 0
        for inventory_price in self.inventoryprice_set.all():
            cost_per_unit = inventory_price.cost_per_unit
            for inventory_return in inventory_price.inventoryreturn_set.all():
                total_cost = inventory_return.num_returned * cost_per_unit
                total_returned += inventory_return.num_returned
                cost_of_returned_inventory += total_cost
        return total_returned , cost_of_returned_inventory

    @property
    def total_amount(self) -> float:
        """amount of purchase whether on account or paid cash"""
        # reurn dict for total amount of purchases
        query = self.inventoryprice_set.annotate(
                    total_cost=ExpressionWrapper(
                        F("cost_per_unit")*F("number_of_unit"), output_field=FloatField()
                        )).aggregate(total_amount=Sum("total_cost"))

        
        return query.get("total_amount" , 0)


    
    # we will add in the future the address for the supplier and the ship address


class InventoryPrice(models.Model):
    """
    Create InventoryPrice table in db.
    as you know each inventory can has multiple price so there are accounting method such as FIFO,LIFO,Moving Average
    in order to solve this proble there are one-To-Many Relationship (Inventort >> InventoryPtie)
    so when i record transaction:

    Model Inventory: 
        Product X
    
    Model InventoryPrice:
        purchase one time on 01-jan-2021 , 10 units with price 10 per unit so total cost = 100
        purchase second time the same product on 01-mar-2021, 10 units with price 12 so total cost 120
    
    Overview:
        Total cost now = 100 + 120 = 220 
        Number of unit = 20

    you will have the choice to sell the inventory who cost you 10 first or the inventory who cost you 12 first
    by this way we will avoide the headache of FIFO ,LIFO when we sell the inventory to the customer so you have
    the choice and keep our Transaction clean when we track the cost
    """
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    cost_per_unit = models.FloatField()
    number_of_unit = models.PositiveIntegerField()
    purchase_inventory = models.ForeignKey(PurchaseInventory, on_delete=models.CASCADE)

    @property
    def total_cost(self):
        return self.cost_per_unit * self.number_of_unit

    def __str__(self):
        return f"{self.inventory.item_name}:{self.cost_per_unit}/unit"


class InventoryReturn(models.Model):
    """
        Purchase Return Model
    """
    inventory_price = models.ForeignKey(InventoryPrice, on_delete=models.CASCADE)
    date = models.DateField()
    num_returned = models.PositiveIntegerField()


    def __str__(self):
        return f"return {self.num_returned} of {self.inventory_price.inventory.item_name}"