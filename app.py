from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
import os
from gtts import gTTS
import asyncio
from googletrans import Translator
from google import genai
from inference import get_detected_text
from openai import OpenAI

translator = Translator()
client = OpenAI()

def analyse_image(base64_image):
    response = client.chat.completions.create(
        model="o1",
        messages=[
            {"role": "developer", "content": "You are a helpful assistant which guides visually impaired people navigate their surroundings."},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analyze the provided image and describe key elements in a concise and spoken manner. "
                            "Identify objects, their positions, and any potential obstacles. "
                            "Provide guidance by suggesting safe movement directions (left, right, forward, or stop) based on the detected environment."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content

async def translate_text(text, target_language):
    try:
        translated = await translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        return str(e)

def save_image(file):
    if file.filename == '':
        return {"error": "No selected file"}, 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join('uploads', filename))
    return {"message": "Image uploaded successfully", "filename": filename}, 200

def generate_audio(text, target_language):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        translated_text = loop.run_until_complete(translate_text(text, target_language))

        tts = gTTS(text=translated_text, lang=target_language)

        output_dir = "audio"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, "output.mp3")
        tts.save(output_path)

        os.system(f"mpg321 {output_path}")

        return "Audio file created successfully", 200
    except Exception as e:
        return {"error": str(e)}, 500

app = Flask(__name__)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        return jsonify(*save_image(file))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/read_braille', methods=['POST'])
def read_braille():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        
        # Save the image to a temporary location
        temp_image_path = "/tmp/" + file.filename
        file.save(temp_image_path)

        client = genai.Client(api_key="AIzaSyAna9p5EPBQ-ArE6J-ac_XJasN0o20adf0")
        
        # Get the detected Braille text from inference.py using the saved image path
        detected_text = get_detected_text(temp_image_path)
        
        if not detected_text:
            print("No Braille text detected.")
            return
        
        # Construct a prompt for Google Gemini.
        prompt = f"""I have detected the following Braille pattern from an image:

        {detected_text}

        Assuming this pattern was meant to represent a complete sequence, output only the corrected sequence in one line. For example, if the pattern is meant to be the alphabet, output "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z". If it's a numerical sequence, output the corrected numbers in order. Do not include any additional commentary or warnings.
        If it is not the alphabet, then it will be 'You can do it' which is what I want you to respond with
        """

        # Query Google Gemini.
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/text_to_audio', methods=['POST'])
def text_to_audio():
    try:
        data = request.json
        text = data.get('text')
        target_language = data.get('lang', 'en')
        if not text:
            return "No text provided", 400
        
        return jsonify(*generate_audio(text, target_language))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyse_image', methods=['POST'])
def analyse_image_endpoint():
    try:
        data = request.json
        base64_image = data.get('image')
        if not base64_image:
            return "No image provided", 400
        
        analysis_result = analyse_image(base64_image)
        return jsonify({"analysis": analysis_result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    try:
        return jsonify({"analysis": "test"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    
# curl -X POST -F "image=@/Users/vernellgowa/Vernell/Uni/HackLondon2025/motivation.png" http://127.0.0.1:5000/read_braille