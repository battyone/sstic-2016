#!/usr/bin/env python3
"""Interpret the instructions associated with the question mark character

documentation: https://developer.apple.com/fonts/TrueType-Reference-Manual/RM05/Chap5.html
"""
import base64
import binascii
import re
import hashlib

store_values = [None] * 22
B64SYM = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/'


def analyze_expr(expr, expected_value):
    """Analyze an expression to guess a value"""
    m = re.match(r'S\[([0-9]+)\]$', expr)
    if m is not None:
        pos = int(m.group(1))
        assert store_values[pos] is None
        symbol = B64SYM[expected_value]
        store_values[pos] = symbol
        print('... found S[{}] = {} : "{}"'.format(pos, expected_value, symbol))
        return

    m = re.match(r'(.*) == ([0-9]+)$', expr)
    if m is not None:
        assert expected_value is True
        return analyze_expr(m.group(1), int(m.group(2)))

    m = re.match(r'\((.*)\)$', expr)
    if m is not None:
        return analyze_expr(m.group(1), expected_value)

    m = re.match(r'(.*) \+ ([0-9]+)$', expr)
    if m is not None:
        return analyze_expr(m.group(1), expected_value - int(m.group(2)))

    m = re.match(r'(.*) - ([0-9]+)$', expr)
    if m is not None:
        return analyze_expr(m.group(1), expected_value + int(m.group(2)))

    m = re.match(r'(.*) \* ([0-9]+)$', expr)
    if m is not None:
        x = int(m.group(2))
        assert x > 0 and expected_value % x == 0
        return analyze_expr(m.group(1), expected_value // x)

    print([expr, expected_value])

stack = []
with open('questionmark_instructions.txt', 'r') as f:
    push_length = 0
    for line in f:
        line = line.rstrip()
        if push_length != 0:
            m = re.match(r' ([0-9]+)$', line)
            assert m, repr(line)
            stack.append(str(int(m.group(1))))
            push_length -= 1
            continue

        m = re.match(r'PUSH[BW]_([0-9]+)$', line)
        if m is not None:
            push_length = int(m.group(1))
            assert push_length > 0, repr(line)
            continue

        if line == 'RS':
            stack.append('S[{}]'.format(stack.pop()))
            continue

        if line == 'WS':
            val = stack.pop()
            pos = stack.pop()
            print('S[{}] <- {}'.format(pos, val))
            assert pos == '99'
            assert val.startswith('((') and val.endswith(') && S[99])')
            analyze_expr(val[2:-len(') && S[99])')], True)
            continue

        if line == 'SWAP':
            a = stack.pop()
            b = stack.pop()
            stack += [a, b]
            continue

        if line == 'ROLL':
            a = stack.pop()
            b = stack.pop()
            c = stack.pop()
            stack += [b, a, c]
            continue

        if line == 'MINDEX':
            a = stack.pop()
            assert re.match(r'[0-9]+$', a), a
            a = int(a)
            assert 0 < a <= len(stack)
            x = stack[-a]
            stack = stack[:-a] + stack[-a + 1:]
            stack.append(x)
            continue

        BINOPS = {
            'ADD': '+',
            'AND': '&&',
            'EQ': '==',
            'SUB': '-',
        }

        if line in BINOPS:
            a = stack.pop()
            b = stack.pop()
            stack.append('({} {} {})'.format(b, BINOPS[line], a))
            continue

        if line == 'MUL':
            # multiplication result is divided by 64
            a = stack.pop()
            b = stack.pop()
            assert re.match(r'[0-9]+$', a), a
            a = int(a)
            assert a % 64 == 0
            stack.append('({} * {})'.format(b, a // 64))
            continue

        if line == 'IF':
            assert stack == ['S[99]']
            break

assert push_length == 0

# Convert values to base64
b64 = ''.join(store_values)
print(b64)
code = binascii.hexlify(base64.b64decode(b64 + '==')).decode('ascii')
with open('pass.code', 'w') as f:
    f.write(code)
