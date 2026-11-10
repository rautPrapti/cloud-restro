from django.conf import settings
from google import genai


def get_food_recommendation(preference, foods):

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    menu = []

    for food in foods:
        menu.append(
            f"Name: {food.name}, "
            f"Category: {food.category.name}, "
            f"Price: Rs. {food.price}"
        )

    prompt = f"""
    You are the food recommendation assistant for Cloud Restro.

    The customer wants: {preference}

    Here is our available menu:
    {chr(10).join(menu)}

    Recommend suitable food items only from this menu.
    Do not invent food items or prices.
    Explain briefly why each recommendation matches
    the customer's preference.
    Be friendly and helpful.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text