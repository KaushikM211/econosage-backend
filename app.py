import gradio as gr
from intent_detection import parse_user_query
from econ_compute import execute_formula
from gemini_module import ask_gemini_explainer

chat_session = None

def econosage_chat(user_input, history):
    global chat_session

    formula, params = parse_user_query(user_input)
    print("Detected formula:", formula)
    print("Extracted params:", params)

    if formula:
        try:
            # Try local calculation
            result, formula_str = execute_formula(formula, params)

            # Send computed result to Gemini for explanation
            response, chat_session = ask_gemini_explainer(
                user_question=user_input,
                computed_result=str(result),
                formula_used=formula_str,
                history_session=chat_session
            )

        except AttributeError as e:
            # Function not found in econ_compute
            if "not found" in str(e).lower() or "has no attribute" in str(e).lower():
                # Fallback: Ask Gemini to calculate & explain fully
                response, chat_session = ask_gemini_explainer(
                    user_question=user_input,
                    history_session=chat_session
                )
            else:
                # Other attribute errors
                response = f"❌ Error: {str(e)}"

        except Exception as e:
            error_msg = str(e)

            # Check if error is missing parameters
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

    else:
        # No formula detected - general question, ask Gemini directly
        response, chat_session = ask_gemini_explainer(
            user_question=user_input,
            history_session=chat_session
        )

    return response

# Use HTML in the description to show your logo above the chat
chat_interface = gr.ChatInterface(
    fn=econosage_chat,
    title="💼 EconoSage: Your AI Finance & Economics Tutor",
    description=(
        "<div style='display:flex;align-items:center;gap:10px;'>"
        "<img src='file/EconoSage_logo.svg' style='height:48px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.12);'/>"
        "<span style='font-size:1.5em;color:#ffd700;font-weight:700;'>EconoSage</span>"
        "</div>"
        "<br>Ask me finance or economics questions. Try things like 'What is inflation?' or 'Calculate compound interest with P=5000, r=5%, t=2, n=4'."
    ),
    examples=[
        "What is inflation and how does it affect consumers?",
        "Calculate compound interest: P=5000, r=5%, t=3 years, n=4",
        "Break-even point if fixed cost is 1000, price per unit is 20, variable cost per unit is 5",
        "Explain GDP growth rate with example",
    ],
    theme="soft",
    cache_examples=False
)

if __name__ == "__main__":
    chat_interface.launch()
