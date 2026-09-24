import '../entities/court.dart';
import '../repositories/court_repository.dart';

/// Caso de uso: obtener las canchas disponibles.
class GetAvailableCourts {
  GetAvailableCourts(this._repository);

  final CourtRepository _repository;

  Future<List<Court>> call() => _repository.getAvailableCourts();
}
