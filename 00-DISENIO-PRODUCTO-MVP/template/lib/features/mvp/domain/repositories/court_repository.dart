import '../entities/court.dart';

/// Contrato del repositorio de canchas (Domain). La implementación vive
/// en Data y la UI nunca la conoce.
abstract interface class CourtRepository {
  Future<List<Court>> getAvailableCourts();
}
