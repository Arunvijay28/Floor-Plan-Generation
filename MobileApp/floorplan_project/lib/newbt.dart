import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';
import 'package:http/http.dart' as http;
import 'dart:io';
import 'package:flutter/material.dart';
import 'dart:html' as html;
import 'dart:typed_data';
import 'package:http_parser/http_parser.dart';

class Displayimagepage extends StatefulWidget {
  const Displayimagepage({super.key});

  @override
  State<Displayimagepage> createState() => _DisplayimagepageState();
}

class _DisplayimagepageState extends State<Displayimagepage> {
  final PageController _pageController = PageController();

  late List<dynamic> retrievedData;
  Map<String, String> roomDirections = {
    'Living Room': 'NE',
    'Bathroom': 'NE',
    'Master Room': 'NE',
    'Kitchen': 'NE',
    'Common Room': 'NE',
    'Balcony': 'NE',
  };

  String imageKey = DateTime.now().millisecondsSinceEpoch.toString();

  // Full names for display
  final Map<String, String> directionFullNames = {
    'NE': 'North East',
    'SE': 'South East',
    'SW': 'South West',
    'NW': 'North West',
    'N': 'North',
    'S': 'South',
    'W': 'West',
    'E': 'East',
  };

  // Short names for submission
  final Map<String, String> directionShortNames = {
    'North East': 'NE',
    'South East': 'SE',
    'South West': 'SW',
    'North West': 'NW',
    'North': 'N',
    'South': 'S',
    'West': 'W',
    'East': 'E',
  };

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    final arg = ModalRoute.of(context)!.settings.arguments as List<dynamic>?;

    if (arg != null && arg.isNotEmpty) {
      retrievedData = arg;
    } else {
      retrievedData = [];
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        centerTitle: true,
        title: Text("Generated Floorplan Layout"),
      ),
      body: Column(
        children: [
          // Generated Layout (Static Image)
          Container(
            margin: EdgeInsets.all(10),
            height: 200,
            width: 200,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              boxShadow: [
                BoxShadow(
                    spreadRadius: 2, blurRadius: 2, color: Colors.black26),
              ],
            ),
            child: Stack(
              alignment: Alignment.bottomCenter,
              children: [
                Image.asset(
                  'assets/images/rectified_image_filtered.png',
                  key: ValueKey(imageKey),
                  fit: BoxFit.cover,
                ),
                Positioned(
                  bottom: -5,
                  child: IconButton(
                    padding: EdgeInsets.all(5),
                    icon: Icon(Icons.edit, color: Colors.blue),
                    onPressed: () {
                      // Trigger the dropdown dialog
                      _showRoomDirectionDialog();
                    },
                  ),
                ),
              ],
            ),
          ),
          SizedBox(height: 10),

          // Retrieved Layout Title
          Container(
            margin: EdgeInsets.all(10),
            child: Center(
              child: Text(
                "Retrieved Floorplan Layout",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
          ),

          // Retrieved Images with Metadata
          retrievedData.isNotEmpty
              ? Expanded(
                  child: Column(
                    children: [
                      Expanded(
                        child: PageView.builder(
                          controller: _pageController,
                          itemCount: retrievedData.length,
                          itemBuilder: (context, index) {
                            final imageInfo = retrievedData[index];

                            return Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                buildImageContainer(
                                    imageInfo['filename']), // Display image
                                SizedBox(height: 10),
                                buildMetadataContainer(
                                    imageInfo), // Display metadata (rank, dis, similarity)
                              ],
                            );
                          },
                        ),
                      ),
                      SizedBox(height: 10),
                      // Pagination Indicator
                      SmoothPageIndicator(
                        controller: _pageController,
                        count: retrievedData.length,
                        effect: JumpingDotEffect(
                          dotHeight: 7,
                          dotWidth: 7,
                          jumpScale: 1.5,
                          activeDotColor: Colors.blue,
                        ),
                      ),
                    ],
                  ),
                )
              : Center(
                  child: Text("No images retrieved",
                      style: TextStyle(fontSize: 16)),
                ),
        ],
      ),
    );
  }

  // Function to display images
  Widget buildImageContainer(String imagePath) {
    return Container(
      height: 200,
      width: 200,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(spreadRadius: 2, blurRadius: 2, color: Colors.black26),
        ],
        color: Colors.white,
      ),
      child: Image.asset(
        imagePath,
        fit: BoxFit.cover,
      ),
    );
  }

  Widget buildMetadataContainer(Map<String, dynamic> imageInfo) {
    return Container(
      width: 200,
      padding: EdgeInsets.all(8),
      margin: EdgeInsets.symmetric(horizontal: 20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(spreadRadius: 2, blurRadius: 2, color: Colors.black26),
        ],
        color: Colors.white,
      ),
      child: Column(
        children: [
          Text("Rank: ${imageInfo['rank']}", style: TextStyle(fontSize: 14)),
          Text("Dis: ${imageInfo['distance']}", style: TextStyle(fontSize: 14)),
          Text("Similarity: ${imageInfo['similarity']}",
              style: TextStyle(fontSize: 14)),
        ],
      ),
    );
  }

  // Show the dialog for room directions
  Future<void> _showRoomDirectionDialog() async {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Edit Room Directions'),
          content: SingleChildScrollView(
            child: Column(
              children: roomDirections.keys.map((room) {
                return DropdownButtonFormField<String>(
                  decoration: InputDecoration(labelText: room),
                  value: directionFullNames[roomDirections[room]],
                  onChanged: (String? newValue) {
                    setState(() {
                      roomDirections[room] = directionShortNames[newValue!]!;
                    });
                  },
                  items: directionFullNames.values
                      .map<DropdownMenuItem<String>>((String value) {
                    return DropdownMenuItem<String>(
                      value: value,
                      child: Text(value),
                    );
                  }).toList(),
                );
              }).toList(),
            ),
          ),
          actions: <Widget>[
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                print('Finalized directions: $roomDirections');
                _sendDirectionToServer();
                // You can send the updated room directions to the server or further processing here
              },
              child: Text('Finalize Direction'),
            ),
          ],
        );
      },
    );
  }

//   Future<void> _sendDirectionToServer() async {
//     // The data you want to send to the server
//     Map<String, dynamic> updatedDirections = {
//       'living_room': roomDirections['Living Room'],
//       'bathroom': roomDirections['Bathroom'],
//       'master_room': roomDirections['Master Room'],
//       'kitchen': roomDirections['Kitchen'],
//       'common_room': roomDirections['Common Room'],
//       'balcony': roomDirections['Balcony'],
//     };

//     try {
//       final response = await http.post(
//         Uri.parse(
//             'http://127.0.0.1:5000/edit_sa'), // Replace with your server URL
//         headers: {'Content-Type': 'application/json'},
//         body: json.encode(updatedDirections), // Convert Map to JSON
//       );

//       if (response.statusCode == 200) {
//         final responseBody = json.decode(response.body);
//         if (responseBody['success']) {
//           print("Successfully updated directions");
//           // You can show a success message or proceed further here
//         } else {
//           print("Failed to update directions");
//         }
//       } else {
//         print("Error: ${response.statusCode}");
//       }
//     } catch (e) {
//       print("Error sending directions to server: $e");
//     }

//     Uri uri = Uri.parse("http://127.0.0.1:5000/reload");
//     try {
//       http.Response response = await http.get(uri);
//       if (response.statusCode == 200) {
//          setState(() {
//             // Reload the image after the server updates it
//             imageKey = DateTime.now().millisecondsSinceEpoch.toString();
//           });
//         print(jsonDecode(response.body)["reply"]);
//       } else {
//         print("Error: server returned ${response.statusCode}");
//       }
//     } catch (e) {
//       print("Error sending directions to server: $e");
//     }
//   }
// }

  Future<void> _sendDirectionToServer() async {
    // The data you want to send to the server
    Map<String, dynamic> updatedDirections = {
      'living_room': roomDirections['Living Room'],
      'bathroom': roomDirections['Bathroom'],
      'master_room': roomDirections['Master Room'],
      'kitchen': roomDirections['Kitchen'],
      'common_room': roomDirections['Common Room'],
      'balcony': roomDirections['Balcony'],
    };

    try {
      final response = await http.post(
        Uri.parse(
            'http://127.0.0.1:5000/edit_sa'), // Replace with your server URL
        headers: {'Content-Type': 'application/json'},
        body: json.encode(updatedDirections), // Convert Map to JSON
      );

      if (response.statusCode == 200) {
        final responseBody = json.decode(response.body);
        if (responseBody['success']) {
          print("Successfully updated directions");
          // Trigger image reload after directions are updated
          _reloadImageFromServer();
        } else {
          print("Failed to update directions");
        }
      } else {
        print("Error: ${response.statusCode}");
      }
    } catch (e) {
      print("Error sending directions to server: $e");
    }
  }

  Future<void> _reloadImageFromServer() async {
    Uri uri = Uri.parse("http://127.0.0.1:5000/reload");
    try {
      http.Response response = await http.get(uri);
      if (response.statusCode == 200) {
        print(jsonDecode(response.body)["reply"]);
        // Reload the image after server finishes copying the image to the folder
        setState(() {
          imageKey = DateTime.now()
              .millisecondsSinceEpoch
              .toString(); // Trigger image reload
        });
      } else {
        print("Error: server returned ${response.statusCode}");
      }
    } catch (e) {
      print("Error sending directions to server: $e");
    }
  }
}
