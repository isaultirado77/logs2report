import pytest
from pathlib import Path
from logs2report.reader import read_operations
from logs2report.extract import extract_reset


@pytest.fixture
def real_log():
    """Usa el log real de datos."""
    log_path = Path('data/2026-09-01.log')
    if not log_path.exists():
        pytest.skip("data/2026-09-01.log not found")
    return log_path


class TestExtractReset:
    """Tests para extract_reset."""

    def test_extract_reset_returns_reset_record(self, real_log):
        """extract_reset devuelve un ResetRecord."""
        operations = read_operations(str(real_log))
        first_operation = list(operations.values())[0]
        result = extract_reset(first_operation)

        assert result is not None
        assert hasattr(result, 'timestamp')
        assert hasattr(result, 'updated_at')
        assert hasattr(result, 'operation_id')

    def test_first_operation_all_fields(self, real_log):
        """Primera operación: verificar todos los doce campos."""
        operations = read_operations(str(real_log))
        first_operation = list(operations.values())[0]
        record = extract_reset(first_operation)

        # 1. timestamp
        assert record.timestamp == '2026-09-01T00:02:39.862105Z'

        # 2. updated_at
        assert record.updated_at == '2026-09-01T00:02:52.868586Z'

        # 3. operation_id
        assert record.operation_id == 'b5ab6865ca8ac9629ff2eb303637d408'

        # 4. requester
        assert record.requester == 'admsistemas520'

        # 5. target
        assert record.target == '520000228'

        # 6. action
        assert record.action == 'resetuser'

        # 7. system
        assert record.system == 'ADManager'

        # 8. requester_name
        assert record.requester_name == 'Nombre_d216ff1cda Apellido_d216ff1cda'

        # 9. target_name
        assert record.target_name == 'Nombre_86f0740bf6 Apellido_86f0740bf6'

        # 10. requester_office
        assert record.requester_office == '0520'

        # 11. target_office
        assert record.target_office == '0520'

        # 12. result (status / statusMessage)
        assert '1' in record.result  # status='1'
        assert 'Password reset successful' in record.result

        # 13. requisitos (debe estar vacío por defecto)
        assert record.requisitos == ''

    def test_second_operation_all_fields(self, real_log):
        """Segunda operación: verificar todos los campos."""
        operations = read_operations(str(real_log))
        second_operation = list(operations.values())[1]
        record = extract_reset(second_operation)

        # Verificar campos básicos
        assert record.timestamp == '2026-09-01T00:03:40.445253Z'
        assert record.updated_at == '2026-09-01T00:03:50.200731Z'
        assert record.operation_id == 'f7dde1e1995c0c89366858c6f494dc4d'
        assert record.requester == 'admsistemas969'
        assert record.target == '969000093'
        assert record.action == 'resetuser'
        assert record.system == 'ADManager'

        # Verificar nombres
        assert record.requester_name == 'Nombre_b52d7f1bdc Apellido_b52d7f1bdc'
        assert record.target_name == 'Nombre_d1e1fa4a78 Apellido_d1e1fa4a78'

        # Verificar oficinas
        assert record.requester_office == '0969'
        assert record.target_office == '0969'

        # Verificar resultado
        assert '1' in record.result
        assert 'Password reset successful' in record.result

    def test_all_required_fields_present(self, real_log):
        """Todos los campos requeridos están presentes."""
        operations = read_operations(str(real_log))
        first_operation = list(operations.values())[0]
        record = extract_reset(first_operation)

        required_fields = [
            'timestamp', 'updated_at', 'operation_id', 'requester', 'target',
            'action', 'system', 'requester_name', 'target_name',
            'requester_office', 'target_office', 'result', 'requisitos'
        ]

        for field in required_fields:
            assert hasattr(record, field), f"Missing field: {field}"
            value = getattr(record, field)
            assert value is not None, f"Field {field} is None"

    def test_operation_id_format(self, real_log):
        """operation_id tiene formato hex de 32 caracteres."""
        operations = read_operations(str(real_log))

        for op_id_str, operation in list(operations.items())[:5]:
            record = extract_reset(operation)
            assert len(record.operation_id) == 32
            assert all(c in '0123456789abcdef' for c in record.operation_id)
            assert record.operation_id == op_id_str

    def test_names_format(self, real_log):
        """Los nombres tienen formato 'Nombre Apellido'."""
        operations = read_operations(str(real_log))

        for operation in list(operations.values())[:3]:
            record = extract_reset(operation)
            # Ambos nombres deben tener al menos dos palabras (Nombre Apellido)
            assert len(record.requester_name.split()) >= 2
            assert len(record.target_name.split()) >= 2

    def test_office_format(self, real_log):
        """OFFICE tiene formato 4 dígitos con cero inicial."""
        operations = read_operations(str(real_log))

        for operation in list(operations.values())[:3]:
            record = extract_reset(operation)
            assert record.requester_office.startswith('0')
            assert len(record.requester_office) == 4
            assert record.target_office.startswith('0')
            assert len(record.target_office) == 4

    def test_result_format(self, real_log):
        """result tiene formato 'status / statusMessage'."""
        operations = read_operations(str(real_log))
        first_operation = list(operations.values())[0]
        record = extract_reset(first_operation)

        # result debe contener un '/'
        assert ' / ' in record.result
        parts = record.result.split(' / ')
        assert len(parts) == 2
        # El status debe ser '1' (éxito) en el MVP
        assert '1' in parts[0]
        # statusMessage debe ser no vacío
        assert len(parts[1]) > 0
