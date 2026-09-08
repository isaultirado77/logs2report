import pytest
from pathlib import Path
import pandas as pd
from logs2report.models import ResetRecord, COLUMNS
from logs2report.report import to_dataframe, write_csv


@pytest.fixture
def sample_records():
    """Registros de prueba con datos reales del log."""
    return [
        ResetRecord(
            timestamp='2026-09-01T00:02:39.862105Z',
            updated_at='2026-09-01T00:02:52.868586Z',
            operation_id='b5ab6865ca8ac9629ff2eb303637d408',
            requester='admsistemas520',
            target='520000228',
            action='resetuser',
            system='ADManager',
            requester_name='Nombre_d216ff1cda Apellido_d216ff1cda',
            target_name='Nombre_86f0740bf6 Apellido_86f0740bf6',
            requester_office='0520',
            target_office='0520',
            result='1 / Password reset successful.',
            requisitos='',
        ),
        ResetRecord(
            timestamp='2026-09-01T00:03:40.445253Z',
            updated_at='2026-09-01T00:03:50.200731Z',
            operation_id='f7dde1e1995c0c89366858c6f494dc4d',
            requester='admsistemas969',
            target='969000093',
            action='resetuser',
            system='ADManager',
            requester_name='Nombre_b52d7f1bdc Apellido_b52d7f1bdc',
            target_name='Nombre_d1e1fa4a78 Apellido_d1e1fa4a78',
            requester_office='0969',
            target_office='0969',
            result='1 / Password reset successful.',
            requisitos='',
        ),
    ]


class TestToDataframe:
    """Tests para to_dataframe."""

    def test_to_dataframe_returns_dataframe(self, sample_records):
        """to_dataframe devuelve un DataFrame."""
        df = to_dataframe(sample_records)
        assert isinstance(df, pd.DataFrame)

    def test_dataframe_has_correct_columns_in_order(self, sample_records):
        """El DataFrame tiene las columnas en el orden de COLUMNS."""
        df = to_dataframe(sample_records)
        expected_columns = [header for header, _ in COLUMNS]
        assert list(df.columns) == expected_columns

    def test_dataframe_has_correct_number_of_rows(self, sample_records):
        """El DataFrame tiene el mismo número de filas que registros."""
        df = to_dataframe(sample_records)
        assert len(df) == len(sample_records)

    def test_dataframe_all_values_are_strings(self, sample_records):
        """Todos los valores en el DataFrame son strings."""
        df = to_dataframe(sample_records)
        for col in df.columns:
            assert df[col].dtype == 'str'

    def test_office_preserves_leading_zero(self, sample_records):
        """OFFICE con cero inicial se preserva."""
        df = to_dataframe(sample_records)

        # Primera fila
        assert df.iloc[0]['oficina solicitante'] == '0520'
        assert df.iloc[0]['oficina target'] == '0520'

        # Segunda fila
        assert df.iloc[1]['oficina solicitante'] == '0969'
        assert df.iloc[1]['oficina target'] == '0969'

    def test_dataframe_column_mapping(self, sample_records):
        """Los valores mapean correctamente a las columnas."""
        df = to_dataframe(sample_records)

        # Verificar primera fila
        row0 = df.iloc[0]
        assert row0['timestamp'] == '2026-09-01T00:02:39.862105Z'
        assert row0['updated_at'] == '2026-09-01T00:02:52.868586Z'
        assert row0['id'] == 'b5ab6865ca8ac9629ff2eb303637d408'
        assert row0['solicitante'] == 'admsistemas520'
        assert row0['target'] == '520000228'


class TestWriteCsv:
    """Tests para write_csv."""

    def test_write_csv_creates_file(self, sample_records, tmp_path):
        """write_csv crea el archivo CSV."""
        output_file = tmp_path / "report.csv"
        write_csv(sample_records, str(output_file))
        assert output_file.exists()

    def test_csv_can_be_read_back(self, sample_records, tmp_path):
        """El CSV escrito puede releerse."""
        output_file = tmp_path / "report.csv"
        write_csv(sample_records, str(output_file))

        df = pd.read_csv(output_file, dtype=str)
        assert len(df) == len(sample_records)

    def test_csv_round_trip_preserves_all_data(self, sample_records, tmp_path):
        """Todos los datos se preservan en el pipeline."""
        output_file = tmp_path / "report.csv"
        write_csv(sample_records, str(output_file))

        df = pd.read_csv(output_file, dtype=str)
        df_from_records = to_dataframe(sample_records)
        df_from_records = df_from_records.replace('', float('nan'))

        pd.testing.assert_frame_equal(df, df_from_records)

    def test_csv_headers_match_columns(self, sample_records, tmp_path):
        """Los encabezados del CSV coinciden con COLUMNS."""
        output_file = tmp_path / "report.csv"
        write_csv(sample_records, str(output_file))

        df = pd.read_csv(output_file, dtype=str)
        expected_headers = [header for header, _ in COLUMNS]

        assert list(df.columns) == expected_headers

    def test_csv_content_correctness(self, sample_records, tmp_path):
        """El contenido del CSV es correcto."""
        output_file = tmp_path / "report.csv"
        write_csv(sample_records, str(output_file))

        df = pd.read_csv(output_file, dtype=str)

        # Verificar algunos valores específicos de la primera fila
        row0 = df.iloc[0]
        assert row0['timestamp'] == '2026-09-01T00:02:39.862105Z'
        assert row0['solicitante'] == 'admsistemas520'
        assert row0['target'] == '520000228'
        assert row0['acción'] == 'resetuser'
        assert row0['sistema'] == 'ADManager'
