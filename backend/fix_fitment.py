import sys
sys.stdout.reconfigure(encoding='utf-8')
data = open('services/fitment_checker.py', encoding='utf-8').read()

# FIX 1: cap hole count at 20 (blocks 51x false positives from reversed text)
data = data.replace(
    'if 1 < dia < 300 and cnt < 100:',
    'if 1 < dia < 300 and 1 < cnt <= 20:'
)
print('Fix1 (hole count cap):', 'cnt <= 20' in data)

# FIX 2: purchased parts - bom_qty=1 since count already = BOM qty
data = data.replace(
    '                bom_qty=int(row.get("qty") or 1),',
    '                bom_qty=1,  # count on ThreadFeature already = BOM qty'
)
print('Fix2 (purchased bom_qty=1):', 'bom_qty=1,' in data)

# FIX 3: Add qty_map so Step-2-created profiles (custom parts) get bom_qty
# First add qty_map definition near desc_map
old3 = '    desc_map: Dict[str, str] = {\n        normalize_part_number(r.get("part_number", "")): (r.get("description") or "")\n        for r in bom_rows\n        if r.get("part_number")\n    }'
new3 = '''    desc_map: Dict[str, str] = {
        normalize_part_number(r.get("part_number", "")): (r.get("description") or "")
        for r in bom_rows
        if r.get("part_number")
    }
    # BOM quantity lookup for all parts (used to set bom_qty on custom part profiles)
    qty_map: Dict[str, int] = {
        normalize_part_number(r.get("part_number", "")): int(r.get("qty") or 1)
        for r in bom_rows
        if r.get("part_number")
    }'''
data = data.replace(old3, new3)
print('Fix3a (qty_map added):', 'qty_map' in data)

# Then use qty_map when creating custom part profiles in Step 2
old3b = '''                if pn not in profiles:
                    profiles[pn] = DimensionProfile(
                        part_number=pn,
                        description=desc,
                        gender=gender,
                        threads=threads,
                        hole_patterns=hole_patterns,
                        bore_shaft_fits=bore_shaft_fits,
                        linear_dims=sorted(set(linear_dims)),
                        countersinks=countersinks,
                        counterbores=counterbores,
                        washers=washers,
                    )'''
new3b = '''                if pn not in profiles:
                    profiles[pn] = DimensionProfile(
                        part_number=pn,
                        description=desc,
                        gender=gender,
                        threads=threads,
                        hole_patterns=hole_patterns,
                        bore_shaft_fits=bore_shaft_fits,
                        linear_dims=sorted(set(linear_dims)),
                        countersinks=countersinks,
                        counterbores=counterbores,
                        washers=washers,
                        bom_qty=qty_map.get(pn, 1),
                    )'''
data = data.replace(old3b, new3b)
print('Fix3b (Step2 bom_qty):', 'qty_map.get(pn, 1)' in data)

open('services/fitment_checker.py', 'w', encoding='utf-8').write(data)
print('All fixes written.')
