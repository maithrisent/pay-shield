def test_pay_by_alias_success(client, auth_headers, alias_string):
    resp = client.post("/transactions/pay-by-alias",
                        json={"alias_string": alias_string, "amount_paise": 1000},
                        headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"

def test_pay_by_alias_unknown_alias(client, auth_headers):
    resp = client.post("/transactions/pay-by-alias",
                        json={"alias_string": "nonexistent@payshield", "amount_paise": 1000},
                        headers=auth_headers)
    assert resp.status_code == 404