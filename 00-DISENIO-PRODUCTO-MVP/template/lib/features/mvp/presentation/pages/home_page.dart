import 'package:flutter/material.dart';

import '../../data/datasources/mock_court_data_source.dart';
import '../../data/repositories/court_repository_impl.dart';
import '../../domain/entities/court.dart';
import '../../domain/usecases/get_available_courts.dart';
import '../widgets/court_card.dart';

/// Pantalla principal del MVP. Obtiene los datos vía el caso de uso
/// (Clean Architecture) y los pinta con componentes M3.
class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final GetAvailableCourts _getCourts = GetAvailableCourts(
    CourtRepositoryImpl(MockCourtDataSource()),
  );

  late final Future<List<Court>> _courts;

  @override
  void initState() {
    super.initState();
    _courts = _getCourts();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Reservar cancha',
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: SearchBar(
              hintText: 'Buscar canchas...',
              leading: const Icon(Icons.search),
            ),
          ),
          Expanded(
            child: FutureBuilder<List<Court>>(
              future: _courts,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Center(child: CircularProgressIndicator());
                }
                final courts = snapshot.data ?? const <Court>[];
                if (courts.isEmpty) {
                  return const Center(child: Text('Sin canchas disponibles'));
                }
                return ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: courts.length,
                  itemBuilder: (context, index) => CourtCard(
                    court: courts[index],
                    onReserve: () => ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('${courts[index].name} reservada'),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Inicio'),
          NavigationDestination(icon: Icon(Icons.search), label: 'Buscar'),
          NavigationDestination(icon: Icon(Icons.person), label: 'Perfil'),
        ],
      ),
    );
  }
}
