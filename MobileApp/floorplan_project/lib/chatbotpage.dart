import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:html' as html;
import 'dart:typed_data';
import 'package:http_parser/http_parser.dart';

class Chatbotpage extends StatefulWidget {
  const Chatbotpage({super.key});

  @override
  State<Chatbotpage> createState() => _ChatbotpageState();
}

class _ChatbotpageState extends State<Chatbotpage> {
  TextEditingController _controller = TextEditingController();
  List<String> messages = ["Bot: Hi, I am your Floorplan Assistant"];

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
    setState(() {
      messages.add(
          "Bot : ${res.startsWith("success") ? "Floorplan finalised" : res}");
    });
    if (res.startsWith("success")) {
      Navigator.pushNamed(context, "/generate");
    }
  }

  Future<void> uploadFile() async {
    html.FileUploadInputElement uploadInput = html.FileUploadInputElement();
    uploadInput.accept = 'image/*'; // Accept only image files
    uploadInput.click();

    uploadInput.onChange.listen((e) async {
      final files = uploadInput.files;
      if (files?.isEmpty ?? true) return;

      final file = files?.first;
      if (file != null) {
        final reader = html.FileReader();
        reader.readAsArrayBuffer(file);
        reader.onLoadEnd.listen((e) async {
          final fileBytes = reader.result as Uint8List;
          var uri = Uri.parse(
              "http://127.0.0.1:5000/upload"); 
          var request = http.MultipartRequest('POST', uri)
            ..files.add(http.MultipartFile.fromBytes('image', fileBytes,
                filename: file.name, contentType: MediaType('image', 'png')));
                
          var response = await request.send();

          if (response.statusCode == 200) {
            print("File uploaded successfully!");
            setState(() {
              messages.add("User uploaded a file: ${file.name}");
            });
          } else {
            print("File upload failed: ${response.statusCode}");
          }
        });
      }
    });
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
                  icon: Icon(Icons.attach_file, color: Colors.grey),
                  onPressed: uploadFile,
                ),
                IconButton(
                  icon: Icon(Icons.arrow_upward, color: Colors.blue),
                  onPressed: sendMessage,
                ),
                SizedBox(width: 8),
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
