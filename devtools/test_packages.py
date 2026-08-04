from dataclasses import dataclass
from fluxus.enums import FluxusIOType, ContentFormat
from devtools.settings import *
from devtools.tools.dev_orm import (
    DevTargetDataText,
    DevTargetDataBlob,
    DevSourceDataBlob,
    DevSourceDataText,
)

"""
Devtools test packages — pre-configured InputArgs kwargs sets for rapid
manual pipeline testing via `fluxus-dev test --inject <key>`.

This module is a living catalog of test scenarios, not an exhaustive
suite. New packages should be added as new source/target combinations,
error cases, or edge cases become relevant to test manually.

Current coverage:

  1-500   Success scenarios: all source x target type combinations
        (file, db, api), e.g. file->file, file->db, file->api,
        db->file, db->db, db->api, api->file, api->db, api->api.
        Each package represents a valid, expected-to-succeed run.

  501-999 Error scenarios: invalid parameter combinations meant to
        trigger specific validation or strategy failures — e.g. a
        db source/target with a nonexistent table name, a malformed
        api url, an unsupported file extension. Each package should
        map to a known, expected exception (see fluxus.exceptions.errors)
        so failures can be manually confirmed against expectations
        rather than treated as surprises.

Numbering leaves gaps (10, 20+) intentionally, to allow inserting new
scenarios into a category without renumbering existing ones.
"""


@dataclass
class TestPackage:
    source_type: FluxusIOType
    source_address: str
    target_type: FluxusIOType
    target_address: str
    transform_strategy_id: int
    source_table: str | None = None
    target_table: str | None = None
    target_format: ContentFormat = ContentFormat.JSON


TEST_PACKAGES: dict[int, TestPackage] = {
    1: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "comments.json"),
        target_type=FluxusIOType.FILE,
        target_address=str(DEV_TARGET_FILE_DIR / "output_json.json"),
        transform_strategy_id=1,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    2: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "comments.json"),
        target_type=FluxusIOType.DB,
        target_address=str(DEV_TARGET_DB_URL),
        transform_strategy_id=1,
        source_table=None,
        target_table=DevTargetDataText.__tablename__,
        target_format=ContentFormat.JSON,
    ),
    3: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "comments.json"),
        target_type=FluxusIOType.API,
        target_address=str(DEV_TARGET_API_URL),
        transform_strategy_id=1,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    4: TestPackage(
        source_type=FluxusIOType.DB,
        source_address=str(DEV_SOURCE_DB_URL),
        target_type=FluxusIOType.FILE,
        target_address=str(DEV_TARGET_FILE_DIR / "output_db.json"),
        transform_strategy_id=0,
        source_table=DevSourceDataText.__tablename__,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    5: TestPackage(
        source_type=FluxusIOType.DB,
        source_address=str(DEV_SOURCE_DB_URL),
        target_type=FluxusIOType.DB,
        target_address=str(DEV_TARGET_DB_URL),
        transform_strategy_id=0,
        source_table=DevSourceDataText.__tablename__,
        target_table=DevTargetDataText.__tablename__,
        target_format=ContentFormat.JSON,
    ),
    6: TestPackage(
        source_type=FluxusIOType.DB,
        source_address=str(DEV_SOURCE_DB_URL),
        target_type=FluxusIOType.API,
        target_address=str(DEV_TARGET_API_URL),
        transform_strategy_id=0,
        source_table=DevSourceDataText.__tablename__,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    7: TestPackage(
        source_type=FluxusIOType.API,
        source_address=str(DEV_SOURCE_API_URL),
        target_type=FluxusIOType.FILE,
        target_address=str(DEV_TARGET_FILE_DIR / "output_api.json"),
        transform_strategy_id=0,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    8: TestPackage(
        source_type=FluxusIOType.API,
        source_address=str(DEV_SOURCE_API_URL),
        target_type=FluxusIOType.DB,
        target_address=str(DEV_TARGET_DB_URL),
        transform_strategy_id=1,
        source_table=None,
        target_table=DevTargetDataText.__tablename__,
        target_format=ContentFormat.JSON,
    ),
    9: TestPackage(
        source_type=FluxusIOType.API,
        source_address=str(DEV_SOURCE_API_URL),
        target_type=FluxusIOType.API,
        target_address=str(DEV_TARGET_API_URL),
        transform_strategy_id=0,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    10: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "cities.csv"),
        target_type=FluxusIOType.FILE,
        target_address=str(DEV_TARGET_FILE_DIR / "output_csv.json"),
        transform_strategy_id=0,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    11: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "cities.csv"),
        target_type=FluxusIOType.DB,
        target_address=str(DEV_TARGET_DB_URL),
        transform_strategy_id=1,
        source_table=None,
        target_table=DevTargetDataText.__tablename__,
        target_format=ContentFormat.JSON,
    ),
    12: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "cities.csv"),
        target_type=FluxusIOType.API,
        target_address=str(DEV_TARGET_API_URL),
        transform_strategy_id=0,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    13: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "The World Wide Web project.htm"),
        target_type=FluxusIOType.FILE,
        target_address=str(DEV_TARGET_FILE_DIR / "output_html.json"),
        transform_strategy_id=0,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    14: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "The World Wide Web project.htm"),
        target_type=FluxusIOType.DB,
        target_address=str(DEV_TARGET_DB_URL),
        transform_strategy_id=0,
        source_table=None,
        target_table=DevTargetDataText.__tablename__,
        target_format=ContentFormat.JSON,
    ),
    15: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "The World Wide Web project.htm"),
        target_type=FluxusIOType.API,
        target_address=str(DEV_TARGET_API_URL),
        transform_strategy_id=0,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    16: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "cd_catalog.xml"),
        target_type=FluxusIOType.FILE,
        target_address=str(DEV_TARGET_FILE_DIR / "output_xml.json"),
        transform_strategy_id=0,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    17: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "cd_catalog.xml"),
        target_type=FluxusIOType.DB,
        target_address=str(DEV_TARGET_DB_URL),
        transform_strategy_id=1,
        source_table=None,
        target_table=DevTargetDataText.__tablename__,
        target_format=ContentFormat.JSON,
    ),
    18: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "cd_catalog.xml"),
        target_type=FluxusIOType.API,
        target_address=str(DEV_TARGET_API_URL),
        transform_strategy_id=0,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    19: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "sample-files.com-basic-text.docx"),
        target_type=FluxusIOType.FILE,
        target_address=str(DEV_TARGET_FILE_DIR / "output_docx.json"),
        transform_strategy_id=0,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    20: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "sample-files.com-basic-text.docx"),
        target_type=FluxusIOType.DB,
        target_address=str(DEV_TARGET_DB_URL),
        transform_strategy_id=0,
        source_table=None,
        target_table=DevTargetDataText.__tablename__,
        target_format=ContentFormat.JSON,
    ),
    21: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "sample-files.com-basic-text.docx"),
        target_type=FluxusIOType.API,
        target_address=str(DEV_TARGET_API_URL),
        transform_strategy_id=0,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    22: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "Free_Test_Data_100KB_XLSX.xlsx"),
        target_type=FluxusIOType.FILE,
        target_address=str(DEV_TARGET_FILE_DIR / "output_xlsx.json"),
        transform_strategy_id=0,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
    23: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "Free_Test_Data_100KB_XLSX.xlsx"),
        target_type=FluxusIOType.DB,
        target_address=str(DEV_TARGET_DB_URL),
        transform_strategy_id=0,
        source_table=None,
        target_table=DevTargetDataText.__tablename__,
        target_format=ContentFormat.JSON,
    ),
    24: TestPackage(
        source_type=FluxusIOType.FILE,
        source_address=str(DEV_SOURCE_FILE_DIR / "Free_Test_Data_100KB_XLSX.xlsx"),
        target_type=FluxusIOType.API,
        target_address=str(DEV_TARGET_API_URL),
        transform_strategy_id=0,
        source_table=None,
        target_table=None,
        target_format=ContentFormat.JSON,
    ),
}
