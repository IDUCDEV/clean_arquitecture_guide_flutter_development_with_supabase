/// Entidad de dominio: una cancha disponible para reservar.
class Court {
  const Court({
    required this.id,
    required this.name,
    required this.club,
    required this.pricePerHour,
    required this.available,
  });

  final String id;
  final String name;
  final String club;
  final double pricePerHour;
  final bool available;
}
