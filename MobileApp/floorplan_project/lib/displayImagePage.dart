import 'package:flutter/material.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';

class Displayimagepage extends StatefulWidget {
  const Displayimagepage({super.key});

  @override
  State<Displayimagepage> createState() => _DisplayimagepageState();
}

class _DisplayimagepageState extends State<Displayimagepage> {
  final PageController _pageController = PageController();

  late List<dynamic> retrievedData; 

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
                BoxShadow(spreadRadius: 2, blurRadius: 2, color: Colors.black26),
              ],
            ),
            child: Image.asset(
              'assets/images/fp_final_0.png',
              fit: BoxFit.cover,
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
                                buildImageContainer(imageInfo['filename']), // Display image
                                SizedBox(height: 10),
                                buildMetadataContainer(imageInfo), // Display metadata (rank, dis, similarity)
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
                  child: Text("No images retrieved", style: TextStyle(fontSize: 16)),
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
          Text("Similarity: ${imageInfo['similarity']}", style: TextStyle(fontSize: 14)),
        ],
      ),
    );
  }
}
