"""
Tradutor simples de TAC (Three Address Code) para assembly x86_64 (MS x64 ABI).
Gera um .s com variáveis/temporários na seção .data e código em .text.
Compatível com gcc/clang (MinGW) na ABI Microsoft x64.
"""

import re
from pathlib import Path
from typing import Iterable, List, Tuple, Set

BIN_OPS = {"+": "add", "-": "sub", "*": "imul", "/": "idiv",
           "==": "seteq", "!=": "setne", "<": "setl", ">": "setg",
           "<=": "setle", ">=": "setge"}


def parse_tac_lines(lines: Iterable[str]) -> List[str]:
    return [ln.strip() for ln in lines if ln.strip()]


def is_string_literal(token: str) -> bool:
    return len(token) >= 2 and token.startswith("\"") and token.endswith("\"")


def canonical_string_literal(token: str) -> str:
    """Normaliza literais: remove aspas duplas duplicadas externas."""
    if not is_string_literal(token):
        return token
    inner = token[1:-1]
    # colapsa aspas extras externas (ex: ""txt"" -> "txt")
    while inner.startswith('"') and inner.endswith('"'):
        inner = inner[1:-1]
    return f'"{inner}"'


def collect_symbols(tac: List[str]) -> Tuple[Set[str], Set[str]]:
    vars_set, temps_set = set(), set()
    token_re = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    for ln in tac:
        if ln.endswith(":"):
            continue
        # lhs = ...
        if "=" in ln and not ln.startswith("if_not") and not ln.startswith("goto"):
            lhs = ln.split("=", 1)[0].strip()
            if lhs.startswith("t"):
                temps_set.add(lhs)
            else:
                vars_set.add(lhs)
        # rhs identifiers
        for tok in token_re.findall(ln):
            if tok in {"if_not", "goto", "output", "input"}:
                continue
            if tok.startswith("L"):
                continue
            if is_string_literal(tok):
                continue
            if tok.startswith("t"):
                temps_set.add(tok)
            elif tok.isidentifier() and not tok.isnumeric():
                vars_set.add(tok)
    return vars_set, temps_set


def is_int_literal(token: str) -> bool:
    return re.fullmatch(r"-?\d+", token) is not None


def emit_prologue() -> List[str]:
    # Microsoft x64 ABI (usada por MinGW/Windows):
    # - Args: rcx, rdx, r8, r9
    # - Shadow space: 32 bytes reservado pelo caller
    # - Stack alinhado a 16 bytes em cada call
    return [
        ".intel_syntax noprefix",
        ".global main",
        ".extern printf",
        ".extern scanf",
        "",
    ]


def emit_data(vars_set: Set[str], temps_set: Set[str], str_labels: dict[str, str]) -> List[str]:
    out = [
        ".section .data",
        "fmt_in: .string \"%ld\"",
        "fmt_out: .string \"%ld\\n\"",
        "fmt_str: .string \"%s\\n\"",
    ]
    for name in sorted(vars_set | temps_set):
        out.append(f"{name}: .quad 0")
    for literal, label in str_labels.items():
        # strip outer quotes and escape inner quotes/backslashes
        body = literal[1:-1].replace("\\", "\\\\").replace("\"", "\\\"")
        out.append(f"{label}: .string \"{body}\"")
    out.append("")
    return out


def emit_text_prologue() -> List[str]:
    # Alinha a stack a 16 bytes considerando ret addr (8) + push rbp (8)
    # Subtrai 32 bytes (shadow space) já no callee para chamadas a printf/scanf
    return [
        ".section .text",
        "main:",
        "    push rbp",
        "    mov rbp, rsp",
        "    sub rsp, 32    # shadow space (Windows x64)",
        "",
    ]


def load_operand(op: str, target: str = "rax") -> List[str]:
    if is_int_literal(op):
        return [f"    mov {target}, {op}"]
    # RIP-relative addressing for x64
    return [
        f"    lea rbx, [rip+{op}]",
        f"    mov {target}, [rbx]",
    ]


def store_dest(dest: str, src: str = "rax") -> List[str]:
    return [
        f"    lea rbx, [rip+{dest}]",
        f"    mov [rbx], {src}",
    ]


def emit_binary(dest: str, a: str, op: str, b: str) -> List[str]:
    lines: List[str] = []
    lines += load_operand(a, "rax")
    if op == "/":
        # idiv usa rdx:rax
        lines.append("    cqo")
        lines += load_operand(b, "rbx")
        lines.append("    idiv rbx")
        lines += store_dest(dest, "rax")
        return lines
    if op in {"==", "!=", "<", ">", "<=", ">="}:
        lines += load_operand(b, "rbx")
        lines.append("    cmp rax, rbx")
        set_map = {
            "==": "sete", "!=": "setne", "<": "setl", ">": "setg",
            "<=": "setle", ">=": "setge",
        }
        lines.append(f"    {set_map[op]} al")
        lines.append("    movzx rax, al")
        lines += store_dest(dest, "rax")
        return lines
    # aritméticos simples
    lines += load_operand(b, "rbx")
    op_map = {"+": "add", "-": "sub", "*": "imul"}
    asm_op = op_map.get(op)
    if asm_op:
        lines.append(f"    {asm_op} rax, rbx")
    lines += store_dest(dest, "rax")
    return lines


def emit_if_not(cond: str, label: str) -> List[str]:
    return load_operand(cond, "rax") + ["    cmp rax, 0", f"    je {label}"]


def emit_goto(label: str) -> List[str]:
    return [f"    jmp {label}"]


def emit_output(op: str, str_labels: dict[str, str]) -> List[str]:
    # MS x64: rcx, rdx, r8, r9
    if is_string_literal(op):
        key = canonical_string_literal(op)
        label = str_labels[key]
        return [
            f"    lea rdx, [rip+{label}]",
            "    lea rcx, [rip+fmt_str]",
            "    xor eax, eax   # printf variadic: clear al",
            "    call printf",
        ]
    lines = load_operand(op, "rdx")
    lines.append("    lea rcx, [rip+fmt_out]")
    lines.append("    xor eax, eax   # printf variadic: clear al")
    lines.append("    call printf")
    return lines


def emit_input(dest: str) -> List[str]:
    # scanf(fmt_in, &dest) -> rcx=fmt, rdx=&dest
    return [
        f"    lea rdx, [rip+{dest}]",
        "    lea rcx, [rip+fmt_in]",
        "    xor eax, eax",
        "    call scanf",
    ]


def translate_tac(tac: List[str]) -> List[str]:
    lines: List[str] = []
    vars_set, temps_set = collect_symbols(tac)
    # coleta literais de string
    str_literals: List[str] = []
    # Captura literais de string, tolerando aspas duplicadas
    str_re = re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"')
    for ln in tac:
        str_literals.extend(canonical_string_literal(m) for m in str_re.findall(ln))
        # garante captura em output(...) mesmo que regex falhe em casos estranhos
        if ln.startswith("output") and "(" in ln and ")" in ln:
            inside = ln[ln.find("(") + 1: ln.rfind(")")].strip()
            if is_string_literal(inside):
                str_literals.append(canonical_string_literal(inside))
    str_labels = {lit: f"str_{i}" for i, lit in enumerate(dict.fromkeys(str_literals))}

    lines += emit_prologue()
    lines += emit_data(vars_set, temps_set, str_labels)
    lines += emit_text_prologue()

    for ln in tac:
        if not ln:
            continue
        if ln.endswith(":"):
            lines.append(ln)  # label
            continue
        if ln.startswith("goto"):
            _, label = ln.split()
            lines += emit_goto(label)
            continue
        if ln.startswith("if_not"):
            parts = ln.split()
            cond = parts[1]
            label = parts[-1]
            lines += emit_if_not(cond, label)
            continue
        if ln.startswith("output"):
            inside = ln[ln.find("(") + 1: ln.rfind(")")]
            lines += emit_output(inside.strip(), str_labels)
            continue
        if "input()" in ln:
            dest = ln.split("=")[0].strip()
            lines += emit_input(dest)
            continue
        # assignment forms
        if "=" in ln:
            lhs, rhs = ln.split("=", 1)
            lhs = lhs.strip()
            rhs = rhs.strip()
            # binary op?
            m = re.match(r"(.+) ([+\-*/]|==|!=|<=|>=|<|>) (.+)", rhs)
            if m:
                a, op, b = m.groups()
                lines += emit_binary(lhs, a.strip(), op.strip(), b.strip())
            else:
                # simple move
                if is_int_literal(rhs):
                    lines.append(f"    mov rax, {rhs}")
                else:
                    lines += load_operand(rhs, "rax")
                lines += store_dest(lhs, "rax")
            continue
    # epílogo
    lines += ["", "    mov rsp, rbp", "    pop rbp", "    mov eax, 0", "    ret"]
    return lines


def tac_file_to_asm(tac_path: Path, asm_path: Path) -> None:
    tac_lines = parse_tac_lines(tac_path.read_text(encoding="utf-8").splitlines())
    asm_lines = translate_tac(tac_lines)
    asm_path.write_text("\n".join(asm_lines) + "\n", encoding="utf-8")

# API pública para uso pelo projeto
def generate_asm_from_tac(tac_lines: List[str], asm_path: Path | str = "out.s") -> Path:
    """Gera assembly a partir de uma lista de linhas TAC e grava em asm_path."""
    asm_path = Path(asm_path)
    asm_lines = translate_tac(tac_lines)
    asm_path.write_text("\n".join(asm_lines) + "\n", encoding="utf-8")
    return asm_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Traduz TAC para assembly x86_64 (MS x64 ABI)")
    parser.add_argument("tac", type=Path, help="Arquivo TAC de entrada")
    parser.add_argument("asm", type=Path, nargs="?", help="Arquivo .s de saída", default=Path("out.s"))
    args = parser.parse_args()
    tac_file_to_asm(args.tac, args.asm)
