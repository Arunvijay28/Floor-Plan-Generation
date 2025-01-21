import os
import re
import google.generativeai as genai

genai.configure(api_key="AIzaSyCCGwlZGlWzLENVHhlP8MmKHxaQMI0GGqI")
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

base_prompt='''
    You are a Floorplan Assistant.
    Now you are going to design a floorplan as per the user interaction.
    Keep the conversation simple and need not to explain about things in detail.
    This is one of my chat with you, make sure that you maintain in same pattern:
    based on the user interaction respond appropriately but make sure that it is simple and clear.
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

floorplan_instrutcion=""

response=chat.send_message(base_prompt)
rep=response.candidates[0].content.parts[0].text.strip()
final_message=""
print("\nBot:Welcome ,Lets Design the floorplan.Type 'done' when finished")

while True:
    user_message = input("User: ").strip()   
    if user_message.lower() in {"done", "exit"}:
        break
    
    input_to_bot=tuning_prompt+user_message

    # Send user message to the chatbot
    try:
        response = chat.send_message(input_to_bot)
        agent_reply = response.candidates[0].content.parts[0].text.strip()
        final_message+=agent_reply
        print(f"Bot: {agent_reply}")
    except Exception as e:
        print(f"Bot: Sorry, there was an issue: {e}")
        continue


res=chat.send_message(final_prompt)
bot_reply=res.candidates[0].content.parts[0].text.strip()

# print(bot_reply)
# Regular expression to extract room name, location, and dimensions
pattern = r"add a (\w+) to the (.*?)of the floorplan with dimensions of (\d+x\d+)"
# Find all matches
matches = re.findall(pattern, bot_reply)
room_details={}

# Format the results
for match in matches:
    room, location, dimensions = match
    floorplan_instrutcion+=f"{room.capitalize()} with dimension {dimensions} at location {location}"
    # print(f"Room: {room.capitalize()}, Location: {location.capitalize()}, Dimensions: {dimensions}")

print(floorplan_instrutcion)