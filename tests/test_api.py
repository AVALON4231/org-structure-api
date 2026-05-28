def test_create_department(client):
    resp = client.post("/departments/", json={"name": "HQ", "parent_id": None})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "HQ"
    assert data["parent_id"] is None

def test_create_employee_not_found(client):
    resp = client.post("/departments/999/employees/", json={
        "full_name": "John Doe",
        "position": "Manager"
    })
    assert resp.status_code == 404

def test_move_department_cycle(client):
    d1 = client.post("/departments/", json={"name": "A"}).json()
    d2 = client.post("/departments/", json={"name": "B", "parent_id": d1["id"]}).json()
    # Попытка переместить A в B (цикл)
    resp = client.patch(f"/departments/{d1['id']}", json={"parent_id": d2["id"]})
    assert resp.status_code == 409

def test_delete_cascade(client):
    d = client.post("/departments/", json={"name": "Temp"}).json()
    e = client.post(f"/departments/{d['id']}/employees/", json={
        "full_name": "Alice", "position": "Dev"
    }).json()
    resp = client.delete(f"/departments/{d['id']}?mode=cascade")
    assert resp.status_code == 204
    # Проверим, что отдел удалён
    resp = client.get(f"/departments/{d['id']}")
    assert resp.status_code == 404