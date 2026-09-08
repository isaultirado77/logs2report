import pytest
from pathlib import Path
from logs2report.reader import read_operations
from logs2report.extract import is_reset_operation, _parse_request


@pytest.fixture
def real_log():
    """Usa el log real de datos."""
    log_path = Path('data/2026-09-01.log')
    if not log_path.exists():
        pytest.skip("data/2026-09-01.log not found")
    return log_path


class TestIsResetOperation:
    """Tests para is_reset_operation."""

    def test_reset_operation_recognized(self, real_log):
        """Una operación de reseteo se reconoce correctamente."""
        operations = read_operations(str(real_log))

        # Tomar la primera operación del log real
        first_op_id = list(operations.keys())[0]
        first_operation = operations[first_op_id]

        assert is_reset_operation(first_operation) is True

    def test_all_operations_are_reset_operations(self, real_log):
        """Todas las operaciones en el log son de reseteo."""
        operations = read_operations(str(real_log))

        for op_id, records in operations.items():
            assert is_reset_operation(records), f"Operation {op_id} not recognized as reset"

    def test_empty_operation_is_not_reset(self):
        """Una operación vacía no es reconocida como reseteo."""
        assert is_reset_operation([]) is False

    def test_operation_without_reset_endpoint(self):
        """Una operación sin el endpoint no es reseteo."""
        fake_operation = [
            {
                'timestamp': '2026-09-01T00:00:00.000000Z',
                'level': 'INFO',
                'content': 'Some other HTTP request'
            }
        ]
        assert is_reset_operation(fake_operation) is False


class TestParseRequest:
    """Tests para _parse_request."""

    def test_parse_request_extracts_fields(self, real_log):
        """Se extraen timestamp, requester y target correctamente."""
        operations = read_operations(str(real_log))

        # Primera operación real
        first_op_id = list(operations.keys())[0]
        first_operation = operations[first_op_id]

        result = _parse_request(first_operation)

        assert 'timestamp' in result
        assert 'requester' in result
        assert 'target' in result

    def test_timestamp_is_iso_format(self, real_log):
        """El timestamp tiene formato ISO."""
        operations = read_operations(str(real_log))
        first_operation = list(operations.values())[0]

        result = _parse_request(first_operation)
        timestamp = result['timestamp']

        assert timestamp.startswith('2026-09-01T')
        assert 'Z' in timestamp

    def test_requester_and_target_are_strings(self, real_log):
        """Requester y target son strings no vacíos."""
        operations = read_operations(str(real_log))
        first_operation = list(operations.values())[0]

        result = _parse_request(first_operation)

        assert isinstance(result['requester'], str)
        assert isinstance(result['target'], str)
        assert len(result['requester']) > 0
        assert len(result['target']) > 0

    def test_parse_request_specific_values(self, real_log):
        """Verificar valores específicos del log real."""
        operations = read_operations(str(real_log))

        # Primera operación debe ser admsistemas520 -> 520000228
        first_operation = list(operations.values())[0]
        result = _parse_request(first_operation)

        assert result['requester'] == 'admsistemas520'
        assert result['target'] == '520000228'
        assert result['timestamp'] == '2026-09-01T00:02:39.862105Z'

    def test_parse_request_second_operation(self, real_log):
        """Segunda operación del log."""
        operations = read_operations(str(real_log))
        second_operation = list(operations.values())[1]

        result = _parse_request(second_operation)

        assert result['requester'] == 'admsistemas969'
        assert result['target'] == '969000093'
        assert result['timestamp'] == '2026-09-01T00:03:40.445253Z'

    def test_parse_request_raises_on_missing_reset(self):
        """Levanta excepción si no hay reset en operación."""
        fake_operation = [
            {
                'timestamp': '2026-09-01T00:00:00.000000Z',
                'level': 'INFO',
                'content': 'Some other HTTP request'
            }
        ]
        with pytest.raises(ValueError, match="No reset request found"):
            _parse_request(fake_operation)

    def test_parse_request_handles_various_office_codes(self, real_log):
        """Las operaciones con distintos códigos de oficina se parsean."""
        operations = read_operations(str(real_log))

        # Recolectar todos los requesters para ver si hay variedad
        requesters = set()
        for operation in operations.values():
            try:
                result = _parse_request(operation)
                requesters.add(result['requester'])
            except ValueError:
                pass

        # Debe haber al menos 3 requesters diferentes
        assert len(requesters) >= 3
