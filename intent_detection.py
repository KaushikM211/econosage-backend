# -*- coding: utf-8 -*-
"""intent_detection

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TiHCbwkMgQJUrBbq2Uq2WwuGftRdSLLd
"""

import re
import ast
import operator as op
from gemini_module import is_theoretical_question, ask_gemini_explainer, model



# Map all formulas to a comprehensive list of keywords for intent detection
INTENT_KEYWORDS = {
    # Core finance formulas
    "compound_interest": ["compound interest", "compound"],
    "simple_interest": ["simple interest", "simple"],
    "principal_from_compound": ["principal from compound", "principal", "initial amount"],
    "rate_from_compound": ["rate from compound", "interest rate", "rate of return"],
    "roi": ["return on investment", "roi"],
    "break_even": ["break even", "breakeven"],
    "npv": ["net present value", "npv"],
    "future_value_annuity": ["future value annuity", "annuity"],
    "payback_period": ["payback period"],
    "price_elasticity_of_demand": ["price elasticity of demand", "elasticity of demand", "ped"],
    "gdp_growth_rate": ["gdp growth rate", "economic growth rate", "gdp growth"],
    "debt_to_equity": ["debt to equity", "debt-equity ratio"],
    "contribution_margin": ["contribution margin"],
    "inventory_turnover": ["inventory turnover"],
    "operating_profit_margin": ["operating profit margin"],
    "present_value": ["present value", "pv"],
    "capm": ["capm", "capital asset pricing model"],
    "elasticity_of_supply": ["elasticity of supply"],
    "dscr": ["debt service coverage ratio", "dscr"],
    "eoq": ["economic order quantity", "eoq"],
    "wacc": ["weighted average cost of capital", "wacc"],
    "markup_price": ["markup pricing", "markup price"],

    # Policy Simulator formulas
    "sales_tax": ["sales tax", "gst", "goods and services tax", "vat", "tax slab", "tax rates"],
    "income_tax_slab": ["income tax slab", "tax slab", "income tax", "tax bracket"],
    "minimum_wage_impact": ["minimum wage", "wage impact", "minimum salary"],
    "budget_deficit": ["budget deficit", "fiscal deficit", "government deficit"],
    "effective_tax_rate": ["effective tax rate", "tax rate"],
    "public_investment_multiplier": ["public investment multiplier", "fiscal multiplier"],
    "subsidy_removal": ["subsidy removal", "removal of subsidy", "end of subsidy"],
    "fuel_cost_impact": ["fuel cost impact", "fuel price effect", "fuel cost"],

    # Inflation Explainer formulas
    "inflation_adjusted_salary": ["inflation adjusted salary", "inflated salary", "inflation adjustment"],
    "rule_of_72": ["rule of 72", "doubling time"],
    "real_interest_rate": ["real interest rate", "inflation adjusted rate"],
    "purchasing_power_loss": ["purchasing power loss", "power loss", "inflation effect"],
    "weighted_cpi": ["weighted cpi", "consumer price index", "cpi"],

    # MacroLens formulas
    "gdp_growth_from_policy": ["gdp growth from policy", "policy impact on gdp", "fiscal stimulus impact"],
    "trade_deficit_growth": ["trade deficit growth", "trade deficit increase", "balance of trade"],
    "macro_stress_score": ["macro stress score", "economic stress", "financial stress"],
    "external_debt_burden": ["external debt burden", "foreign debt burden"],
    "capital_flow_score": ["capital flow", "capital movement", "capital inflow", "capital outflow"],

    # Region specific (generic keys - interpret region separately)
    "vat_sales_tax": ["vat", "sales tax", "value added tax"],
    "income_tax_bracket": ["income tax bracket", "tax bracket", "tax slabs"],


    # Stock Market, Data Fetcher
    "get_stock_price": ["stock price", "share price", "price of stock", "stock quote", "ticker price", "share value"],
    "get_currency_rate": ["currency exchange rate", "exchange rate", "currency converter", "convert currency", "forex rate"],
    "get_inflation_rate": ["inflation rate", "consumer price index", "cpi"],
    "get_gst_rate": ["gst", "vat", "tax rate", "sales tax"]

    # Add more as needed
}


PARAM_PATTERNS = {
    # --- Core financial parameters ---
    "P": r"(?:principal|P)\s*(?:=|is|:)?\s*([\d\.]+)",  # Principal amount (initial investment or loan)
    "r": r"(?:rate|interest rate|r)\s*(?:=|is|:)?\s*([\d\.]+)%?",  # Interest rate (percentage or decimal)
    "t": r"(?:time|duration|t)\s*(?:=|is|:)?\s*([\d\.]+)",  # Time period (years)
    "n": r"(?:n|compounded|frequency|times per year)\s*(?:=|is|:)?\s*([\d\.]+)",  # Compounding frequency per year

    # --- Final amount / total value ---
    "A": r"(?:amount|final amount|total amount|A)\s*(?:=|is|:)?\s*([\d\.]+)",  # Final amount including interest

    # --- ROI specific ---
    "gain": r"(?:gain|profit)\s*(?:=|is|:)?\s*([\d\.]+)",  # Gain or profit
    "cost": r"(?:cost|investment cost)\s*(?:=|is|:)?\s*([\d\.]+)",  # Cost value

    # --- Break-even analysis ---
    "fixed_costs": r"(?:fixed costs?)\s*(?:=|is|:)?\s*([\d\.]+)",  # Fixed costs
    "price_per_unit": r"(?:price per unit|selling price)\s*(?:=|is|:)?\s*([\d\.]+)",  # Selling price
    "variable_cost_per_unit": r"(?:variable cost per unit)\s*(?:=|is|:)?\s*([\d\.]+)",  # Variable cost

    # --- DCF / NPV / IRR ---
    "discount_rate": r"(?:discount rate|discount)\s*(?:=|is|:)?\s*([\d\.]+)%?",  # Discount rate
    "cash_flows": r"(?:cash flows?)\s*(?:=|are|:)?\s*\[([\d\.,\s]+)\]",  # List of cash flows

    # --- Loan/Annuity/EMI ---
    "payment": r"(?:payment|PMT)\s*(?:=|is|:)?\s*([\d\.]+)",  # Payment per period
    "rate_per_period": r"(?:rate per period)\s*(?:=|is|:)?\s*([\d\.]+)%?",  # Periodic interest rate
    "periods": r"(?:periods?|n_periods?)\s*(?:=|is|:)?\s*([\d\.]+)",  # Total number of periods

    # --- Payback / profitability analysis ---
    "initial_investment": r"(?:initial investment)\s*(?:=|is|:)?\s*([\d\.]+)",  # Initial investment
    "annual_cash_inflow": r"(?:annual cash inflow)\s*(?:=|is|:)?\s*([\d\.]+)",  # Annual returns

    # --- Elasticity ---
    "percent_change_quantity": r"(?:percent(?:age)? change in quantity)\s*(?:=|is|:)?\s*([\d\.]+)%?",  # % change in quantity
    "percent_change_price": r"(?:percent(?:age)? change in price)\s*(?:=|is|:)?\s*([\d\.]+)%?",  # % change in price
    "percent_change_quantity_supplied": r"(?:percent(?:age)? change in quantity supplied)\s*(?:=|is|:)?\s*([\d\.]+)%?",  # % change in supply

    # --- GDP Growth ---
    "gdp_t": r"(?:gdp(?: at time t)?)\s*(?:=|is|:)?\s*([\d\.]+)",  # GDP at time t
    "gdp_t_minus_1": r"(?:gdp(?: at time t-1)?)\s*(?:=|is|:)?\s*([\d\.]+)",  # GDP at time t-1

    # --- Financial ratios ---
    "total_debt": r"(?:total debt)\s*(?:=|is|:)?\s*([\d\.]+)",  # Total debt
    "shareholders_equity": r"(?:shareholders'? equity)\s*(?:=|is|:)?\s*([\d\.]+)",  # Shareholders' equity
    "operating_income": r"(?:operating income)\s*(?:=|is|:)?\s*([\d\.]+)",  # Operating income
    "revenue": r"(?:revenue|sales)\s*(?:=|is|:)?\s*([\d\.]+)",  # Revenue

    # --- CAPM / WACC ---
    "risk_free_rate": r"(?:risk[- ]free rate)\s*(?:=|is|:)?\s*([\d\.]+)%?",  # Risk-free rate
    "beta": r"(?:beta)\s*(?:=|is|:)?\s*([\d\.]+)",  # Beta
    "market_return": r"(?:market return)\s*(?:=|is|:)?\s*([\d\.]+)%?",  # Expected market return

    # --- DSCR ---
    "net_operating_income": r"(?:net operating income|NOI)\s*(?:=|is|:)?\s*([\d\.]+)",  # NOI
    "total_debt_service": r"(?:total debt service)\s*(?:=|is|:)?\s*([\d\.]+)",  # Total debt service

    # --- EOQ ---
    "demand": r"(?:demand)\s*(?:=|is|:)?\s*([\d\.]+)",  # Demand
    "ordering_cost": r"(?:ordering cost)\s*(?:=|is|:)?\s*([\d\.]+)",  # Ordering cost
    "holding_cost": r"(?:holding cost)\s*(?:=|is|:)?\s*([\d\.]+)",  # Holding cost

    # --- WACC specific ---
    "E": r"(?:market value of equity|E)\s*(?:=|is|:)?\s*([\d\.]+)",  # Equity market value
    "V": r"(?:total market value|V)\s*(?:=|is|:)?\s*([\d\.]+)",  # Total market value (E + D)
    "Re": r"(?:cost of equity|Re)\s*(?:=|is|:)?\s*([\d\.]+)%?",  # Cost of equity
    "D": r"(?:market value of debt|D)\s*(?:=|is|:)?\s*([\d\.]+)",  # Debt market value
    "Rd": r"(?:cost of debt|Rd)\s*(?:=|is|:)?\s*([\d\.]+)%?",  # Cost of debt
    "Tc": r"(?:corporate tax rate|Tc)\s*(?:=|is|:)?\s*([\d\.]+)%?",  # Tax rate

    # --- Markup calculation ---
    "markup_percentage": r"(?:markup(?: percentage)?)\s*(?:=|is|:)?\s*([\d\.]+)%?",  # Markup %

    # --- Stock/Currency/Misc ---
    "stock_symbol": r"(?:stock symbol|ticker|symbol|share of|stock of|stock price of|price of)\s*(?:=|is|:)?\s*([A-Za-z]{1,5})",  # Stock symbol
    "from_currency": r"(?:from currency)\s*(?:=|is|:)?\s*([A-Za-z]{3})",  # Currency from
    "to_currency": r"(?:to currency)\s*(?:=|is|:)?\s*([A-Za-z]{3})",  # Currency to
    "country_code": r"(?:country|for)\s*(?:=|is|:)?\s*([A-Za-z]{2})",  # ISO country code
    "year": r"(?:year|for year|in year)\s*(?:=|is|:)?\s*(\d{4})"  # Year (YYYY)
}

 
# -------------------------------
# Language-to-Region Mapping
# -------------------------------

REGION_KEYWORDS = {
    "IN": ["india", "bharat", "hindustan", "भारतीय", "भारत"],
    "US": ["usa", "america", "united states", "us", "अमेरिका"],
    "AU": ["australia", "aus", "ऑस्ट्रेलिया"],
    "GB": ["uk", "united kingdom", "britain", "england", "ब्रिटेन"],
    "CA": ["canada", "कनाडा"],
    "SG": ["singapore", "सिंगापुर"],
    "FR": ["france", "फ्रांस"],
    "DE": ["germany", "जर्मनी"],
    "ES": ["spain", "स्पेन"],
    "IT": ["italy", "इटली"],
    "JP": ["japan", "जापान"],
    "CN": ["china", "चीन"],
    "BR": ["brazil", "ब्राज़ील"],
    "MX": ["mexico", "मेक्सिको"],
    "ZA": ["south africa", "दक्षिण अफ्रीका"],
    "AE": ["uae", "united arab emirates", "दुबई"],
    "RU": ["russia", "रूस"]
}

lang_region_map = {
    # English
    "en": "US",       # English → United States
    "en-gb": "GB",    # English (UK) → United Kingdom
    "en-us": "US",    # English (US) → United States

    # South Asian Languages (India)
    "hi": "IN",       # Hindi → India
    "bn": "IN",       # Bengali → India
    "ta": "IN",       # Tamil → India
    "te": "IN",       # Telugu → India
    "kn": "IN",       # Kannada → India
    "ml": "IN",       # Malayalam → India
    "mr": "IN",       # Marathi → India
    "ur": "IN",       # Urdu → India
    "pa": "IN",       # Punjabi → India
    "gu": "IN",       # Gujarati → India
    "or": "IN",       # Odia → India
    "as": "IN",       # Assamese → India
    "sd": "IN",       # Sindhi → India
    "sa": "IN",       # Sanskrit → India
    "ne": "NP",       # Nepali → Nepal
    "si": "LK",       # Sinhala → Sri Lanka

    # European Languages
    "fr": "FR",       # French → France
    "de": "DE",       # German → Germany
    "es": "ES",       # Spanish → Spain
    "it": "IT",       # Italian → Italy
    "pt": "PT",       # Portuguese → Portugal
    "pt-br": "BR",    # Portuguese (Brazil) → Brazil
    "es-419": "MX",   # Spanish (LatAm) → Mexico
    "es-mx": "MX",    # Spanish (Mexico) → Mexico
    "nl": "NL",       # Dutch → Netherlands
    "pl": "PL",       # Polish → Poland
    "cs": "CZ",       # Czech → Czech Republic
    "hu": "HU",       # Hungarian → Hungary
    "ro": "RO",       # Romanian → Romania
    "el": "GR",       # Greek → Greece
    "da": "DK",       # Danish → Denmark
    "sv": "SE",       # Swedish → Sweden
    "fi": "FI",       # Finnish → Finland
    "no": "NO",       # Norwegian → Norway
    "ru": "RU",       # Russian → Russia
    "uk": "UA",       # Ukrainian → Ukraine

    # East & Southeast Asian Languages
    "zh": "CN",       # Chinese (generic) → China
    "zh-cn": "CN",    # Chinese (Simplified) → China
    "zh-tw": "CN",    # Chinese (Traditional) → China
    "ja": "JP",       # Japanese → Japan
    "ko": "KR",       # Korean → South Korea
    "vi": "VN",       # Vietnamese → Vietnam
    "th": "TH",       # Thai → Thailand
    "id": "ID",       # Indonesian → Indonesia
    "ms": "MY",       # Malay → Malaysia
    "my": "MM",       # Burmese → Myanmar
    "km": "KH",       # Khmer → Cambodia
    "lo": "LA",       # Lao → Laos
    "mn": "MN",       # Mongolian → Mongolia
    "tl": "PH",       # Tagalog (Filipino) → Philippines

    # Middle Eastern Languages
    "ar": "AE",       # Arabic → UAE
    "he": "IL",       # Hebrew → Israel
    "fa": "IR",       # Persian (Farsi) → Iran
    "ku": "IQ",       # Kurdish → Iraq

    # African Languages
    "zu": "ZA",       # Zulu → South Africa
    "af": "ZA",       # Afrikaans → South Africa
    "xh": "ZA",       # Xhosa → South Africa
    "sw": "KE",       # Swahili → Kenya
    "am": "ET",       # Amharic → Ethiopia
    "ig": "NG",       # Igbo → Nigeria
    "yo": "NG",       # Yoruba → Nigeria
    "ha": "NG",       # Hausa → Nigeria
}



def extract_params(text):
    if not isinstance(text, str):
        raise ValueError("Input to extract_params must be a string.")

    params = {}

    # Check for DATA_FETCH format
    if text.strip().lower().startswith("data_fetch:"):
        fetch_match = re.match(r"data_fetch:\s*(\w+):\s*(.*)", text.strip(), re.IGNORECASE)
        if fetch_match:
            _, param_str = fetch_match.groups()
            param_pairs = [p.strip() for p in param_str.split(",") if "=" in p]
            for pair in param_pairs:
                key, val = pair.split("=", 1)
                key = key.strip()
                val = val.strip()
                if val.replace('.', '', 1).isdigit():
                    val = float(val)
                params[key] = val
        return params

    # Standard formula extraction
    for param, pattern in PARAM_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1)
            if val:
                try:
                    val_float = float(val)
                    if param in [
                        "r", "rate_per_period", "discount_rate", "risk_free_rate",
                        "Re", "Rd", "Tc", "markup_percentage",
                        "percent_change_quantity", "percent_change_price",
                        "percent_change_quantity_supplied", "market_return"
                    ]:
                        if val_float > 1:
                            val_float /= 100
                    params[param] = val_float
                except Exception:
                    pass
    return params



# -------------------------------
# Region Detection Function
# -------------------------------

def detect_region(user_text, detected_lang_code=None):
    """
    Detect region from user_text via keywords.
    Fallback to region via detected language.
    Default is 'US'.
    """
    text = user_text.lower()
    for region, keywords in REGION_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return region.upper()
    
    if detected_lang_code:
        region = lang_region_map.get(detected_lang_code.lower())
        if region:
            return region.upper()

    return "US"  # default fallback


# -------------------------------
# Detect Intent from Gemini
# -------------------------------

def detect_intent_from_keywords(text):
    text = text.lower()
    for formula, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return formula
    return None


# -------------------------------
# Formula Intent from Gemini
# -------------------------------

# Safe evaluation for math expressions
def safe_eval_expr(expr):
    operators = {
        ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
        ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg
    }

    def _eval(node):
        if isinstance(node, ast.Num): return node.n
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub): return -_eval(node.operand)
        elif isinstance(node, ast.BinOp): return operators[type(node.op)](_eval(node.left), _eval(node.right))
        else: raise ValueError("Unsupported expression")

    try:
        node = ast.parse(expr, mode='eval').body
        return _eval(node)
    except Exception:
        return expr  # fallback to raw string

# --- Main function ---

def get_formula_intent_from_gemini(user_question: str):
    try:
        formula_keys_list = ", ".join(INTENT_KEYWORDS.keys())
        prompt = (
            f"""
You are a finance/economics assistant. Given a user question, your job is to detect the **intent** and respond in ONE of these **three exact formats**:

1️⃣ If it's a theoretical/explanatory question (no formula or API needed), reply with:
THEORETICAL

2️⃣ If it's a computational query requiring a formula, reply with:
FORMULA: <formula_key>: param1 = value1, param2 = value2, ...

3️⃣ If it's a data-fetch request (e.g., stock price, currency rate, inflation), reply with corresponding company stock symbol:
DATA_FETCH: <function_key>: param1 = value1, param2 = value2, ...

Use formula or function keys only from this list:
{formula_keys_list}

⚠️ Follow strictly:
- Extract all required parameters from the question.
- Use correct variable names like P, r, n, t for compound interest.
- For data fetchers (like stock/currency), detect company name, currency codes, etc.
- If the user mentions a company name, the parameter is company name for stock data de

User Question:
{user_question}
"""
        )

        chat = model.start_chat(history=[])
        response = chat.send_message(prompt)
        rephrased = response.text.strip()
        print(f"--- Gemini rephrased output:\n{rephrased}")

        # Case 1: THEORETICAL
        if rephrased.lower() == "theoretical":
            return "theoretical", None, rephrased

        # Case 2 or 3: FORMULA or DATA_FETCH
        match = re.match(r"(FORMULA|DATA_FETCH):\s*(\w+):", rephrased, re.IGNORECASE)
        if not match:
            return "theoretical", None, rephrased

        intent_type = match.group(1).lower()
        formula_key = match.group(2).lower()

        if formula_key not in INTENT_KEYWORDS:
            return "theoretical", None, rephrased

        return intent_type, formula_key, rephrased

    except Exception as e:
        print(f"⚠️ Error in Gemini rephrase intent: {e}")
        return "theoretical", None, user_question


# -------------------------------
# Final Updated Parser
# -------------------------------

def parse_user_query(user_text: str, detected_lang_code: str | None = None):
    """
    Main parsing function.

    Returns tuple:
        (is_theoretical: bool,
         formula: str|None,
         params: dict,
         region: str)
    """


     # Step 1: Detect user region from original text & lang code
    region = detect_region(user_text, detected_lang_code)

    # Step 2: Determine formula intent or theoretical using Gemini
    intent_type, formula, rephrased = get_formula_intent_from_gemini(user_text)
    if intent_type == "theoretical":
        return True, None, {}, region
    elif intent_type == "data_fetch":
        return False, formula, extract_params(rephrased), region  # Mark this specially downstream
    elif intent_type == "formula":
        return False, formula, extract_params(rephrased), region

