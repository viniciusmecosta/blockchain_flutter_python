import 'package:blockchain/componentes/blockchain_screen.dart';
import 'package:blockchain/componentes/new_transaction.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Blockchain',
      theme: ThemeData(
        primarySwatch: Colors.blueGrey,
      ),
      home: MyHomePage(),
    );
  }
}

Future<void> mineBlock(BuildContext context) async {
  try {
    // Exibindo um AlertDialog inicial para mostrar o início da mineração
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Mineração de Bloco'),
          content: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Iniciando a mineração...'),
              SizedBox(height: 10),
              LinearProgressIndicator(), // Adicionando uma barra de progresso
            ],
          ),
        );
      },
    );

    final response =
        await http.get(Uri.parse("http://localhost:5000/mine_block"));
    if (response.statusCode == 200) {
      // Extraindo as informações da resposta do servidor
      final Map<String, dynamic> responseData = json.decode(response.body);
      final int blockNumber = responseData['index'];
      final String message = responseData['message'];

      // Fechando o AlertDialog inicial

      // Exibindo um AlertDialog com as informações do bloco
      showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: Text('Mineração de Bloco'),
            content: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('Bloco Número: $blockNumber'),
                SizedBox(height: 10),
                Text(message),
              ],
            ),
            actions: <Widget>[
              TextButton(
                onPressed: () {
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (context) => MyHomePage()),
                  );
                },
                child: Text('Fechar'),
              ),
            ],
          );
        },
      );
    } else {
      print('Falha ao minerar bloco: ${response.statusCode}');
    }
  } catch (e) {
    print('Erro ao tentar minerar bloco: $e');
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  List<Block> blocks = [];

  @override
  void initState() {
    super.initState();
    fetchData();
  }

  Future<void> fetchData() async {
    try {
      final response =
          await http.get(Uri.parse("http://localhost:5000/get_chain"));
      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        setState(() {
          blocks = List<Block>.from(
              result['chain'].map((block) => Block.fromJson(block)));
        });
      } else {
        print("Erro ao buscar dados da blockchain");
      }
    } catch (e) {
      print("Erro na requisição: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Blockchain'),
        centerTitle: true,
        actions: [
          IconButton(
            onPressed: () async {
              await mineBlock(context);
            },
            icon: Icon(Icons.work),
          ),
        ],
        leading: IconButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => MyForm()),
            );
          },
          icon: Icon(Icons.add),
        ),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            SizedBox(height: 20),
            Text('Lista de Blocos',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            SizedBox(height: 10),
            Expanded(
              child: ListView.builder(
                itemCount: blocks.length,
                itemBuilder: (context, index) {
                  return BlockWidget(block: blocks[index]);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
