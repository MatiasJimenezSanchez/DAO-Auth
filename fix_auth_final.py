import subprocess, re

C = "web"
def get(p):
    return subprocess.run(["docker-compose","exec","-T",C,"cat",p], capture_output=True, text=True).stdout
def put(local, cp, content):
    open(local,"w",encoding="utf-8").write(content)
    subprocess.run(["docker-compose","cp",local,f"{C}:{cp}"], capture_output=True)
    print(f"  ✅ {cp}")

src = get("/code/tests/content/test_content_hierarchy.py")

OLD = '''        payload = {
            "title": "No Desc Sim",
            "slug": "no-desc-sim",
            "company_id": base_company["id"],
            "category_id": base_category["id"]
            # short_description omitida intencionalmente
        }
        res = client.post("/api/v1/simulaciones", json=payload)
        assert res.status_code in [422, 400], f"Esperado 422, got {res.status_code}: {res.text}"'''

NEW = '''        sim_data = {
            "title": "No Desc Sim",
            "slug": "no-desc",
            "short_description": "",
            "company_id": base_company.id,
            "category_id": base_category.id
        }
        res = client.post("/api/v1/simulaciones", json=sim_data)
        assert res.status_code in [422, 400]'''

src = src.replace(OLD, NEW)
put("tests/content/test_content_hierarchy.py", "/code/tests/content/test_content_hierarchy.py", src)

r = subprocess.run(
    ["docker-compose","exec","-T",C,"pytest",
     "tests/content/test_content_hierarchy.py::TestContentValidation::test_simulation_description_required",
     "-v","--tb=short"],
    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
)
print(r.stdout[-1500:])