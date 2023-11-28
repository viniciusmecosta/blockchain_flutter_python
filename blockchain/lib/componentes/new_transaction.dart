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
      title: 'Nova Transação',
      theme: ThemeData(
        primarySwatch: Colors.blueGrey,
      ),
      home: MyForm(),
    );
  }
}

class MyForm extends StatefulWidget {
  @override
  _MyFormState createState() => _MyFormState();
}

class _MyFormState extends State<MyForm> {
  TextEditingController _controllerOrigem = TextEditingController();
  TextEditingController _controllerDestino = TextEditingController();
  TextEditingController _controllerValor = TextEditingController();

  Future<void> _enviarDadosParaBackend() async {
    final String origem = _controllerOrigem.text;
    final String destino = _controllerDestino.text;
    final String valor = _controllerValor.text;

    final response = await http.post(
      Uri.parse("http://localhost:5000/add_transaction"),
      headers: {"Content-Type": "application/json"},
      body: json.encode({
        "sender": origem,
        "receiver": destino,
        "amount": valor,
      }),
    );

    if (response.statusCode == 201) {
      print("Dados enviados com sucesso!");

      // Exibe um diálogo informativo
      showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: Text("Sucesso"),
            content: Text("Transação realizada com sucesso!"),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.pop(context); // Fecha o diálogo
                  Navigator.pop(context); // Volta para a tela anterior
                },
                child: Text("OK"),
              ),
            ],
          );
        },
      );
    } else {
      print("Erro ao enviar os dados para o backend.");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Nova Transação'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextFormField(
              controller: _controllerOrigem,
              decoration: InputDecoration(
                labelText: 'Origem',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 10),
            TextFormField(
              controller: _controllerDestino,
              decoration: InputDecoration(
                labelText: 'Destino',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 10),
            TextFormField(
              controller: _controllerValor,
              decoration: InputDecoration(
                labelText: 'Valor',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _enviarDadosParaBackend,
              style: ElevatedButton.styleFrom(
                primary: Colors.blueGrey, // background color
                onPrimary: Colors.white, // text color
              ),
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Text(
                  'Confirmar',
                  style: TextStyle(fontSize: 18),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
