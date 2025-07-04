import os
import gradio as gr
import requests
import re
from intent_detection import parse_user_query
from econ_compute import execute_formula
from gemini_module import ask_gemini_explainer
from data_fetcher_utils import auto_fetch_live_data
from langdetect import detect

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

chat_session = None

def translate_to_english(text):
    if not HF_API_TOKEN:
        return text, "en"

    try:
        lang_code = detect(text)  # e.g., 'fr' for French
    except:
        lang_code = "en"

    API_URL = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-mul-en"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": text}

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        translated = response.json()
        if isinstance(translated, list) and 'translation_text' in translated[0]:
            return translated[0]['translation_text'], lang_code
        if isinstance(translated, list) and 'generated_text' in translated[0]:
            return translated[0]['generated_text'], lang_code
    except Exception:
        pass

    return text, lang_code  # return detected language anyway



def is_formula_line(line):
    # Consider a line formula if it has math symbols and mostly numbers, letters, whitespace,
    # but no typical sentence punctuation like commas, colons, or parentheses
    math_symbols = ['=', '+', '-', '*', '/', '^', '%']
    # If line contains math symbols
    if any(sym in line for sym in math_symbols):
        # Check if line contains no commas or parentheses or colons (sentence punctuation)
        if not any(punct in line for punct in [',', '(', ')', ':', ';']):
            # Also ensure mostly alphanumeric + math symbols
            if re.fullmatch(r'[\w\s=+\-*/^%]*', line):
                return True
    return False

def translate_from_english(text, target_lang_code):
    if not HF_API_TOKEN or target_lang_code == "en":
        return text  # No translation needed or no token

    lines = text.split('\n')
    translated_lines = []

    model_name = f"Helsinki-NLP/opus-mt-en-{target_lang_code}"
    API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    for line in lines:
        if line.strip() == "":
            translated_lines.append(line)
            continue

        if is_formula_line(line):
            # Preserve formula line as is
            translated_lines.append(line)
        else:
            # Translate this text line
            payload = {"inputs": line, "options": {"wait_for_model": True}}
            try:
                response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                translated = response.json()
                if isinstance(translated, list) and 'translation_text' in translated[0]:
                    translated_lines.append(translated[0]['translation_text'])
                elif isinstance(translated, list) and 'generated_text' in translated[0]:
                    translated_lines.append(translated[0]['generated_text'])
                else:
                    translated_lines.append(line)  # fallback to original line
            except Exception:
                # Fallback: add notice and original line
                fallback_msg = ("\n\n(Note: Sorry, I couldn't translate the response back to your language, so here is the answer in English.)")
                translated_lines.append(line + fallback_msg)

    return "\n".join(translated_lines)


def econosage_chat(user_input, history):
    global chat_session

    # Step 1: Translate user query to English
    english_input, lang_code = translate_to_english(user_input)
    print(f"Translated input: {english_input}") 

    # Step 2: Extract theory/computation intent, formula (if any), params, and region
    is_theoretical, formula, params, region = parse_user_query(
        user_text=english_input,
        detected_lang_code=lang_code
    )
    print(f"Parsed formula: {formula}, params: {params}") 
    # Step 3: Handle theoretical/explanatory queries
    if is_theoretical:
        response, chat_session = ask_gemini_explainer(
            user_question=user_input,
            history_session=chat_session
        )
    
    # Step 4: Handle formula-based computational queries
    elif formula:
        try:
            params.setdefault("region", region)
            print(f"Params before live data fetch: {params}")
            params = auto_fetch_live_data(params)
            print(f"Params after live data fetch: {params}") 
            result, formula_str = execute_formula(formula, params)
	    
            response, chat_session = ask_gemini_explainer(
                user_question=user_input,
                computed_result=str(result),
                formula_used=formula_str,
                history_session=chat_session
            )
            if "retrieved from" in formula_str.lower():
                response = f"{formula_str}\n\n{response}"

        except AttributeError as e:
            if "not found" in str(e).lower() or "has no attribute" in str(e).lower():
                response, chat_session = ask_gemini_explainer(
                    user_question=user_input,
                    history_session=chat_session
                )
            else:
                response = f"❌ Error: {str(e)}"

        except Exception as e:
            error_msg = str(e)
            if "missing" in error_msg and "positional arguments" in error_msg:
                import re
                missing_params = re.findall(r"'(\w+)'", error_msg)
                if missing_params:
                    missing_str = ", ".join(missing_params)
                    response = (f"Could you please provide the following missing parameter"
                                f"{'s' if len(missing_params) > 1 else ''}: {missing_str}? "
                                "Once I have those, I'll be happy to help you with the calculation.")
                else:
                    response = f"❌ Error during calculation: {error_msg}"
            else:
                response = f"❌ Error during calculation: {error_msg}"

    # Step 5: If Gemini couldn’t map it, still try to explain
    else:
        response, chat_session = ask_gemini_explainer(
            user_question=user_input,
            history_session=chat_session
        )

    # Step 6: Translate final response back to original language
    print(f"Translating from English to {lang_code}")
    print(f"Original English: {response}")
    final_response = translate_from_english(response, lang_code)
    print(f"Hugging Face response: {final_response}")
    return final_response

# Gradio UI setup with polished branding and diverse examples
chat_interface = gr.ChatInterface(
    fn=econosage_chat,
    title="💡 EconoSage | Smarter Finance, Anywhere — Ask. Calculate. Learn.",
    description=(
    "### 💡 **EconoSage**  \n"
    "Your multilingual AI tutor for finance & economics. Ask questions or run real-time calculations — from anywhere, in any language.\n\n"
    "**Try queries like:**  \n"
    "What is inflation? | Calculate compound interest: P=5000, r=5%, t=2, n=4 | Stock price of Apple | ¿Cuál es el tipo de cambio de USD a EUR? | Inflation rate for India in 2023 | Prix de l'action de Tesla"
    ),
    examples=[
        "What is inflation and how does it affect consumers?",
        "Calculate compound interest: P=5000, r=5%, t=3 years, n=4",
        "Break-even point if fixed cost is 1000, price per unit is 20, variable cost per unit is 5",
        "Explain GDP growth rate with example",
        "¿Qué es la inflación?",
        "Wie berechnet man den ROI?",
        "Prix de l'action de Tesla",
        "株価を教えてください"
    ],
    theme="soft",
    cache_examples=False
)


if __name__ == "__main__":
    chat_interface.launch()
