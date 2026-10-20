"""Constrained-random stimulus generator for the dual-core CPU.

Writes three memory images in the byte-addressed, little-endian
"@address / byte" format used by $readmemh:

    inst_1_dram_file.dat  - program for core 1
    inst_2_dram_file.dat  - program for core 2
    data_dram_file.dat    - initial data memory, starting at 0x1000

Constraints applied:
  * Exclusive store: at the same instruction count, at most one core
    issues a STORE.
  * Load/store immediates stay small so addresses remain inside the
    initialized data region.
  * ADDI/SUBI immediates are kept non-negative to avoid overflow.
  * BEQ and JUMP are excluded, so programs run straight through
    without infinite loops or out-of-range targets.
"""
import random

NUM_INSTRUCTIONS = 50   # instructions per core
DATA_MEM_START = 0x1000  # base address of the data DRAM
DATA_MEM_WORDS = 256     # number of 16-bit words to initialize

OP_R_TYPE = 0
OP_MULT = 1
OP_ADDI = 2
OP_SUBI = 3
OP_LOAD = 4
OP_STORE = 5


def generate_instruction(allow_store=True):
    """Return (16-bit instruction, is_store)."""
    allowed_ops = [OP_R_TYPE, OP_MULT, OP_ADDI, OP_SUBI, OP_LOAD]
    if allow_store:
        allowed_ops.append(OP_STORE)

    op = random.choice(allowed_ops)
    rs = random.randint(0, 7)
    rt = random.randint(0, 7)
    rd = random.randint(0, 7)
    is_store = False

    if op == OP_R_TYPE:
        func = random.randint(0, 7)
        # 000 | rs | rt | rd | func | 0
        inst = (OP_R_TYPE << 13) | (rs << 10) | (rt << 7) | (rd << 4) | (func << 1)
    elif op == OP_MULT:
        rl = random.randint(0, 7)
        # 001 | rs | rt | rd | rl | 0
        inst = (OP_MULT << 13) | (rs << 10) | (rt << 7) | (rd << 4) | (rl << 1)
    elif op in (OP_ADDI, OP_SUBI):
        imm = random.randint(0, 63)
        inst = (op << 13) | (rs << 10) | (rt << 7) | (imm & 0x7F)
    elif op == OP_LOAD:
        imm = random.randint(0, 15)
        inst = (OP_LOAD << 13) | (rs << 10) | (rt << 7) | (imm & 0x7F)
    else:  # OP_STORE
        imm = random.randint(0, 15)
        inst = (OP_STORE << 13) | (rs << 10) | (rt << 7) | (imm & 0x7F)
        is_store = True

    return inst, is_store


def format_hex(value, width=4):
    return hex(value)[2:].zfill(width)


def write_image(path, words, base_addr):
    """Write 16-bit words as little-endian bytes, one address line per byte."""
    with open(path, "w") as f:
        addr = base_addr
        for word in words:
            hex_str = format_hex(word, 4)
            f.write(f"@{format_hex(addr, 5)}\n{hex_str[2:4]}\n")      # low byte
            f.write(f"@{format_hex(addr + 1, 5)}\n{hex_str[0:2]}\n")  # high byte
            addr += 2


def main():
    inst1, inst2 = [], []
    for _ in range(NUM_INSTRUCTIONS):
        # Randomly pick which core draws first, then forbid the other
        # core from storing if the first one did.
        if random.choice([True, False]):
            i1, s1 = generate_instruction(allow_store=True)
            i2, _ = generate_instruction(allow_store=not s1)
        else:
            i2, s2 = generate_instruction(allow_store=True)
            i1, _ = generate_instruction(allow_store=not s2)
        inst1.append(i1)
        inst2.append(i2)

    write_image("inst_1_dram_file.dat", inst1, 0)
    write_image("inst_2_dram_file.dat", inst2, 0)
    data = [random.randint(0, 0xFFFF) for _ in range(DATA_MEM_WORDS)]
    write_image("data_dram_file.dat", data, DATA_MEM_START)
    print("Generated inst_1_dram_file.dat, inst_2_dram_file.dat, data_dram_file.dat")


if __name__ == "__main__":
    main()
