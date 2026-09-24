import '../../domain/entities/court.dart';

/// Fuente de datos local con datos mock. Sustituir por una fuente remota
/// (API, Supabase, etc.) sin tocar el resto de capas.
class MockCourtDataSource {
  Future<List<Court>> fetchAvailableCourts() async {
    return const [
      Court(
        id: '1',
        name: 'Cancha Central',
        club: 'Club Deportivo',
        pricePerHour: 15,
        available: true,
      ),
      Court(
        id: '2',
        name: 'Cancha 2',
        club: 'Club Deportivo',
        pricePerHour: 18,
        available: true,
      ),
      Court(
        id: '3',
        name: 'Cancha 3',
        club: 'Club Deportivo',
        pricePerHour: 20,
        available: false,
      ),
    ];
  }
}
