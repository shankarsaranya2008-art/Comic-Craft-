import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY is missing.")
    raise SystemExit(1)

print("API key found.")
print("Testing Gemini image generation...")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.1-flash-image",
    contents=(
        "Create a single comic-book illustration of a friendly robot "
        "discovering a beautiful hidden garden inside a futuristic "
        "laboratory. Bright colorful comic art, expressive character, "
        "detailed background, no text."
    ),
)

saved = False

for part in response.parts:

    if part.inline_data is not None:

        image = part.as_image()

        image.save("gemini_test_image.png")

        print("SUCCESS!")
        print("Image saved to:")
        print("gemini_test_image.png")

        saved = True
        break

if not saved:
    print("Gemini returned no image.")
    print("Response:")
    print(response)