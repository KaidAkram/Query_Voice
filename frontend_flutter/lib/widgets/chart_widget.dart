import 'package:flutter/material.dart';
// import 'package:fl_chart/fl_chart.dart';

/// ChartWidget — A reusable chart component for rendering query results.
///
/// Supports multiple chart types:
/// - Bar chart (default)
/// - Line chart
/// - Pie chart
///
/// Data is passed in as a list of maps from the API response.
class ChartWidget extends StatelessWidget {
  final List<Map<String, dynamic>> data;
  final String chartType;

  const ChartWidget({
    super.key,
    required this.data,
    this.chartType = 'bar',
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
      ),
      child: const Center(
        child: Text('Chart rendering — coming soon'),
      ),
      // TODO: Implement fl_chart rendering based on chartType
    );
  }
}
