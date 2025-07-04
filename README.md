Inspiration
I wanted to create a smart and friendly assistant that makes economics and finance easy to understand for everyone — whether you're a student, a professional, or just curious about how the economy works. Inspired by the complexity of real-world economic decisions and the lack of accessible tools, I built EconoSage to bring clarity, transparency, and interactive learning to economics through AI.

What it does
EconoSage is my economic sidekick that can:

Explain complex economic concepts like inflation, interest rates, and ROI in simple language
Fetch real-time financial data such as stock prices, currency exchange rates, and inflation figures
Simulate how policy changes impact markets and everyday finances
Answer your questions with step-by-step explanations and clear formulas
Converse in multiple languages, making global economics accessible to all
How I built it
I combined cutting-edge technologies to build EconoSage:

A Python Flask backend powers the core logic, handling conversations, computations, and data retrieval
Integration with Google’s Gemini Pro API allows natural and precise language understanding and generation
Live financial data is fetched dynamically from trusted sources like Yahoo Finance and the World Bank
My modular calculation engine hosts over 40 economic formulas, making computations accurate and reusable
The frontend uses Streamlit deployed on Hugging Face Spaces to provide an interactive, browser-based chat experience
Challenges I ran into
Building EconoSage wasn’t without hurdles:

Turning everyday language into precise numbers and formulas was tricky — I needed to handle vague or incomplete inputs gracefully
Managing multiple real-time data sources meant dealing with inconsistent formats and occasional missing data
Ensuring the AI gave consistent and reliable answers required careful prompt engineering and deterministic settings
Balancing technical accuracy with simple, clear explanations was a constant challenge
Supporting multiple languages while keeping numeric accuracy and context intact took extra effort
Accomplishments I’m proud of
Successfully bridging complex economic theory with an easy-to-use chatbot interface
Developing a robust modular system that seamlessly ties language understanding, data fetching, and financial calculations
Creating near-deterministic AI outputs by fine-tuning prompts and controlling model parameters
Deploying a fully functional web app that users can access instantly without setup or installs
Building a flexible foundation that can easily scale to include more economic domains and languages
What I learned
The importance of carefully parsing user input to extract meaningful and correct parameters
How to integrate multiple external data sources dynamically and handle data quality issues
Strategies for controlling large language model behavior to produce consistent and factual answers
How modular, reusable code architectures simplify adding new features and maintaining complex projects
The value of clear communication and explanation, especially when dealing with technical topics
What’s next for EconoSage
Expanding simulation capabilities to include more policies and economic indicators
Adding personalized financial advice and planning tools based on user input
Enhancing multilingual conversation quality and expanding language support
Integrating more real-time data feeds for broader market coverage
Developing mobile and voice assistant versions for greater accessibility
