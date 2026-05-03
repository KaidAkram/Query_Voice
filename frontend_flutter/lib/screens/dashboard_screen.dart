import 'package:flutter/material.dart';

/// DashboardScreen — Displays query results as interactive charts and tables.
///
/// Renders business intelligence visualizations based on the SQL query results
/// returned from the FastAPI backend.
class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
      ),
      body: const Center(
        child: Text('Dashboard visualizations — coming soon'),
      ),
      // TODO: Integrate fl_chart widgets for dynamic data rendering
    );
  }
}
