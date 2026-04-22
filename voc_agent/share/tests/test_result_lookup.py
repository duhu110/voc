from voc_agent.share.tools.fetch_enabled_categories import CATEGORY_QUERY
from voc_agent.share.tools.fetch_enabled_tags import TAG_QUERY
from voc_agent.share.tools.result_lookup import (
    build_category_lookup,
    build_tag_lookup,
    resolve_category_id,
    resolve_tag_id,
)


def test_build_category_lookup_indexes_by_code() -> None:
    categories = [
        {'id': 11, 'code': 'RULE_PROCESS', 'name': '办理规则争议'},
        {'id': 12, 'code': 'FEE_PACKAGE', 'name': '套餐收费争议'},
    ]

    lookup = build_category_lookup(categories)

    assert lookup['RULE_PROCESS']['id'] == 11
    assert lookup['FEE_PACKAGE']['name'] == '套餐收费争议'


def test_resolve_category_id_returns_id_for_known_code() -> None:
    categories = [
        {'id': 11, 'code': 'RULE_PROCESS', 'name': '办理规则争议'},
    ]

    assert resolve_category_id('RULE_PROCESS', categories) == 11
    assert resolve_category_id('UNKNOWN', categories) is None


def test_build_tag_lookup_indexes_by_group_and_code() -> None:
    tags = [
        {'id': 21, 'group_code': 'PRODUCT', 'code': 'MOBILE', 'name': '移动业务'},
        {'id': 22, 'group_code': 'REQUEST', 'code': 'REFUND', 'name': '退费'},
    ]

    lookup = build_tag_lookup(tags)

    assert lookup[('PRODUCT', 'MOBILE')]['id'] == 21
    assert lookup[('REQUEST', 'REFUND')]['name'] == '退费'


def test_resolve_tag_id_returns_id_for_known_group_and_code() -> None:
    tags = [
        {'id': 21, 'group_code': 'PRODUCT', 'code': 'MOBILE', 'name': '移动业务'},
    ]

    assert resolve_tag_id('PRODUCT', 'MOBILE', tags) == 21
    assert resolve_tag_id('PRODUCT', 'UNKNOWN', tags) is None


def test_enabled_category_query_selects_id_for_result_mapping() -> None:
    assert 'select' in str(CATEGORY_QUERY).lower()
    assert 'id,' in str(CATEGORY_QUERY).lower()


def test_enabled_tag_query_selects_id_for_result_mapping() -> None:
    assert 'select' in str(TAG_QUERY).lower()
    assert 't.id' in str(TAG_QUERY).lower()
