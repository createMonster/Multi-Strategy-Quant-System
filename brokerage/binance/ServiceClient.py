#aids in the order logic and helps integrate the brokerage into the system, no external dependency


class ServiceClient():

    def __init__(self, brokerage_config=None):
        self.brokerage_config = brokerage_config

    #lets implement some API interface that our TradeClient would use, and later we will see how they become useful

    def get_size_config(self, inst):
        order_min_contracts = 1 #minimum size of order
        contract_size = 1 #size in units of a contract
        return order_min_contracts, contract_size

    def get_order_specs(self, inst, units, current_contracts):
        #this is an internal `order` object that is passed around different components of the trading system
        #it is the `settings` of an order item, that all brokerages should implement to meet internal needs
        order_min_contracts, contract_size = self.get_size_config(inst)
        order_min_units = self.contracts_to_units(label=inst, contracts=order_min_contracts)
        optimal_min_order = units / order_min_units
        rounded_min_order = round(optimal_min_order)
        specs = {
            "instrument": inst,
            "scaled_units": units,
            "contract_size": contract_size,
            "order_min_contracts": order_min_contracts,
            "order_min_units": order_min_units,
            "optimal_contracts": optimal_min_order * order_min_contracts,
            "rounded_contracts": rounded_min_order * order_min_contracts,
            "current_contracts": current_contracts,
            "current_units": self.contracts_to_units(inst, current_contracts)
        }
        return specs

    def contracts_to_units(self, label, contracts):
        order_min_contracts, contract_size = self.get_size_config(label)
        return contracts * contract_size

    def units_to_contracts(self, label, units):
        #these are conversions between contract and unit sizing, for instance how many units are there in a micro contract, a mini contract etc?
        #these depend on the brokerage specifications!
        order_min_contracts, contract_size = self.get_size_config(label)
        return units / contract_size


    def is_inertia_override(self, percent_change):
        return percent_change > 0.05 #positional inertia to prevent too frequent trading
    
    def code_to_label_nomenclature(self, code):
        #these are external to internal conversions between instrument naming
        #for instance a EUR/USD contract can be: EUR_USD, EUR/USD, EUR;USD etc etc. let code be the brokerage code, and the label be the internal name
        return code

    def label_to_code_nomenclature(self, label):
        return label
