import data_fetcher  # your existing module
import inspect

DATA_FETCHER_MAPPING = {
    "get_stock_price": {
        "func": data_fetcher.get_stock_price,
        "args": ["symbol", "date", "target_currency", "country", "region"],  # match your function's parameters
        "output_param": "stock_price"
    },
    "get_currency_rate": {
        "func": data_fetcher.get_currency_rate,
        "args": ["from_currency", "to_currency"],
        "output_param": "currency_rate"
    },
    "get_inflation_rate": {
        "func": data_fetcher.get_inflation_rate,
        "args": ["country", "year"],
        "output_param": "inflation_rate"
    },
    "get_gst_rate": {
        "func": data_fetcher.get_gst_rate,
        "args": ["country"],
        "output_param": "gst_rate"
    }
}


# ✅ Generalized safe call using only required args (positional)
def _call_data_fetcher(func, params, required_args):
    """
    Safely calls the fetch function using only required positional arguments.
    """
    func_args = [params[arg] for arg in required_args]
    return func(*func_args)


def auto_fetch_live_data(params):
    updated_params = dict(params)
    for key, fetch_info in DATA_FETCHER_MAPPING.items():
        func = fetch_info["func"]
        required_args = fetch_info["args"]
        output_key = fetch_info["output_param"]

        if all(arg in updated_params and updated_params[arg] is not None for arg in required_args):
            try:
                fetched_value = _call_data_fetcher(func, updated_params, required_args)
                updated_params[output_key] = fetched_value
            except Exception as e:
                print(f"[Warning] Data fetch failed for '{key}': {e}")
    return updated_params