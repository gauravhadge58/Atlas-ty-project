from services.bom_extractor import _part_number_plausible

# Check if "14" is considered plausible
print(f"_part_number_plausible('14')? {_part_number_plausible('14')}")
print(f"_part_number_plausible('1')? {_part_number_plausible('1')}")
print(f"_part_number_plausible('ABC')? {_part_number_plausible('ABC')}")
