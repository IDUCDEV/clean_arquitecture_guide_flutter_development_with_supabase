import '../../domain/entities/court.dart';
import '../../domain/repositories/court_repository.dart';
import '../datasources/mock_court_data_source.dart';

/// Implementación del repositorio. Traduce la fuente de datos al dominio.
class CourtRepositoryImpl implements CourtRepository {
  CourtRepositoryImpl(this._dataSource);

  final MockCourtDataSource _dataSource;

  @override
  Future<List<Court>> getAvailableCourts() =>
      _dataSource.fetchAvailableCourts();
}
