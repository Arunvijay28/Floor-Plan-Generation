import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:graphview/GraphView.dart';
import 'package:http/http.dart' as http;

class GraphPage extends StatefulWidget {
  @override
  _GraphPageState createState() => _GraphPageState();
}

class _GraphPageState extends State<GraphPage> {
  final Graph graph = Graph();
  final Map<String, Node> roomNodes = {};
  String? selectedRoom;
  int nodeCounter = 1;

  final Map<String, Color> roomColors = {
    "entrance": Color(0xFFBFE3E8),
    "dining room": Color(0xFF7BA779),
    "CommonRoom": Color(0xFFE87A90),
    "storage": Color(0xFFFF8C69),
    "front door": Color(0xFF1F849B),
    "unknown": Color(0xFF727171),
    "interior_door": Color(0xFFD3A2C7),
    "Living Room": Color(0xFFEEE8AA),
    "Bathroom": Color(0xFFFFD700),
    "Kitchen": Color(0xFFADD8E6),
    "CommonRoom": Color(0xFFFFA500),
    "Balcony": Color(0xFF6B8E23),
    "MasterRoom": Color(0xFFF08080),
  };

  final Map<String, Color> roomOptions = {
    "entrance": Color(0xFFBFE3E8),
    "dining room": Color(0xFF7BA779),
    "CommonRoom": Color(0xFFE87A90),
    "storage": Color(0xFFFF8C69),
    "front door": Color(0xFF1F849B),
    "unknown": Color(0xFF727171),
    "interior_door": Color(0xFFD3A2C7),
  };

  final List<List<double>> probMatrix = [
    [0, 38.7, 37.4, 15.0, 20.9, 23.1],
    [48.5, 0, 37.6, 25.7, 8.0, 41.6],
    [39.0, 31.3, 0, 15.5, 12.1, 19.6],
    [30.5, 41.6, 30.3, 0, 23.3, 28.0],
    [34.3, 10.5, 19.0, 18.8, 0, 51.4],
    [23.7, 34.1, 19.3, 14.2, 32.2, 0],
  ];
  final double threshold = 27.0;
  final List<String> initialRooms = [
    "Living Room",
    "Bathroom",
    "Kitchen",
    "CommonRoom",
    "Balcony",
    "MasterRoom"
  ];

  final Map<String, int> ROOM_CLASS = {
    "Living Room": 1,
    "Kitchen": 2,
    "MasterRoom": 3,
    "Bathroom": 4,
    "Balcony": 5,
    "entrance": 6,
    "dining room": 7,
    "CommonRoom": 8,
    "storage": 10,
    "front door": 15,
    "unknown": 16,
    "interior_door": 17
  };

  @override
  void initState() {
    super.initState();
    _generateInitialGraph();
  }

  Future<String> layout_retrieval(
      List<int> nodes, List<Map<String, int>> edges) async {
    Uri uri = Uri.parse("http://127.0.0.1:5000/layout_retrieval");
    try {
      http.Response response = await http.post(uri,
          headers: {"Content-Type": "application/json"},
          body: jsonEncode({"nodes": nodes, "edges": edges}));
      if (response.statusCode == 200) {
        return jsonDecode(response.body)["reply"];
      } else {
        return "Error: server returned ${response.statusCode}";
      }
    } catch (e) {
      return "Error from connecting to the server $e";
    }
  }

  Future<dynamic> display_images(String res) async {
    Uri uri = Uri.parse("http://127.0.0.1:5000/display_images");
    if (res.startsWith("success")) {
      try {
        http.Response response = await http.get(uri);
        if (response.statusCode == 200) {
          return jsonDecode(response.body);
        } else {
          return "Error from server:${response.statusCode}";
        }
      } catch (e) {
        return "Error connecting to the server :$e";
      }
    } else {
      return res;
    }
  }

  void _generateInitialGraph() {
    List<Node> nodes = [];

    for (String room in initialRooms) {
      final node = Node.Id(nodeCounter++);
      roomNodes[room] = node;
      nodes.add(node);
      graph.addNode(node);
    }

    for (int i = 0; i < probMatrix.length; i++) {
      for (int j = i + 1; j < probMatrix.length; j++) {
        if (probMatrix[i][j] > threshold) {
          graph.addEdge(nodes[i], nodes[j]);
        }
      }
    }

    setState(() {});
  }

  void _addNode(String roomName) {
    final newNode = Node.Id(nodeCounter++);
    roomNodes[roomName] = newNode;
    graph.addNode(newNode);
    setState(() {});
  }

  void _selectRoom(String roomKey) {
    setState(() {
      if (selectedRoom == null) {
        selectedRoom = roomKey;
      } else {
        if (selectedRoom != roomKey) {
          _addEdge(selectedRoom!, roomKey);
        }
        selectedRoom = null;
      }
    });
  }

  void _addEdge(String fromRoom, String toRoom) {
    if (roomNodes.containsKey(fromRoom) && roomNodes.containsKey(toRoom)) {
      graph.addEdge(roomNodes[fromRoom]!, roomNodes[toRoom]!);
      setState(() {});
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text("Both rooms must exist before adding an edge."),
      ));
    }
  }

  void _sendDataToBackend() async {
    List<String> nodeNames = roomNodes.keys.toList();

    List<int> realNodes = [];
    for (int i = 0; i < nodeNames.length; i++) {
      realNodes.add(ROOM_CLASS[nodeNames[i]]! - 1);
    }

    List<Map<String, int>> edges = [];

    graph.edges.forEach((edge) {
      String fromRoom = roomNodes.keys.firstWhere(
          (key) => roomNodes[key] == edge.source,
          orElse: () => "Unknown");
      String toRoom = roomNodes.keys.firstWhere(
          (key) => roomNodes[key] == edge.destination,
          orElse: () => "Unknown");

      edges.add({
        "from": ROOM_CLASS[fromRoom]! - 1,
        "to": ROOM_CLASS[toRoom]! - 1,
      });
    });

    print("Edges: $edges");
    print("Nodes: $realNodes");

    String response_from_layout_retrieval =
        await layout_retrieval(realNodes, edges);
    print(response_from_layout_retrieval);

    var response_for_display_image =
        await display_images(response_from_layout_retrieval);
    print(response_for_display_image);

    if (response_for_display_image is Map<String, dynamic> &&
        response_for_display_image.containsKey("images_info")) {
      List<dynamic> images_info = response_for_display_image["images_info"];
      Navigator.pushNamed(context, "/display", arguments: images_info);
    } 
    
    else 
    {
      print("error");
      void showAlert(String errorMessage) {
        showDialog(
          context: context,
          builder: (BuildContext context) {
            return AlertDialog(
              title: Text("Error",
                  style: TextStyle(
                      color: Colors.red, fontWeight: FontWeight.bold)),
              content: Text(errorMessage),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pop(); // Close the alert
                  },
                  child: Text("OK", style: TextStyle(color: Colors.blue)),
                ),
              ],
            );
          },
        );
      }
    }
    // }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Interactive Graph")),
      body: Column(
        children: [
          Expanded(
            child: Center(
              child: Container(
                width: 400,
                height: 400,
                color: Theme.of(context).scaffoldBackgroundColor,
                child: InteractiveViewer(
                  constrained: false,
                  boundaryMargin: EdgeInsets.all(20),
                  minScale: 0.5,
                  maxScale: 1.5,
                  child: GraphView(
                    graph: graph,
                    algorithm: FruchtermanReingoldAlgorithm(),
                    paint: Paint()..color = Colors.black,
                    builder: (Node node) {
                      int nodeId = node.key!.value;
                      String room = roomNodes.keys.firstWhere(
                          (key) => roomNodes[key]!.key!.value == nodeId,
                          orElse: () => "Unknown");

                      return GestureDetector(
                        onTap: () => _selectRoom(room),
                        child: Container(
                          padding: EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: selectedRoom == room
                                ? Colors.red
                                : (roomColors[room] ?? Colors.grey),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child:
                              Text(room, style: TextStyle(color: Colors.white)),
                        ),
                      );
                    },
                  ),
                ),
              ),
            ),
          ),
          Wrap(
            children: roomOptions.keys.map((room) {
              return ElevatedButton(
                onPressed: () => _addNode(room),
                child: Text(room),
                style: ElevatedButton.styleFrom(
                    foregroundColor: roomOptions[room]),
              );
            }).toList(),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: ElevatedButton(
              onPressed: _sendDataToBackend,
              child: Text("Generate"),
            ),
          ),
        ],
      ),
    );
  }
}
