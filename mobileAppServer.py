from flask import Flask, request, jsonify,render_template,redirect,url_for,session
from housegan_integration.newtest import from_server,finall
import google.generativeai as genai
import re
import os
import faiss_mode
import shutil
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

IMAGE_FOLDER = os.path.join("static", "images")
MOBILEAPP_IMAGE_FOLDER=r"D:\Arun\learning\app_development\flutter_learn\assets\images"
  

session=[]
room_list=[]
# Configure Google Generative AI
genai.configure(api_key="AIzaSyAoQFy4vYDU5bjsZcCKPduf02hSCXFT8UY")
model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
chat = model.start_chat(history=[])

base_prompt='''
    You are a Floorplan Assistant.
    Now you are going to design a floorplan as per the user interaction.
    Keep the conversation simple and need not to explain about things in detail.
    This is one of my chat with you, make sure that you maintain in same pattern:
    based on the user interaction respond appropriately but make sure that it is simple and clear.
    Dont consider this as inital chat it is just for your reference.
    User: add a bedroom
    Bot: What is the location of the bedroom? (Example: Northeast corner/North corner)
    What is the dimension of the bedroom? (Example: 15x15 or 15x12)
    User: location of bedroom is northeast corner
    Bot: What is the dimension of the bedroom? (Example: 15x15 or 15x12)
    User: 15x15
    Bot: Okay, I will add a bedroom to the northeast corner of the floorplan with dimensions of 15x15. Is there anything else I can help you with today?
    User: can i include one more room
    Bot: Yes, you can include one more room. What type of room would you like to add?
    User: i want a kitchen
    Bot: What is the location of the kitchen? (Example: Northeast corner/North corner)
    User: south
    Bot: What is the dimension of the kitchen? (Example: 15x15 or 15x12)
    User: 12x12
    Bot: Okay, I will add a kitchen to the south of the floorplan with dimensions of 12x12. Is there anything else I can help you with today?
    User: dome
    Bot: I'm sorry, I don't understand what you mean by "dome". Can you please rephrase your request?
    User: done
    Only remember the response method of those chat no need to remmeber these text.
    Just greet user hi etc.. . 
    Need not to respond for this prompt.

'''

tuning_prompt = '''
        The user requies to add an amininty(Balcony/ Living Room/Common room/Bed Room/Master Room/ Bathroom/Kitchen etc..) to 
        the floorplan.
        For each of the you should ask these two questions one by one:
        What is the location of the <aminity> (Example: Nort east corner/North corner)?
        What is the dimension of the <aminity> (Example: 15x15 or 15x12)?
        Ask only the two questions, do not add any other content to it.
        Ask the above questions one by one to the user not all at the same time.
        Do not ask/respond anything unwanted and extra things other than that what i said you to ask.
        If user did not mention location or dimension of any <aminity> you assign some random location and dimension based on
        your knowledge.And respond with the value that you have filled for that particular <aminity>.
        user input:
        '''


final_prompt='''
            Have the final updated floorplan instruction in this format:
            I will add <aminities given by user> to the <location of each aminity>
            of the floorplan with dimensions of <dimension of each aminity>.
            Repeat the same pattern for all aminities
            Just give the in this format alone need not mention any other things.
'''

floorplan_instruction = ""


@app.route('/')
def index():
    start_chat()
    return jsonify({"reply":True})

@app.route('/start', methods=['GET'])
def start_chat():
    try:
        response = chat.send_message(base_prompt)
        bot_reply = response.candidates[0].content.parts[0].text.strip()
        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/message', methods=['POST'])
def send_message():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    input_to_bot = tuning_prompt + user_message
    try:
        response = chat.send_message(input_to_bot)
        agent_reply = response.candidates[0].content.parts[0].text.strip()
        return jsonify({"reply": agent_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/finalize', methods=['GET'])
def finalize_instructions():
    try:
        response = chat.send_message(final_prompt)
        bot_reply = response.candidates[0].content.parts[0].text.strip()
        print(bot_reply)
        session.clear() 
        room_list.clear()
        pattern = r"add a ([\w\s]+) to the (.*?) of the floorplan with dimensions of (\d+x\d+)"
        matches = re.findall(pattern, bot_reply)
        global floorplan_instruction
        for room, location, dimensions in matches:
            session.append(room)
            room_list.append(room)
            floorplan_instruction += f"{room.capitalize()} with dimension {dimensions} at location {location}\n"

        # if len(session)<6:
        #     print(session)
        #     remaining=6-len(session)
        #     return jsonify({
        #     "reply": f"You have added {len(session)} rooms. Please add {remaining} more room(s) to complete the floorplan."
        #     })
        return jsonify({"reply":"success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/layout_retrieval', methods=['POST'])
def layout_retrieval():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400
        nodes = data.get("nodes")
        edgesdata = data.get("edges")

        n=len(edgesdata)
        for i in range(n):
            nodes.append(16)
        nodes.append(14)
        # from_server(nodes,edgesdata)
        print(nodes)
        print(edgesdata)
        finall()
        return jsonify({"reply":"success"})
    
    except Exception as e:
        return jsonify({"reply": str(e)}), 500
    


@app.route('/display_images')
def display_images():

    if floorplan_instruction=="":
        user_instruction="It would be good to have a common room . I would like to place common room at the north side of the apartment. The common room should be around 200 sqft with the aspect ratio of 3 over 4. The common room should have an en-suite bathroom. The common room should be next to the bathroom, kitchen, balcony. The bathroom should be considered. Place bathroom at the south side of the apartment. Make bathroom around 50 sqft with the aspect ratio of 7 over 8. The bathroom can be used by guest. The bathroom connects to the common room, master room, living room. Make a kitchen . The kitchen should be at the south side of the apartment. Make kitchen approx 50 sqft with the aspect ratio of 7 over 4. The kitchen attaches to the common room, balcony, master room, living room. Can you make a balcony ? I would like to place balcony at the south side of the apartment. Can you make balcony around 50 sqft with the aspect ratio of 5 over 2? The balcony is private. The balcony connects to the common room, kitchen, master room. The master room should be considered. The master room should be at the south side of the apartment. Make master room approx 150 sqft with the aspect ratio of 4 over 5. The master room should have an en-suite bathroom. The master room should be next to the bathroom, kitchen, balcony. It would be great to have a living room . Make living room around 650 sqft with the aspect ratio of 1 over 2."

    user_instruction=floorplan_instruction
    print(user_instruction)
    rl, dl, sl = faiss_mode.retrieve_top_images_from_text(user_instruction)    # here we need to give floorplan instruction

    images_info = [
    {
        "filename": f"images/img{i+1}.png",
        "rank": int(rl[i]),
        "distance": round(float(dl[i]), 3),  
        "similarity": round(float(sl[i]), 3) 
    }
        for i in range(len(rl))
    ]
    shutil.copytree(IMAGE_FOLDER, MOBILEAPP_IMAGE_FOLDER,dirs_exist_ok=True)
    
    return jsonify({"reply":"success","images_info":images_info})

if __name__ == '__main__':
    app.run(debug=True)