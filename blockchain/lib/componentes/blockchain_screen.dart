import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:intl/intl.dart';

class Block {
  final int index;
  final String timestamp;
  final int proof;
  final String previousHash;
  final String hash;
  final List<Map<String, dynamic>> transactions;

  Block({
    required this.hash,
    required this.index,
    required this.timestamp,
    required this.proof,
    required this.previousHash,
    required this.transactions,
  });

  factory Block.fromJson(Map<String, dynamic> json) {
    return Block(
      index: json['index'],
      timestamp: json['timestamp'],
      proof: json['proof'],
      hash: json['hash'],
      previousHash: json['previous_hash'],
      transactions: List<Map<String, dynamic>>.from(json['transactions']),
    );
  }
}

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Blockchain App',
      theme: ThemeData(
        primarySwatch: Colors.blueGrey,
      ),
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Blockchain App'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => BlockchainScreen()),
                );
              },
              child: Text('Abrir Lista de Blocos'),
            ),
            ElevatedButton(
              onPressed: () {},
              child: Text('Adicionar Nova Transação'),
            ),
          ],
        ),
      ),
    );
  }
}

class BlockchainScreen extends StatefulWidget {
  @override
  _BlockchainScreenState createState() => _BlockchainScreenState();
}

class _BlockchainScreenState extends State<BlockchainScreen> {
  List<Block> blocks = [];

  @override
  void initState() {
    super.initState();
    fetchData();
  }

  Future<void> fetchData() async {
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
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Lista de Blocos'),
      ),
      body: Container(
        padding: EdgeInsets.all(5),
        child: ListView.builder(
          itemCount: blocks.length,
          itemBuilder: (context, index) {
            return BlockWidget(block: blocks[index]);
          },
        ),
      ),
    );
  }
}

class BlockWidget extends StatelessWidget {
  final Block block;

  const BlockWidget({Key? key, required this.block}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final formattedDateTime = DateFormat.yMd().add_Hms().format(
          DateTime.parse(block.timestamp),
        );

    return Card(
      elevation: 10,
      margin: EdgeInsets.all(15),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("Bloco: #${block.index}",
                    style:
                        TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                Text("Hash do Bloco: ${block.hash}",
                    style: TextStyle(fontSize: 17, color: Colors.grey)),
              ],
            ),
            SizedBox(height: 10),
            Text("Data/hora: ${formattedDateTime}",
                style: TextStyle(fontSize: 14)),
            Text("Nonce: ${block.proof}", style: TextStyle(fontSize: 14)),
            Text("Hash do bloco anterior: ${block.previousHash}",
                style: TextStyle(fontSize: 14)),
            SizedBox(height: 10),
            Divider(),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("Transações:",
                    style:
                        TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                SizedBox(height: 10),
                DataTable(
                  columns: const [
                    DataColumn(label: Text('De:')),
                    DataColumn(label: Text('Para:')),
                    DataColumn(label: Text('Valor:')),
                  ],
                  rows: block.transactions
                      .map(
                        (transaction) => DataRow(cells: [
                          DataCell(Text("${transaction['sender']}")),
                          DataCell(Text("${transaction['receiver']}")),
                          DataCell(Text("${transaction['amount']}")),
                        ]),
                      )
                      .toList(),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
