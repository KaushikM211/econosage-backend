# econ_compute.py

import math
import inspect
from data_fetcher import *

# --------------------
# Core Financial Math
# --------------------

def calculate_compound_interest(**kwargs):
    P = kwargs.get('P')
    r = kwargs.get('r')
    n = kwargs.get('n')
    t = kwargs.get('t')
    if None in (P, r, n, t):
        raise ValueError("Missing parameters for compound interest: P, r, n, t required.")
    A = P * (1 + r / n) ** (n * t)
    return round(A, 2), "A = P * (1 + r/n)^(n*t)"

def calculate_principal_from_compound(**kwargs):
    A = kwargs.get('A')
    r = kwargs.get('r')
    n = kwargs.get('n')
    t = kwargs.get('t')
    if None in (A, r, n, t):
        raise ValueError("Missing parameters for principal from compound: A, r, n, t required.")
    P = A / (1 + r / n) ** (n * t)
    return round(P, 2), "P = A / (1 + r/n)^(n*t)"

def calculate_rate_from_compound(**kwargs):
    P = kwargs.get('P')
    A = kwargs.get('A')
    n = kwargs.get('n')
    t = kwargs.get('t')
    tol = kwargs.get('tol', 1e-8)
    max_iter = kwargs.get('max_iter', 1000)
    if None in (P, A, n, t):
        raise ValueError("Missing parameters for rate from compound: P, A, n, t required.")
    r = 0.05
    for _ in range(max_iter):
        f = P * (1 + r / n) ** (n * t) - A
        if abs(f) < tol:
            return round(r, 8), "Numerically solved r in compound interest"
        df = P * (n * t) * (1 + r / n) ** (n * t - 1) / n
        if df == 0:
            break
        r_new = r - f / df
        if abs(r_new - r) < tol:
            return round(r_new, 8), "Numerically solved r in compound interest"
        r = r_new
    raise ValueError("Rate calculation did not converge")

def calculate_simple_interest(**kwargs):
    P = kwargs.get('P')
    r = kwargs.get('r')
    t = kwargs.get('t')
    if None in (P, r, t):
        raise ValueError("Missing parameters for simple interest: P, r, t required.")
    I = P * r * t
    return round(I, 2), "I = P * r * t"

def calculate_present_value(**kwargs):
    FV = kwargs.get('FV')
    r = kwargs.get('r')
    t = kwargs.get('t')
    if None in (FV, r, t):
        raise ValueError("Missing parameters for present value: FV, r, t required.")
    PV = FV / (1 + r) ** t
    return round(PV, 2), "PV = FV / (1 + r)^t"

def calculate_roi(**kwargs):
    # Support two modes:
    # Mode 1: gain, cost
    # Mode 2: P, r, n, t (compounded)
    gain = kwargs.get('gain')
    cost = kwargs.get('cost')
    P = kwargs.get('P')
    r = kwargs.get('r')
    n = kwargs.get('n')
    t = kwargs.get('t')

    if gain is not None and cost is not None:
        if cost == 0:
            raise ValueError("Cost cannot be zero")
        roi = (gain - cost) / cost
        return round(roi, 4), "ROI = (Gain - Cost) / Cost"
    elif None not in (P, r, n, t):
        A = P * (1 + r / n) ** (n * t)
        roi = (A - P) / P
        return round(roi, 4), "ROI from compound interest = (A - P) / P"
    else:
        raise ValueError("Insufficient parameters for ROI: provide either gain & cost or P, r, n, t.")

def calculate_npv(**kwargs):
    discount_rate = kwargs.get('discount_rate')
    cash_flows = kwargs.get('cash_flows')
    if discount_rate is None or cash_flows is None:
        raise ValueError("Missing parameters for NPV: discount_rate and cash_flows required.")
    npv = sum(cf / ((1 + discount_rate) ** i) for i, cf in enumerate(cash_flows))
    return round(npv, 2), "NPV = Σ (Cash Flow / (1 + r)^t)"

def calculate_future_value_annuity(**kwargs):
    payment = kwargs.get('payment')
    rate_per_period = kwargs.get('rate_per_period')
    periods = kwargs.get('periods')
    if None in (payment, rate_per_period, periods):
        raise ValueError("Missing parameters for future value annuity: payment, rate_per_period, periods required.")
    if rate_per_period == 0:
        fv = payment * periods
    else:
        fv = payment * ((1 + rate_per_period) ** periods - 1) / rate_per_period
    return round(fv, 2), "FV = payment * [((1 + r)^n - 1) / r]"

# --------------------
# Policy Simulator
# --------------------

def calculate_sales_tax(**kwargs):
    base_price = kwargs.get('base_price')
    tax_rate = kwargs.get('tax_rate')
    if None in (base_price, tax_rate):
        raise ValueError("Missing parameters for sales tax: base_price and tax_rate required.")
    final_price = base_price * (1 + tax_rate)
    return round(final_price, 2), "Final Price = Base Price × (1 + Tax Rate)"

def calculate_vat(**kwargs):
    base_price = kwargs.get('base_price')
    vat_rate = kwargs.get('vat_rate')
    if None in (base_price, vat_rate):
        raise ValueError("Missing parameters for VAT: base_price and vat_rate required.")
    final_price = base_price * (1 + vat_rate)
    return round(final_price, 2), "Final Price = Base Price × (1 + VAT Rate)"

def calculate_emi(**kwargs):
    principal = kwargs.get('principal')
    annual_rate = kwargs.get('annual_rate')
    months = kwargs.get('months')
    if None in (principal, annual_rate, months):
        raise ValueError("Missing parameters for EMI: principal, annual_rate, months required.")
    r = annual_rate / 12
    if r == 0:
        emi = principal / months
    else:
        emi = principal * r * ((1 + r) ** months) / (((1 + r) ** months) - 1)
    return round(emi, 2), "EMI = P·r·(1+r)^n / [(1+r)^n - 1]"

def calculate_subsidy_removal_effect(**kwargs):
    base_cost = kwargs.get('base_cost')
    subsidy_amount = kwargs.get('subsidy_amount')
    if None in (base_cost, subsidy_amount):
        raise ValueError("Missing parameters for subsidy removal effect: base_cost and subsidy_amount required.")
    new_cost = base_cost + subsidy_amount
    return round(new_cost, 2), "New Cost = Base + Subsidy Removed"

def calculate_fuel_cost_impact(**kwargs):
    base_cost = kwargs.get('base_cost')
    fuel_share = kwargs.get('fuel_share')
    price_delta = kwargs.get('price_delta')
    if None in (base_cost, fuel_share, price_delta):
        raise ValueError("Missing parameters for fuel cost impact: base_cost, fuel_share, price_delta required.")
    increase = price_delta * fuel_share
    new_cost = base_cost + increase
    return round(new_cost, 2), "New Cost = Base + (ΔFuel Price × Fuel Share)"

def calculate_income_tax_slab(**kwargs):
    income = kwargs.get('income')
    slabs = kwargs.get('slabs')
    rates = kwargs.get('rates')
    if None in (income, slabs, rates):
        raise ValueError("Missing parameters for income tax slab: income, slabs, and rates required.")
    tax = 0
    prev_limit = 0
    for slab_limit, rate in zip(slabs, rates):
        if income > slab_limit:
            taxable = slab_limit - prev_limit
        else:
            taxable = max(0, income - prev_limit)
        tax += taxable * rate
        prev_limit = slab_limit
        if income <= slab_limit:
            break
    return round(tax, 2), "Income Tax computed on slab rates"

def calculate_minimum_wage_impact(**kwargs):
    current_wage = kwargs.get('current_wage')
    min_wage = kwargs.get('min_wage')
    workforce_pct = kwargs.get('workforce_pct')
    if None in (current_wage, min_wage, workforce_pct):
        raise ValueError("Missing parameters for minimum wage impact: current_wage, min_wage, and workforce_pct required.")
    if current_wage >= min_wage:
        return 0.0, "No wage increase required"
    increase = (min_wage - current_wage) * workforce_pct
    return round(increase, 2), "Wage cost increase due to minimum wage policy"

def calculate_budget_deficit(**kwargs):
    gov_expenditure = kwargs.get('gov_expenditure')
    gov_revenue = kwargs.get('gov_revenue')
    if None in (gov_expenditure, gov_revenue):
        raise ValueError("Missing parameters for budget deficit: gov_expenditure and gov_revenue required.")
    deficit = gov_expenditure - gov_revenue
    return round(deficit, 2), "Budget Deficit = Expenditure - Revenue"

def calculate_effective_tax_rate(**kwargs):
    total_tax_paid = kwargs.get('total_tax_paid')
    total_income = kwargs.get('total_income')
    if None in (total_tax_paid, total_income):
        raise ValueError("Missing parameters for effective tax rate: total_tax_paid and total_income required.")
    if total_income == 0:
        raise ValueError("Total income cannot be zero")
    rate = total_tax_paid / total_income
    return round(rate, 4), "Effective Tax Rate = Tax Paid / Income"

def calculate_public_investment_multiplier(**kwargs):
    mpc = kwargs.get('mpc')
    mps = kwargs.get('mps')
    if None in (mpc, mps):
        raise ValueError("Missing parameters for public investment multiplier: mpc and mps required.")
    if mps == 0:
        raise ValueError("MPS cannot be zero")
    multiplier = 1 / mps
    return round(multiplier, 4), "Multiplier = 1 / MPS"

# --------------------
# Inflation Explainer
# --------------------

def calculate_weighted_cpi(**kwargs):
    weights_dict = kwargs.get('weights_dict')
    inflation_dict = kwargs.get('inflation_dict')
    if weights_dict is None or inflation_dict is None:
        raise ValueError("Missing parameters for weighted CPI: weights_dict and inflation_dict are required.")
    cpi = sum(weights_dict.get(k, 0) * inflation_dict.get(k, 0) for k in weights_dict)
    return round(cpi, 4), "CPI = Σ (weight × category inflation)"

def calculate_inflated_cost(**kwargs):
    base_value = kwargs.get('base_value')
    inflation_rate = kwargs.get('inflation_rate')
    years = kwargs.get('years')
    if None in (base_value, inflation_rate, years):
        raise ValueError("Missing parameters for inflated cost: base_value, inflation_rate, years required.")
    future_value = base_value * (1 + inflation_rate) ** years
    return round(future_value, 2), "FV = PV × (1 + r)^t"

def calculate_real_value(**kwargs):
    nominal_value = kwargs.get('nominal_value')
    inflation_rate = kwargs.get('inflation_rate')
    if None in (nominal_value, inflation_rate):
        raise ValueError("Missing parameters for real value: nominal_value, inflation_rate required.")
    real_value = nominal_value / (1 + inflation_rate)
    return round(real_value, 2), "Real Value = Nominal / (1 + Inflation Rate)"

def calculate_reverse_inflation(**kwargs):
    present_value = kwargs.get('present_value')
    future_value = kwargs.get('future_value')
    years = kwargs.get('years')
    if None in (present_value, future_value, years):
        raise ValueError("Missing parameters for reverse inflation: present_value, future_value, years required.")
    rate = (future_value / present_value) ** (1 / years) - 1
    return round(rate, 4), "r = (FV / PV)^(1/t) - 1"

def calculate_inflation_adjusted_salary(**kwargs):
    salary = kwargs.get('salary')
    inflation_rate = kwargs.get('inflation_rate')
    years = kwargs.get('years')
    if None in (salary, inflation_rate, years):
        raise ValueError("Missing parameters for inflation adjusted salary: salary, inflation_rate, years required.")
    adjusted_salary = salary * (1 + inflation_rate) ** years
    return round(adjusted_salary, 2), "Adjusted Salary = Salary × (1 + inflation)^years"

def calculate_rule_of_72(**kwargs):
    inflation_rate = kwargs.get('inflation_rate')
    if inflation_rate is None:
        raise ValueError("Missing parameter for rule of 72: inflation_rate required.")
    if inflation_rate == 0:
        return float('inf'), "Rule of 72: Inflation rate cannot be zero"
    years = 72 / (inflation_rate * 100)
    return round(years, 2), "Rule of 72 = 72 / Inflation Rate (%)"

def calculate_real_interest_rate(**kwargs):
    nominal_rate = kwargs.get('nominal_rate')
    inflation_rate = kwargs.get('inflation_rate')
    if None in (nominal_rate, inflation_rate):
        raise ValueError("Missing parameters for real interest rate: nominal_rate and inflation_rate required.")
    real_rate = ((1 + nominal_rate) / (1 + inflation_rate)) - 1
    return round(real_rate, 4), "Real Interest Rate = ((1 + Nominal) / (1 + Inflation)) - 1"

def calculate_purchasing_power_loss(**kwargs):
    original_price = kwargs.get('original_price')
    inflation_rate = kwargs.get('inflation_rate')
    years = kwargs.get('years')
    if None in (original_price, inflation_rate, years):
        raise ValueError("Missing parameters for purchasing power loss: original_price, inflation_rate, years required.")
    loss = original_price * (1 - 1 / ((1 + inflation_rate) ** years))
    return round(loss, 2), "Purchasing Power Loss over years"

# --------------------
# MacroLens
# --------------------

def calculate_import_cost_with_fx(**kwargs):
    base_cost = kwargs.get('base_cost')
    fx_devaluation_pct = kwargs.get('fx_devaluation_pct')
    if None in (base_cost, fx_devaluation_pct):
        raise ValueError("Missing parameters for import cost with FX: base_cost and fx_devaluation_pct required.")
    new_cost = base_cost * (1 + fx_devaluation_pct)
    return round(new_cost, 2), "Import Cost = Base × (1 + FX Drop Rate)"

def calculate_capital_flow_score(**kwargs):
    us_rate_delta = kwargs.get('us_rate_delta')
    exposure_index = kwargs.get('exposure_index')
    if None in (us_rate_delta, exposure_index):
        raise ValueError("Missing parameters for capital flow score: us_rate_delta and exposure_index required.")
    score = us_rate_delta * exposure_index
    return round(score, 4), "Score = US Rate Change × Exposure Index"

def calculate_gdp_growth_from_policy(**kwargs):
    fiscal_stimulus = kwargs.get('fiscal_stimulus')
    multiplier = kwargs.get('multiplier')
    base_gdp = kwargs.get('base_gdp')
    if None in (fiscal_stimulus, multiplier, base_gdp):
        raise ValueError("Missing parameters for GDP growth from policy: fiscal_stimulus, multiplier, base_gdp required.")
    growth = fiscal_stimulus * multiplier / base_gdp
    return round(growth * 100, 2), "GDP Growth % from Fiscal Stimulus"

def calculate_external_debt_burden(**kwargs):
    debt_usd = kwargs.get('debt_usd')
    fx_rate_local = kwargs.get('fx_rate_local')
    gdp_local = kwargs.get('gdp_local')
    if None in (debt_usd, fx_rate_local, gdp_local):
        raise ValueError("Missing parameters for external debt burden: debt_usd, fx_rate_local, gdp_local required.")
    debt_local = debt_usd * fx_rate_local
    burden_ratio = debt_local / gdp_local
    return round(burden_ratio, 4), "External Debt Burden = Debt / GDP"

def calculate_trade_deficit_growth(**kwargs):
    trade_deficit_current = kwargs.get('trade_deficit_current')
    trade_deficit_previous = kwargs.get('trade_deficit_previous')
    if None in (trade_deficit_current, trade_deficit_previous):
        raise ValueError("Missing parameters for trade deficit growth: trade_deficit_current and trade_deficit_previous required.")
    if trade_deficit_previous == 0:
        raise ValueError("Previous trade deficit cannot be zero")
    growth = (trade_deficit_current - trade_deficit_previous) / trade_deficit_previous
    return round(growth, 4), "Trade Deficit Growth Rate"

def calculate_macro_stress_score(**kwargs):
    fiscal_deficit = kwargs.get('fiscal_deficit')
    inflation_rate = kwargs.get('inflation_rate')
    external_debt_ratio = kwargs.get('external_debt_ratio')
    if None in (fiscal_deficit, inflation_rate, external_debt_ratio):
        raise ValueError("Missing parameters for macro stress score: fiscal_deficit, inflation_rate, external_debt_ratio required.")
    score = 0.5 * fiscal_deficit + 0.3 * inflation_rate + 0.2 * external_debt_ratio
    return round(score, 4), "Macro Stress Composite Score"

# --------------------
# Other Core Metrics
# --------------------

def calculate_break_even(**kwargs):
    fixed_costs = kwargs.get('fixed_costs')
    price_per_unit = kwargs.get('price_per_unit')
    variable_cost_per_unit = kwargs.get('variable_cost_per_unit')
    if None in (fixed_costs, price_per_unit, variable_cost_per_unit):
        raise ValueError("Missing parameters for break-even: fixed_costs, price_per_unit, variable_cost_per_unit required.")
    margin = price_per_unit - variable_cost_per_unit
    if margin == 0:
        raise ValueError("Price must exceed variable cost")
    units = fixed_costs / margin
    return round(units, 2), "Break-even = Fixed / (Price - Variable)"

def calculate_price_elasticity_of_demand(**kwargs):
    percent_change_quantity = kwargs.get('percent_change_quantity')
    percent_change_price = kwargs.get('percent_change_price')
    if None in (percent_change_quantity, percent_change_price):
        raise ValueError("Missing parameters for price elasticity of demand: percent_change_quantity and percent_change_price required.")
    if percent_change_price == 0:
        raise ValueError("Price change cannot be zero")
    ped = percent_change_quantity / percent_change_price
    return round(ped, 4), "PED = ΔQ% / ΔP%"

def calculate_gdp_growth_rate(**kwargs):
    gdp_t = kwargs.get('gdp_t')
    gdp_t_minus_1 = kwargs.get('gdp_t_minus_1')
    if None in (gdp_t, gdp_t_minus_1):
        raise ValueError("Missing parameters for GDP growth rate: gdp_t and gdp_t_minus_1 required.")
    if gdp_t_minus_1 == 0:
        raise ValueError("Previous GDP cannot be zero")
    growth = ((gdp_t - gdp_t_minus_1) / gdp_t_minus_1) * 100
    return round(growth, 2), "GDP Growth = (GDP_t - GDP_t-1) / GDP_t-1 × 100%"

def calculate_debt_to_equity(**kwargs):
    total_debt = kwargs.get('total_debt')
    shareholders_equity = kwargs.get('shareholders_equity')
    if None in (total_debt, shareholders_equity):
        raise ValueError("Missing parameters for debt to equity: total_debt and shareholders_equity required.")
    if shareholders_equity == 0:
        raise ValueError("Equity cannot be zero")
    ratio = total_debt / shareholders_equity
    return round(ratio, 4), "D/E = Debt / Equity"

def calculate_inventory_turnover(**kwargs):
    cost_of_goods_sold = kwargs.get('cost_of_goods_sold')
    average_inventory = kwargs.get('average_inventory')
    if None in (cost_of_goods_sold, average_inventory):
        raise ValueError("Missing parameters for inventory turnover: cost_of_goods_sold and average_inventory required.")
    if average_inventory == 0:
        raise ValueError("Inventory cannot be zero")
    turnover = cost_of_goods_sold / average_inventory
    return round(turnover, 2), "Turnover = COGS / Avg Inventory"

def calculate_contribution_margin(**kwargs):
    price_per_unit = kwargs.get('price_per_unit')
    variable_cost_per_unit = kwargs.get('variable_cost_per_unit')
    if None in (price_per_unit, variable_cost_per_unit):
        raise ValueError("Missing parameters for contribution margin: price_per_unit and variable_cost_per_unit required.")
    margin = price_per_unit - variable_cost_per_unit
    return round(margin, 2), "CM = Price - Variable Cost"

def calculate_operating_profit_margin(**kwargs):
    operating_income = kwargs.get('operating_income')
    revenue = kwargs.get('revenue')
    if None in (operating_income, revenue):
        raise ValueError("Missing parameters for operating profit margin: operating_income and revenue required.")
    if revenue == 0:
        raise ValueError("Revenue cannot be zero")
    margin = (operating_income / revenue) * 100
    return round(margin, 2), "OPM = Operating Income / Revenue × 100%"

def calculate_capm(**kwargs):
    risk_free_rate = kwargs.get('risk_free_rate')
    beta = kwargs.get('beta')
    market_return = kwargs.get('market_return')
    if None in (risk_free_rate, beta, market_return):
        raise ValueError("Missing parameters for CAPM: risk_free_rate, beta, market_return required.")
    expected_return = risk_free_rate + beta * (market_return - risk_free_rate)
    return round(expected_return, 4), "CAPM = Rf + β(Rm - Rf)"

def calculate_elasticity_of_supply(**kwargs):
    percent_change_quantity_supplied = kwargs.get('percent_change_quantity_supplied')
    percent_change_price = kwargs.get('percent_change_price')
    if None in (percent_change_quantity_supplied, percent_change_price):
        raise ValueError("Missing parameters for elasticity of supply: percent_change_quantity_supplied and percent_change_price required.")
    if percent_change_price == 0:
        raise ValueError("Price change cannot be zero")
    elasticity = percent_change_quantity_supplied / percent_change_price
    return round(elasticity, 4), "Elasticity = ΔQs% / ΔP%"

def calculate_dscr(**kwargs):
    net_operating_income = kwargs.get('net_operating_income')
    total_debt_service = kwargs.get('total_debt_service')
    if None in (net_operating_income, total_debt_service):
        raise ValueError("Missing parameters for DSCR: net_operating_income and total_debt_service required.")
    if total_debt_service == 0:
        raise ValueError("Debt service cannot be zero")
    dscr = net_operating_income / total_debt_service
    return round(dscr, 4), "DSCR = NOI / Debt Service"

def calculate_eoq(**kwargs):
    demand = kwargs.get('demand')
    ordering_cost = kwargs.get('ordering_cost')
    holding_cost = kwargs.get('holding_cost')
    if None in (demand, ordering_cost, holding_cost):
        raise ValueError("Missing parameters for EOQ: demand, ordering_cost, holding_cost required.")
    if holding_cost == 0:
        raise ValueError("Holding cost cannot be zero")
    eoq = math.sqrt((2 * demand * ordering_cost) / holding_cost)
    return round(eoq, 2), "EOQ = √(2DS/H)"

def calculate_wacc(**kwargs):
    E = kwargs.get('E')
    V = kwargs.get('V')
    Re = kwargs.get('Re')
    D = kwargs.get('D')
    Rd = kwargs.get('Rd')
    Tc = kwargs.get('Tc')
    if None in (E, V, Re, D, Rd, Tc):
        raise ValueError("Missing parameters for WACC: E, V, Re, D, Rd, Tc required.")
    if V == 0:
        raise ValueError("V cannot be zero")
    wacc = (E / V) * Re + (D / V) * Rd * (1 - Tc)
    return round(wacc, 4), "WACC = (E/V)*Re + (D/V)*Rd*(1 - Tc)"

def calculate_markup_price(**kwargs):
    cost = kwargs.get('cost')
    markup_percentage = kwargs.get('markup_percentage')
    if None in (cost, markup_percentage):
        raise ValueError("Missing parameters for markup price: cost and markup_percentage required.")
    price = cost + (cost * markup_percentage)
    return round(price, 2), "Price = Cost + (Cost × Markup%)"

def calculate_payback_period(**kwargs):
    # Accept either:
    #   - initial_investment and annual_cash_inflow
    #   - or other params if needed in future

    initial_investment = kwargs.get("initial_investment")
    annual_cash_inflow = kwargs.get("annual_cash_inflow")

    if initial_investment is None or annual_cash_inflow is None:
        raise ValueError("initial_investment and annual_cash_inflow are required parameters")

    if annual_cash_inflow == 0:
        raise ValueError("Annual cash inflow cannot be zero")

    period = initial_investment / annual_cash_inflow
    return round(period, 2), "Payback Period = Investment / Annual Cash Inflow"


SUPPORTED_FUNCTIONS = {
    # Core simple
    "compound_interest": calculate_compound_interest,
    "principal_from_compound": calculate_principal_from_compound,
    "rate_from_compound": calculate_rate_from_compound,
    "simple_interest": calculate_simple_interest,
    "present_value": calculate_present_value,
    "roi": calculate_roi,
    "npv": calculate_npv,
    "future_value_annuity": calculate_future_value_annuity,

    # Policy Simulator
    "sales_tax": calculate_sales_tax,
    "vat": calculate_vat,
    "emi": calculate_emi,
    "subsidy_removal_effect": calculate_subsidy_removal_effect,
    "fuel_cost_impact": calculate_fuel_cost_impact,
    "income_tax_slab": calculate_income_tax_slab,
    "minimum_wage_impact": calculate_minimum_wage_impact,
    "budget_deficit": calculate_budget_deficit,
    "effective_tax_rate": calculate_effective_tax_rate,
    "public_investment_multiplier": calculate_public_investment_multiplier,

    # Inflation Explainer
    "inflated_cost": calculate_inflated_cost,
    "real_value": calculate_real_value,
    "reverse_inflation": calculate_reverse_inflation,
    "weighted_cpi": calculate_weighted_cpi,
    "inflation_adjusted_salary": calculate_inflation_adjusted_salary,
    "rule_of_72": calculate_rule_of_72,
    "real_interest_rate": calculate_real_interest_rate,
    "purchasing_power_loss": calculate_purchasing_power_loss,

    # MacroLens
    "import_cost_fx": calculate_import_cost_with_fx,
    "capital_flow_score": calculate_capital_flow_score,
    "gdp_growth_from_policy": calculate_gdp_growth_from_policy,
    "external_debt_burden": calculate_external_debt_burden,
    "trade_deficit_growth": calculate_trade_deficit_growth,
    "macro_stress_score": calculate_macro_stress_score,

    # Other Core Metrics
    "break_even": calculate_break_even,
    "payback_period": calculate_payback_period,
    "price_elasticity_of_demand": calculate_price_elasticity_of_demand,
    "gdp_growth_rate": calculate_gdp_growth_rate,
    "debt_to_equity": calculate_debt_to_equity,
    "inventory_turnover": calculate_inventory_turnover,
    "contribution_margin": calculate_contribution_margin,
    "operating_profit_margin": calculate_operating_profit_margin,
    "capm": calculate_capm,
    "elasticity_of_supply": calculate_elasticity_of_supply,
    "dscr": calculate_dscr,
    "eoq": calculate_eoq,
    "wacc": calculate_wacc,
    "markup_price": calculate_markup_price,

   # Data Fetch Functions
   "get_stock_price": get_stock_price,
   "get_currency_rate": get_currency_rate,
   "get_inflation_rate": get_inflation_rate,
   "get_gst_rate": get_gst_rate
}

def execute_formula(formula_name, params):
    if formula_name not in SUPPORTED_FUNCTIONS:
        raise NotImplementedError(f"Formula '{formula_name}' not implemented.")

    func = SUPPORTED_FUNCTIONS[formula_name]
    return func(**params)


