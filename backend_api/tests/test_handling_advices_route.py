from __future__ import annotations

from backend_api.routes.handling_advices import _params


def test_handling_advice_params_include_scope_filters() -> None:
    params = _params(
        query="  退费  ",
        status="active",
        primary_leaf_code="FEE",
        product_tag_code="MOBILE",
        request_tag_code="REFUND",
        page=2,
        page_size=50,
    )

    assert params["query"] == "退费"
    assert params["query_like"] == "%退费%"
    assert params["status"] == "active"
    assert params["primary_leaf_code"] == "FEE"
    assert params["product_tag_code"] == "MOBILE"
    assert params["request_tag_code"] == "REFUND"
    assert params["limit"] == 50
    assert params["offset"] == 50


def test_handling_advice_params_normalize_blank_filters() -> None:
    params = _params(
        query="",
        status=" ",
        primary_leaf_code=" ",
        product_tag_code=" ",
        request_tag_code=" ",
        page=0,
        page_size=200,
    )

    assert params["query"] is None
    assert params["query_like"] is None
    assert params["status"] is None
    assert params["primary_leaf_code"] is None
    assert params["product_tag_code"] is None
    assert params["request_tag_code"] is None
    assert params["limit"] == 100
    assert params["offset"] == 0
