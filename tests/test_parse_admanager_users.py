import pytest
from pathlib import Path
from logs2report.reader import read_operations
from logs2report.extract import _parse_admanager_users


@pytest.fixture
def real_log():
    """Usa el log real de datos."""
    log_path = Path('data/2026-09-01.log')
    if not log_path.exists():
        pytest.skip("data/2026-09-01.log not found")
    return log_path


class TestParseAdmanagerUsers:
    """Tests para _parse_admanager_users."""

    def test_parse_admanager_returns_dict(self, real_log):
        """La función devuelve un diccionario."""
        operations = read_operations(str(real_log))
        first_operation = list(operations.values())[0]
        result = _parse_admanager_users(first_operation)
        assert isinstance(result, dict)

    def test_parse_admanager_extracts_two_users(self, real_log):
        """Se extraen dos usuarios por operación."""
        operations = read_operations(str(real_log))
        first_operation = list(operations.values())[0]
        result = _parse_admanager_users(first_operation)
        assert len(result) == 2

    def test_parse_admanager_indexed_by_sam_account_name(self, real_log):
        """Los usuarios están indexados por SAM_ACCOUNT_NAME."""
        operations = read_operations(str(real_log))
        first_operation = list(operations.values())[0]
        result = _parse_admanager_users(first_operation)

        # Las claves deben ser SAM_ACCOUNT_NAME
        assert 'admsistemas520' in result or 'admsistemas969' in result
        for key in result.keys():
            assert isinstance(key, str)
            assert len(key) > 0

    def test_each_user_has_required_fields(self, real_log):
        """Cada usuario tiene FIRST_NAME, LAST_NAME, OFFICE."""
        operations = read_operations(str(real_log))
        first_operation = list(operations.values())[0]
        result = _parse_admanager_users(first_operation)

        for sam_account, user_data in result.items():
            assert 'FIRST_NAME' in user_data
            assert 'LAST_NAME' in user_data
            assert 'OFFICE' in user_data

    def test_office_preserves_leading_zero(self, real_log):
        """OFFICE conserva el cero inicial (e.g., '0520', no '520')."""
        operations = read_operations(str(real_log))
        first_operation = list(operations.values())[0]
        result = _parse_admanager_users(first_operation)

        for sam_account, user_data in result.items():
            office = user_data['OFFICE']
            # OFFICE debe empezar con '0'
            assert office.startswith('0'), f"OFFICE '{office}' should start with '0'"
            # OFFICE debe tener 4 caracteres
            assert len(office) == 4, f"OFFICE '{office}' should have 4 characters"

    def test_first_operation_specific_values(self, real_log):
        """Primera operación: admsistemas520 y 520000228."""
        operations = read_operations(str(real_log))
        first_operation = list(operations.values())[0]
        result = _parse_admanager_users(first_operation)

        # Verificar que tenemos ambas cuentas
        assert 'admsistemas520' in result
        assert '520000228' in result

        # Verificar datos de admsistemas520
        admsistemas_data = result['admsistemas520']
        assert admsistemas_data['FIRST_NAME'] == 'Nombre_d216ff1cda'
        assert admsistemas_data['LAST_NAME'] == 'Apellido_d216ff1cda'
        assert admsistemas_data['OFFICE'] == '0520'

        # Verificar datos de 520000228
        target_data = result['520000228']
        assert target_data['FIRST_NAME'] == 'Nombre_86f0740bf6'
        assert target_data['LAST_NAME'] == 'Apellido_86f0740bf6'
        assert target_data['OFFICE'] == '0520'

    def test_second_operation_different_order(self, real_log):
        """Segunda operación: orden invertido respecto a la primera.

        La primera operación consulta primero el target (520000228),
        luego el requester (admsistemas520).
        La segunda operación consulta primero el requester (admsistemas969),
        luego el target (969000093).
        """
        operations = read_operations(str(real_log))
        second_operation = list(operations.values())[1]
        result = _parse_admanager_users(second_operation)

        # Ambas cuentas deben estar presentes sin importar el orden
        assert 'admsistemas969' in result
        assert '969000093' in result

        # Verificar datos de admsistemas969
        admsistemas_data = result['admsistemas969']
        assert admsistemas_data['FIRST_NAME'] == 'Nombre_b52d7f1bdc'
        assert admsistemas_data['LAST_NAME'] == 'Apellido_b52d7f1bdc'
        assert admsistemas_data['OFFICE'] == '0969'

        # Verificar datos de 969000093
        target_data = result['969000093']
        assert target_data['FIRST_NAME'] == 'Nombre_d1e1fa4a78'
        assert target_data['LAST_NAME'] == 'Apellido_d1e1fa4a78'
        assert target_data['OFFICE'] == '0969'

    def test_order_independence(self, real_log):
        """El resultado es independiente del orden de consultas en el log."""
        operations = read_operations(str(real_log))
        ops_list = list(operations.values())

        # Comparar primera y segunda operación: ambas deben tener
        # exactamente dos usuarios sin importar el orden de aparición
        result1 = _parse_admanager_users(ops_list[0])
        result2 = _parse_admanager_users(ops_list[1])

        assert len(result1) == 2
        assert len(result2) == 2

        # Las claves (SAM_ACCOUNT_NAME) deben coincidir con requester y target
        # de cada operación (no verificamos aquí, pero el resultado debe ser consistente)
        assert all(isinstance(v, dict) for v in result1.values())
        assert all(isinstance(v, dict) for v in result2.values())
