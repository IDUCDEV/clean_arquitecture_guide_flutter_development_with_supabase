import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mvp_template/app.dart';

void main() {
  testWidgets('La app arranca y muestra la Home con tema M3', (tester) async {
    await tester.pumpWidget(const MvpApp());
    await tester.pumpAndSettle();

    expect(find.text('Reservar cancha'), findsOneWidget);
    expect(find.byType(NavigationBar), findsOneWidget);
    expect(find.byType(Card), findsNWidgets(3));
  });
}
