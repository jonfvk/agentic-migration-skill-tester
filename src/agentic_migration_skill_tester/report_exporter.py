import json
from typing import Dict, Any, Optional

class ReportExporterError(Exception):
    pass

class ReportExporter:
    """
    Exports the migration validation report to a file in JSON or text format.
    """
    def __init__(self, report_data: Dict[str, Any], formatted_text: Optional[str] = None):
        """
        :param report_data: The structured report data (dict) to export (for JSON).
        :param formatted_text: Optional pre-formatted text report (for text export).
        """
        self.report_data = report_data
        self.formatted_text = formatted_text

    def export(self, file_path: str, format: str = 'json') -> None:
        """
        Exports the report to the given file path in the specified format.
        :param file_path: Path to the output file.
        :param format: 'json' or 'txt'.
        :raises ReportExporterError: If export fails or format is invalid.
        """
        if format not in ('json', 'txt'):
            raise ReportExporterError(f"Unsupported export format: {format}")
        try:
            if format == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.report_data, f, indent=2, ensure_ascii=False)
            elif format == 'txt':
                if not self.formatted_text:
                    raise ReportExporterError("No formatted text provided for TXT export.")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.formatted_text)
        except Exception as e:
            raise ReportExporterError(f"Failed to export report: {e}")
