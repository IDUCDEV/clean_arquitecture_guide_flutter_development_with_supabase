import 'package:flutter/material.dart';

import '../../domain/entities/court.dart';

/// Card M3 para mostrar una cancha con su disponibilidad.
class CourtCard extends StatelessWidget {
  const CourtCard({super.key, required this.court, this.onReserve});

  final Court court;
  final VoidCallback? onReserve;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          child: Icon(court.available ? Icons.sports_tennis : Icons.lock),
        ),
        title: Text(court.name),
        subtitle: Text(
          '${court.club} · \$${court.pricePerHour.toStringAsFixed(0)}/h',
        ),
        trailing: court.available
            ? FilledButton(onPressed: onReserve, child: const Text('Reservar'))
            : const Chip(label: Text('Ocupado')),
      ),
    );
  }
}
