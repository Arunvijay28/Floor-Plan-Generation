import 'package:flutter/material.dart';
import 'package:flutter_learn/chatbotpage.dart';
import 'package:flutter_learn/displayImagePage.dart';
import 'package:flutter_learn/graphpage.dart';

void main() {
  // print("hello");
  runApp(MaterialApp(
    home: Scaffold(
      body: Chatbotpage(),
    ),
    routes: {
      '/generate': (context) => GraphPage(),
      "/display": (context) => Displayimagepage()
    },
  ));
}
