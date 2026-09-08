import pytest
from pathlib import Path
from logs2report.reader import read_operations

FRAGMENT_CONTENT = """2026-09-01T00:02:39.862105Z | INFO [operation_Id=b5ab6865ca8ac9629ff2eb303637d408] | HTTP Request: http://apitools.com:8000/v3/users_admin/resetuser?sAMAccountName_requester=admsistemas520&sAMAccountName_target=520000228 "HTTP/1.1" 200
2026-09-01T00:02:41.536428Z | INFO [operation_Id=b5ab6865ca8ac9629ff2eb303637d408] | HTTP Request: GET https://admanager.retailstore.com/RestAPI/SearchUser?domainName=retailstore.com&AuthToken=[REDACTED_TOKEN]&range=2&startIndex=1&filter=%28sAMAccountName%3Aequal%3A520000228%29 "HTTP/1.1 200 "
2026-09-01T00:02:41.53718Z | INFO [operation_Id=b5ab6865ca8ac9629ff2eb303637d408] | ADManagerRawClient.get_users_list_info_from_admanager invoked
Params to execute POST to SearchUser: {'domainName': 'retailstore.com', 'AuthToken': '[REDACTED_TOKEN]', 'range': 2, 'startIndex': 1, 'filter': '(sAMAccountName:equal:520000228)'}, Raw Response: {"UsersList":[{"EXTENSIONATTRIBUTE3":"C336","FIRST_NAME":"Nombre_86f0740bf6","LAST_NAME":"Apellido_86f0740bf6","OFFICE":"0520","SAM_ACCOUNT_NAME":"520000228"}],"count":1,"statusMessage":"","status":"SUCCESS"}

, Raw status_code: 200, Raw reason_phrase:
2026-09-01T00:03:40.445253Z | INFO [operation_Id=f7dde1e1995c0c89366858c6f494dc4d] | HTTP Request: http://apitools.com:8000/v3/users_admin/resetuser?sAMAccountName_requester=admsistemas969&sAMAccountName_target=969000093 "HTTP/1.1" 200
2026-09-01T00:02:41.54504Z | INFO [operation_Id=b5ab6865ca8ac9629ff2eb303637d408] | HTTP Request: GET https://admanager.retailstore.com/RestAPI/SearchUser?domainName=retailstore.com&AuthToken=[REDACTED_TOKEN]&range=2&startIndex=1&filter=%28sAMAccountName%3Aequal%3Aadmsistemas520%29 "HTTP/1.1 200 "
2026-09-01T00:02:41.545614Z | INFO [operation_Id=b5ab6865ca8ac9629ff2eb303637d408] | ADManagerRawClient.get_users_list_info_from_admanager invoked
Params to execute POST to SearchUser: {'domainName': 'retailstore.com', 'AuthToken': '[REDACTED_TOKEN]', 'range': 2, 'startIndex': 1, 'filter': '(sAMAccountName:equal:admsistemas520)'}, Raw Response: {"UsersList":[{"FIRST_NAME":"Nombre_d216ff1cda","LAST_NAME":"Apellido_d216ff1cda","OFFICE":"0520","SAM_ACCOUNT_NAME":"admsistemas520"}],"count":1,"statusMessage":"","status":"SUCCESS"}

, Raw status_code: 200, Raw reason_phrase:
2026-09-01T00:03:42.017586Z | INFO [operation_Id=f7dde1e1995c0c89366858c6f494dc4d] | HTTP Request: GET https://admanager.retailstore.com/RestAPI/SearchUser?domainName=retailstore.com&AuthToken=[REDACTED_TOKEN]&range=2&startIndex=1&filter=%28sAMAccountName%3Aequal%3Aadmsistemas969%29 "HTTP/1.1 200 "
2026-09-01T00:03:42.018461Z | INFO [operation_Id=f7dde1e1995c0c89366858c6f494dc4d] | ADManagerRawClient.get_users_list_info_from_admanager invoked
Params to execute POST to SearchUser: {'domainName': 'retailstore.com', 'AuthToken': '[REDACTED_TOKEN]', 'range': 2, 'startIndex': 1, 'filter': '(sAMAccountName:equal:admsistemas969)'}, Raw Response: {"UsersList":[{"FIRST_NAME":"Nombre_b52d7f1bdc","LAST_NAME":"Apellido_b52d7f1bdc","OFFICE":"0969","SAM_ACCOUNT_NAME":"admsistemas969"}],"count":1}

, Raw status_code: 200, Raw reason_phrase:
2026-09-01T00:02:52.868586Z | INFO [operation_Id=b5ab6865ca8ac9629ff2eb303637d408] | HTTP Request: POST https://admanager.retailstore.com/RestAPI/ResetPwd?AuthToken=[REDACTED_TOKEN]&PRODUCT_NAME=smartdeskbot&domainName=retailstore.com&pwd=[REDACTED_PASSWORD]&inputFormat=%5B%7B%22userPrincipalName%22%3A%22520000228%40retailstore.com%22%7D%5D "HTTP/1.1 200 "
2026-09-01T00:02:52.869206Z | INFO [operation_Id=b5ab6865ca8ac9629ff2eb303637d408] | ADM-Raw response | status: 200 | body: [{'sAMAccountName': '520000228', 'reset': 'yes', 'statusMessage': 'Password reset successful.', 'status': '1'}]
2026-09-01T00:03:50.200731Z | INFO [operation_Id=f7dde1e1995c0c89366858c6f494dc4d] | HTTP Request: POST https://admanager.retailstore.com/RestAPI/ResetPwd?AuthToken=[REDACTED_TOKEN]&PRODUCT_NAME=smartdeskbot&domainName=retailstore.com&pwd=[REDACTED_PASSWORD]&inputFormat=%5B%7B%22userPrincipalName%22%3A%22969000093%40retailstore.com%22%7D%5D "HTTP/1.1 200 "
2026-09-01T00:03:50.201411Z | INFO [operation_Id=f7dde1e1995c0c89366858c6f494dc4d] | ADM-Raw response | status: 200 | body: [{'sAMAccountName': '969000093', 'reset': 'yes', 'statusMessage': 'Password reset successful.', 'status': '1'}]
"""

@pytest.fixture
def real_log_fragment(tmp_path):
    """Fragmento real del log 2026-09-01 (primeras 2 operaciones intercaladas)."""
    log_file = tmp_path / "test_log.log"
    log_file.write_text(FRAGMENT_CONTENT, encoding='utf-8')
    return log_file


class TestReadOperations:
    """Tests para reader.read_operations()."""

    def test_read_returns_dict_of_operations(self, real_log_fragment):
        """El resultado es un dict con operation_Id como claves."""
        operations = read_operations(str(real_log_fragment))
        assert isinstance(operations, dict)
        assert 'b5ab6865ca8ac9629ff2eb303637d408' in operations
        assert 'f7dde1e1995c0c89366858c6f494dc4d' in operations

    def test_each_operation_is_list_of_records(self, real_log_fragment):
        """Cada operación es una lista de registros."""
        operations = read_operations(str(real_log_fragment))
        for op_id, records in operations.items():
            assert isinstance(records, list)
            assert len(records) > 0
            for record in records:
                assert isinstance(record, dict)
                assert 'timestamp' in record
                assert 'level' in record
                assert 'content' in record

    def test_records_have_required_fields(self, real_log_fragment):
        """Cada registro tiene timestamp, level y content."""
        operations = read_operations(str(real_log_fragment))
        for op_id, records in operations.items():
            for record in records:
                assert isinstance(record['timestamp'], str)
                assert isinstance(record['level'], str)
                assert isinstance(record['content'], str)
                # El timestamp debe ser ISO format
                assert record['timestamp'].startswith('2026-09-01T')
                assert record['level'] in ['INFO', 'DEBUG', 'WARN', 'ERROR']

    def test_multiline_records_are_preserved(self, real_log_fragment):
        """Los registros multilínea se preservan en el content."""
        operations = read_operations(str(real_log_fragment))
        op_b5ab = operations['b5ab6865ca8ac9629ff2eb303637d408']

    #     # El segundo registro debe ser multilínea
        second_record = op_b5ab[2]
        assert '\n' in second_record['content']
        assert 'ADManagerRawClient' in second_record['content']
        assert 'Params to execute POST' in second_record['content']
        assert 'Raw Response:' in second_record['content']

    def test_operations_are_intercalated(self, real_log_fragment):
        """Las operaciones intercaladas se agrupan correctamente por operation_Id."""
        operations = read_operations(str(real_log_fragment))

        # Primera operación (b5ab) debe tener 7 registros
        # Segunda operación (f7dde) debe tener 5 registros
        op_b5ab = operations['b5ab6865ca8ac9629ff2eb303637d408']
        op_f7dde = operations['f7dde1e1995c0c89366858c6f494dc4d']

        assert len(op_b5ab) == 7
        assert len(op_f7dde) == 5

    def test_operation_id_extracted_from_each_record(self, real_log_fragment):
        """Cada registro está bajo el operation_Id correcto."""
        operations = read_operations(str(real_log_fragment))
        op_b5ab = operations['b5ab6865ca8ac9629ff2eb303637d408']
        op_f7dde = operations['f7dde1e1995c0c89366858c6f494dc4d']

    #     # Todos los records de b5ab deben contener el operation_Id
        for record in op_b5ab:
            assert 'operation_Id=b5ab6865ca8ac9629ff2eb303637d408' in record['content']

        # Todos los records de f7dde deben contener el operation_Id
        for record in op_f7dde:
            assert 'operation_Id=f7dde1e1995c0c89366858c6f494dc4d' in record['content']

    # def test_timestamp_level_extracted_correctly(self, real_log_fragment):
        """El timestamp y level se extraen en cada línea con timestamp."""
        operations = read_operations(str(real_log_fragment))
        op_b5ab = operations['b5ab6865ca8ac9629ff2eb303637d408']

        # Primer registro debe tener timestamp específico
        assert op_b5ab[0]['timestamp'] == '2026-09-01T00:02:39.862105Z'
        assert op_b5ab[0]['level'] == 'INFO'

    #     # Segundo registro
        assert op_b5ab[1]['timestamp'] == '2026-09-01T00:02:41.536428Z'
        assert op_b5ab[1]['level'] == 'INFO'

    def test_empty_lines_are_preserved_in_multiline_content(self, real_log_fragment):
        """Las líneas vacías en registros multilínea se preservan."""
        operations = read_operations(str(real_log_fragment))
        op_b5ab = operations['b5ab6865ca8ac9629ff2eb303637d408']

        # El tercer registro debe contener líneas vacías
        third_record = op_b5ab[2]
        # Debe haber una línea vacía seguida de ", Raw status_code: 200, Raw reason_phrase:"
        assert '\n\n' in third_record['content'] or '\n,' in third_record['content']

    def test_file_not_found_raises_error(self):
        """Lanzar excepción si el archivo no existe."""
        with pytest.raises(FileNotFoundError):
            read_operations('/ruta/inexistente.log')

    def test_real_log_file(self):
        """Prueba con el archivo real del log (estadísticas básicas)."""
        log_path = Path('data/2026-09-01.log')
        if log_path.exists():
            operations = read_operations(str(log_path))

            # Debe haber exactamente 40 operaciones
            assert len(operations) == 40

            # Cada operación debe tener registros
            for op_id, records in operations.items():
                assert len(records) > 0
                # op_id debe ser hex de 32 caracteres
                assert len(op_id) == 32

                assert all(c in '0123456789abcdef' for c in op_id)