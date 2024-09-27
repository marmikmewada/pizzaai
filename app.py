from flask import Flask, request, jsonify
import random
import re

app = Flask(__name__)

# Pizza menu data
pizzas = [
    {"name": "Margherita", "sizes": ["Small", "Medium", "Large"], "prices": [8, 12, 16]},
    {"name": "Pepperoni", "sizes": ["Small", "Medium", "Large"], "prices": [9, 13, 17]},
    {"name": "Veggie", "sizes": ["Small", "Medium", "Large"], "prices": [8, 12, 16]},
    {"name": "BBQ Chicken", "sizes": ["Medium", "Large"], "prices": [14, 18]},
    {"name": "Hawaiian", "sizes": ["Medium", "Large"], "prices": [14, 18]},
]

offers = [
    "Buy one Margherita pizza and get a second for 50% off!",
    "Get a free drink with any large pizza order!",
    "Order two medium pizzas and save $5!",
]

def get_pizza_list():
    return ", ".join([pizza['name'] for pizza in pizzas])

def get_pizza_details(pizza_name):
    for pizza in pizzas:
        if pizza['name'].lower() == pizza_name.lower():
            sizes = ', '.join(pizza['sizes'])
            prices = ', '.join(f"{size}: ${price}" for size, price in zip(pizza['sizes'], pizza['prices']))
            return (f"Our {pizza['name']} pizza is available in sizes: {sizes}. "
                    f"Prices are: {prices}.")
    return None

def parse_input(input_text):
    input_lower = input_text.lower()
    keywords = {
        "greeting": re.search(r'\b(hi|hello|hey|greetings|morning|afternoon|evening)\b', input_lower),
        "pizza": re.search(r'\bpizza\b', input_lower),
        "offer": re.search(r'\b(offer|promotion|deal)\b', input_lower),
        "size": re.search(r'\b(size|sizes|price|prices)\b', input_lower),
        "recommend": re.search(r'\brecommend\b', input_lower),
        "order": re.search(r'\border\b', input_lower),
        "customize": re.search(r'\b(custom|customize)\b', input_lower),
        "topping": re.search(r'\b(topping|toppings)\b', input_lower),
        "vegan": re.search(r'\b(vegan|vegetarian)\b', input_lower),
        "thank": re.search(r'\b(thank|thanks)\b', input_lower),
        "confirm_order": re.search(r'\b(order|confirm|yes|okay|sure)\b', input_lower),
        "cancel_order": re.search(r'\b(cancel|no|stop)\b', input_lower),
    }
    return keywords

def generate_response(keywords, current_order=None):
    if keywords['greeting']:
        return "Hello! Welcome to Pizza Today! How can I assist you with your pizza cravings today?"

    if keywords['thank']:
        return "You're welcome! If you have any other questions or need help, just let me know!"

    if keywords['recommend']:
        recommended_pizza = random.choice(pizzas)
        return (f"I recommend the {recommended_pizza['name']} pizza! "
                f"It’s available in sizes: {', '.join(recommended_pizza['sizes'])}. "
                f"Prices start at ${recommended_pizza['prices'][0]}.")

    if keywords['offer']:
        return random.choice(offers)

    if keywords['size']:
        return (f"We offer the following pizzas: {get_pizza_list()}. "
                "Sizes available are Small, Medium, and Large, with prices ranging from $8 to $18.")

    if keywords['customize']:
        return "You can customize your pizza with different toppings. What toppings would you like?"

    if keywords['topping']:
        return "We have a variety of toppings! You can choose from pepperoni, mushrooms, onions, olives, and more. What would you like on your pizza?"

    if keywords['vegan']:
        return "We have great vegetarian options like the Veggie pizza. Would you like to hear more about it?"

    if keywords['pizza']:
        return "What specific pizza would you like to know about? You can ask for recommendations or available offers."

    if keywords['order']:
        return "Great! What pizza would you like to order? Please specify the type and size."

    if current_order:
        if keywords['confirm_order']:
            return f"Your order for {current_order['size']} {current_order['name']} pizza has been placed! Thank you!"
        if keywords['cancel_order']:
            return "Your order has been canceled. Let me know if you'd like to order something else!"

    return "I'm here to help! You can ask me about our pizzas, offers, sizes, or even customize your order."

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    input_text = data.get('input', '').strip()

    if not input_text:
        return jsonify({'response': "Welcome to Pizza Today! Here’s our menu: " + get_pizza_list()})

    # Check if the input matches a specific pizza request
    pizza_response = get_pizza_details(input_text)
    if pizza_response:
        return jsonify({'response': pizza_response})

    # Parse the input to identify keywords
    keywords = parse_input(input_text)

    # Handle current order context
    current_order = None
    if 'order' in keywords and keywords['pizza']:
        pizza_name = next((pizza['name'] for pizza in pizzas if pizza['name'].lower() in input_text.lower()), None)
        size = re.search(r'\b(small|medium|large)\b', input_text.lower())
        if pizza_name and size:
            current_order = {"name": pizza_name, "size": size.group(0).capitalize()}

    # Generate a response based on the identified keywords
    response = generate_response(keywords, current_order)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
