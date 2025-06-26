import unittest
from unittest.mock import patch, MagicMock
import sys


import main


class TestMainModule(unittest.TestCase):

    @patch("main.generate_pdf_report")
    @patch("main.generate_charts")
    @patch("main.process_csv_file")
    @patch("main.discover_csv_files")
    @patch("main.load_config")
    def test_main_default_config(self, mock_load_config, mock_discover_csv_files,
                                 mock_process_csv_file, mock_generate_charts,
                                 mock_generate_pdf_report):
        # Konfiguracja mocków
        mock_load_config.return_value = {"input_dir": "test_data"}
        mock_discover_csv_files.return_value = ["file1.csv", "file2.csv"]
        mock_process_csv_file.side_effect = lambda f, c: {"summary": f"{f}_summary"}
        mock_generate_charts.side_effect = lambda s, c: [f"{s}_chart"]

        # Wyczyść argumenty w sys.argv i uruchom main
        sys.argv = ["main.py"]
        main.main()

        # Assercje
        mock_load_config.assert_called_once_with("config.yaml")
        mock_discover_csv_files.assert_called_once_with("test_data")
        self.assertEqual(mock_process_csv_file.call_count, 2)
        self.assertEqual(mock_generate_charts.call_count, 2)
        self.assertEqual(mock_generate_pdf_report.call_count, 2)
        mock_generate_pdf_report.assert_any_call("file1.csv", {"summary": "file1.csv_summary"},
                                                 ["file1.csv_summary_chart"], {"input_dir": "test_data"})

    @patch("main.load_config")
    def test_main_with_custom_config_path(self, mock_load_config):
        sys.argv = ["main.py", "custom_config.yaml"]
        mock_load_config.return_value = {}
        with patch("main.discover_csv_files", return_value=[]):
            main.main()
        mock_load_config.assert_called_once_with("custom_config.yaml")


if __name__ == "__main__":
    unittest.main()
