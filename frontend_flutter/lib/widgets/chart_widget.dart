import 'package:flutter/material.dart';
// import 'package:fl_chart/fl_chart.dart';
import 'package:animate_do/animate_do.dart';
import '../core/theme_constants.dart';

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
    return ZoomIn(
      duration: const Duration(milliseconds: 600),
      child: Container(
        height: 250,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: QueryVoiceTheme.surface,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: Colors.white.withOpacity(0.05)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.2),
              blurRadius: 15,
              spreadRadius: 2,
            )
          ],
        ),
        child: Column(
          children: [
            Row(
              children: [
                Icon(
                  chartType == 'bar' ? Icons.bar_chart : Icons.pie_chart,
                  color: QueryVoiceTheme.secondary,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Text(
                  '${chartType.toUpperCase()} ANALYSIS',
                  style: const TextStyle(
                    fontSize: 10,
                    letterSpacing: 1,
                    fontWeight: FontWeight.bold,
                    color: Colors.white54,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Expanded(
              child: chartType == 'bar' ? _buildBarChart() : _buildPieChart(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBarChart() => const Center(child: Text('Bar Chart Placeholder'));
  Widget _buildPieChart() => const Center(child: Text('Pie Chart Placeholder'));
}
