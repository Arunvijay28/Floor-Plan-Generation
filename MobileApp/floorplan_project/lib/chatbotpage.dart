import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class Chatbotpage extends StatefulWidget {
  const Chatbotpage({super.key});

  @override
  State<Chatbotpage> createState() => _ChatbotpageState();
}

class _ChatbotpageState extends State<Chatbotpage> {
  TextEditingController _controller = TextEditingController();
  List<String> messages = [
    "Bot: Hi, I am your Floorplan Assistant"
  ]; // Stores chat messages

  Future<String> fetchData(String userMessage) async {
    Uri uri = Uri.parse("http://127.0.0.1:5000/message");

    try {
      http.Response response = await http.post(
        uri,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"message": userMessage}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body)["reply"];
      } else {
        return "Error: Server returned ${response.statusCode}";
      }
    } catch (e) {
      return "Error: Failed to connect to server: $e";
    }
  }

   Future<String> finalized() async {
    Uri uri = Uri.parse("http://127.0.0.1:5000/finalize");
    try {
      http.Response response = await http.get(uri);
      if (response.statusCode == 200) {
        return jsonDecode(response.body)["reply"];
      } else {
        return "Error: server returned ${response.statusCode}";
      }
    } catch (e) {
      return "Error from connecting to the server $e";
    }
  }

  void sendMessage() async {
    String userMessage = _controller.text.trim();
    if (userMessage.isEmpty) return;

    setState(() {
      messages.add("User: $userMessage");
    });

    String apiResponse = await fetchData(userMessage);
    _controller.clear();

    setState(() {
      messages.add("Bot: $apiResponse");
    });
  }

  void finaliseFloorplan() async {
    String res = await finalized();
    print(res);
    setState(() {
      messages.add(
          "Bot : ${res.startsWith("success") ? "Floorplan finalised" : res}");
    });
    if (res.startsWith("success")) {
      Navigator.pushNamed(context, "/generate");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        centerTitle: true,
        backgroundColor: Colors.white,
        title: const Text(
          "Floorplan Assistant",
          style: TextStyle(color: Colors.black),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(10),
        child: Column(
          children: [
            Expanded(
              child: ListView.builder(
                itemCount: messages.length,
                itemBuilder: (context, index) {
                  return Container(
                    padding: EdgeInsets.all(8),
                    margin: EdgeInsets.symmetric(vertical: 4),
                    decoration: BoxDecoration(
                      color: messages[index].startsWith("Bot")
                          ? Colors.blue[100]
                          : Colors.grey[300],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      messages[index],
                      style: TextStyle(fontSize: 16),
                    ),
                  );
                },
              ),
            ),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: "Enter your Floorplan instruction",
                      border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8)),
                    ),
                  ),
                ),
                IconButton(
                  padding: EdgeInsets.all(5),
                  icon: Icon(Icons.arrow_upward, color: Colors.blue),
                  onPressed: sendMessage,
                ),
                SizedBox(width: 8), // Spacing between buttons
                ElevatedButton(
                  onPressed: finaliseFloorplan,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    padding: EdgeInsets.symmetric(vertical: 12, horizontal: 10),
                  ),
                  child: Text(
                    "Finalise",
                    style: TextStyle(fontSize: 14, color: Colors.white),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
