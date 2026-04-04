# replacements for for certain stdlib functions that aren't implemented in micropython

def isnumeric(s: str) -> bool:
    if not s:
        return False
    for c in s:
        if c not in "0123456789":
            return False
    return True

def translate(s: str, table: dict[str, str]) -> str:
    result = ""
    for c in s:
        result += table.get(c, c)
    return result

def sign(val: float) -> int:
        return 1 if val > 0 else -1 if val < 0 else 0