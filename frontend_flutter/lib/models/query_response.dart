/// QueryResponse — Data class representing the backend's response to a query.
///
/// Contains:
/// - The original natural language question (transcribed or typed)
/// - The generated SQL query
/// - The query execution results as tabular data
/// - Optional chart metadata
class QueryResponse {
  final String naturalLanguageQuery;
  final String generatedSql;
  final List<Map<String, dynamic>> results;
  final String? chartType;
  final String? summary;

  QueryResponse({
    required this.naturalLanguageQuery,
    required this.generatedSql,
    required this.results,
    this.chartType,
    this.summary,
  });

  factory QueryResponse.fromJson(Map<String, dynamic> json) {
    return QueryResponse(
      naturalLanguageQuery: json['natural_language_query'] as String,
      generatedSql: json['generated_sql'] as String,
      results: List<Map<String, dynamic>>.from(json['results'] as List),
      chartType: json['chart_type'] as String?,
      summary: json['summary'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'natural_language_query': naturalLanguageQuery,
      'generated_sql': generatedSql,
      'results': results,
      'chart_type': chartType,
      'summary': summary,
    };
  }
}
