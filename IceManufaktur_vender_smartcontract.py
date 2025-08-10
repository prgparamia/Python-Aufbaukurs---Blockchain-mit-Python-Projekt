class IceToken:
    def __init__(self, initial_supply):
        self.total_supply = initial_supply
        self.price= {}

    def mint(self, account, amount):
        self.price[account] = self.price.get(account, 0) + amount
        self.total_supply += amount

    def balance_of(self, account):
        return self.price.get(account, 0)




class contractIceCreamDelivery:  

    def __init__(self, initial_stock: int, price_per_unit: int, factory_address: str,vender_address: str,inspector_address:str):
        self.stock = initial_stock
        self.price_per_unit = price_per_unit
        self.owner = factory_address
        self.vender=vender_address
        self.inspector=inspector_address

        
        self.payment_released=False
        self.delivery_confirmed_by_inspector=False
        
        
        self.contract_balance = 0
        self.events = []

    def _only_owner(self, caller):
        if caller != self.owner:
            raise PermissionError("Only owner can perform this action.")
        
    def _only_vender(self, caller):
        if caller != self.vender:
            raise PermissionError("Only vender can perform this action.")
        
    def _only_inspector(self, caller):
        if caller != self.inspector:
            raise PermissionError("Only inspector can perform this action.")



    def buy_ice_cream(self, quantity: int, temp_celsius: int, value_sent: int, vender_address: str):
        if temp_celsius >= 0:
            raise ValueError("Temperature must be below 0°C to proceed.")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if self.stock < quantity:
            raise ValueError("Not enough stock.")
        total_price = quantity * self.price_per_unit
        if value_sent != total_price:
            raise ValueError(f"Incorrect payment amount. Expected {total_price}, got {value_sent}.")

        self.stock -= quantity
        self.contract_balance += total_price

        self.events.append({
            "event": "IceCreamSold",
            "vendor": vender_address,
            "quantity": quantity,
            "total_price": total_price

        })

    

    def restock(self, amount: int, caller: str):
        self._only_owner(caller)
        self.stock += amount
        self.events.append({
            "event": "StockReplenished",
            "amount": amount
        })

    def update_price(self, new_price: int, caller: str):
        self._only_owner(caller)
        if new_price <= 0:
            raise ValueError("Price must be greater than zero.")
        self.price_per_unit = new_price
        self.events.append({
            "event": "PriceUpdated",
            "new_price": new_price
        })

    def refundVender(self,caller:str):
        self._only_vender(caller)
        if self.delivery_confirmed_by_inspector:
            raise Exception("Delivery already confimed: can not be refunded to the vender")
        if self.payment_released:
            raise Exception("Payment already releasd:con not be refunded to the vender")
        print(f"{self.contract_balance} released to {self.vender}  as refund ")
        self.payment_released=True
        self.contract_balance=0
    

    def withdraw(self, caller: str):
        self._only_owner(caller)
        withdrawn = self.contract_balance
        self.contract_balance = 0
        return withdrawn  # This simulates sending ETH to owner

    def get_stock(self):
        return self.stock
    
    def confirmDelivery(self,caller:str):
        self._only_inspector(caller)
        self.delivery_confirmed_by_inspector=True
        print("Delivery confirmed by inspector")
        
    def releasePayment(self,caller:str):
        self._only_inspector(caller)
        if  not self.delivery_confirmed_by_inspector:
            raise Exception("Delivery not confirmed by Inspector")

        if self.payment_released:
            raise Exception("Payment already released")
        
        self.payment_released=True
        print(f"{self.contract_balance} released to {self.owner}  as payment ")
        self.contract_balance=0

   

    def get_contract_balance(self):
        return self.contract_balance

    def get_event_log(self):
        return self.events
    


if __name__ == "__main__":
    owner = "0xOwner"
    buyer= "0xBuyer"
    veryfier="0xVeryfier"

    contract = contractIceCreamDelivery (initial_stock=100, price_per_unit=10, factory_address=owner,vender_address=buyer,inspector_address=veryfier)

    # User tries to buy ice cream in cold weather
    try:
        contract.buy_ice_cream(quantity=3, temp_celsius= -5, value_sent=30, vender_address=buyer)
        print("Purchase successful.")
    except Exception as e:
        print("Purchase failed:", e)

    # Owner restocks
    contract.restock(amount=50, caller=owner)

    # Owner changes price
    contract.update_price(new_price=15, caller=owner)

        
    # Refund vender

    contract.refundVender(caller=buyer)

    # Withdraw funds
    withdrawn_amount = contract.withdraw(caller=owner)
    print(f"Owner withdrew: {withdrawn_amount}")



    # Confirm delevery
    contract.confirmDelivery(caller=veryfier)
    # Release payment to trh Owner(factory)
    try:
       contract.releasePayment(caller=veryfier)
       print("Payment release successful")

    except:
        print("payment release unsuccessful")
 
    
    # Show status
    print("Stock:", contract.get_stock())
    print("Balance:", contract.get_contract_balance())
    print("Events:", contract.get_event_log())
