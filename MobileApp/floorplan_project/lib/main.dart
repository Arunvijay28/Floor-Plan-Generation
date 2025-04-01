import 'package:flutter/material.dart';
import 'package:flutter_learn/chatbotpage.dart';
import 'package:flutter_learn/displayImagePage.dart';
import 'package:flutter_learn/graphpage.dart';
// import 'package:flutter_learn/newbt.dart';

void main() {
  // print("hello");
  runApp(MaterialApp(
    home: Scaffold(
      body: Chatbotpage(),
      // body:Displayimagepage(),
    ),
    routes: {
      '/generate': (context) => GraphPage(),
      "/display": (context) => Displayimagepage()
    },
  ));
}
