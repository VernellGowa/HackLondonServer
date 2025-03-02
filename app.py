from flask import Flask, jsonify, request
import os
from inference import get_detected_text
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

# async def translate_text(text, target_language):
#     try:
#         translated = await translator.translate(text, dest=target_language)
#         return translated.text
#     except Exception as e:
#         return str(e)

# def save_image(file):
#     if file.filename == '':
#         return {"error": "No selected file"}, 400
    
#     filename = secure_filename(file.filename)
#     file.save(os.path.join('uploads', filename))
#     return {"message": "Image uploaded successfully", "filename": filename}, 200

app = Flask(__name__)

@app.route('/read_braille', methods=['POST'])
def read_braille():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        temp_image_path = "/tmp/" + file.filename
        file.save(temp_image_path)

        detected_text = get_detected_text(temp_image_path)
        
        return jsonify({"response": detected_text}) if detected_text else jsonify({"error": "No text detected"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/read_braille_ai', methods=['POST'])
def read_braille_ai():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        
        # Save the image to a temporary location
        temp_dir = "tmp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        temp_image_path = os.path.join(temp_dir, file.filename)
        file.save(temp_image_path)

        get_detected_text(temp_image_path)

        response = client.chat.completions.create(
            model="o1",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant which translates annotated Braille text to spoken language."},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Analyze the provided image and output the Braille text. " ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://hacklondon-897572133117.us-central1.run.app/braille/" + file.filename,
                            },
                        },
                    ],
                }
            ],
        )
        text = response.choices[0].message.content
        print(text)
        
        if not text:
            return jsonify({"error": str(e)}), 500
        
        return jsonify({"response": text})
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


if __name__ == '__main__':
    # port = int(os.environ.get("PORT", 8080))  # Use Cloud Run's port
    # app.run(host='0.0.0.0', port=port)
    app.run(host='0.0.0.0')
    
# curl -X POST -F "image=@/Users/vernellgowa/Vernell/Uni/HackLondon2025/alphabet.png" http://127.0.0.1:5000/read_braille

# curl -X POST -F "image=@/Users/vernellgowa/Vernell/Uni/HackLondon2025/alphabet.png" https://hacklondon-897572133117.us-central1.run.app/read_braille

# curl -X POST -F "image=@/Users/vernellgowa/Vernell/Uni/HackLondon2025/alphabet.png" https://hacklondon-897572133117.us-central1.run.app/analyse_image

# 