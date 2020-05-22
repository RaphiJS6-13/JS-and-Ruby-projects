from re import search as re_test
from re import match, sub
from decimal import Decimal

class ParseError(SyntaxError):
  pass

def tokenize(code: str):
  code = code + " "
  output: [{str: str}] = []
  token: {str: str} = {}
  nested: int = 0
  column: int = 1
  for i in range(0, len(code)):
    c = code[i]
    if c == '(':
      if token != {}:
        output.append(token)
      nested += 1
      output.append({'column': column, 'type': 'group', 'value': '('})
      token = {}
    elif c == ')':
      if token != {}:
        output.append(token)
      if nested == 0:
        raise ParseError(f"column {column}: unexpected token ')'")
      output.append({'column': column, 'type': 'group', 'value': ')'})
      nested -= 1
      token = {}
    elif re_test(r'[\d\.]', c) or (c in '+-' and re_test(r'\d', code[i+1])):
      if token != {}:
        token['value'] += c
      else:
        token = {'column': column, 'type': 'num', 'value': c}
    elif re_test(r'\s', c):
      if token != {}:
        output.append(token)
      token = {}
    elif c in '+-*/':
      if token != {}:
        output.append(token)
      output.append({'column': column, 'type': 'op', 'value': c})
      token = {}
    else:
      raise ParseError(f"column {column}: unexpected token '{c}'")
    column += 1

  if nested != 0:
    raise ParseError(f"column {len(code)}: unmatched '('")
  return output

class Op:
  def __init__(self, kind: str, column: int):
    self.__kind = kind
    self.__col = column
    self.right  = None
    self.left = None
  @property
  def kind(self) -> str:
    return self.__kind
  @property
  def column(self) -> int:
    return self.__col
  def __str__(self):
    l = self.left
    r = self.right
    if isinstance(l, dict):
      l = l['value']
    if isinstance(r, dict):
      r = r['value']
    return f"({self.__kind} {l} {r})"
  
def AST(tokens) -> list:
  while True:
    end_paren: int = None
    for i in range(0, len(tokens)):
      if isinstance(tokens[i],dict) and tokens[i]['value'] == ')':
        end_paren = i
        break
    if end_paren == None:
      break
    start_paren = end_paren
    while True:
      now = tokens[start_paren]
      if (not isinstance(now, Op))\
      and now['value'] == '(':
        break
      start_paren -= 1
    prologue = tokens[0:start_paren]
    epilogue = tokens[end_paren+1:]
    section = tokens[start_paren+1: end_paren]
    if len(section) != 1:
      section = AST(section)
    
    tokens = prologue + section + epilogue

  if len(tokens) == 1:
    return tokens
  elif len(tokens) == 2:
    if isinstance(tokens[0], dict) and tokens[0]['type'] == 'op':
      raise ParseError(f"column {tokens[0]['column']}: unexpected token '{tokens[0]['value']}'")
    else:
      raise ParseError(f"column {tokens[1]['column']}: unexpected token '{tokens[1]['value']}'")
  elif len(tokens) == 3:
    ret = Op(tokens[1]['value'],\
      tokens[1]['column'])
    if not isinstance(tokens[0], Op):
      tokens[0]['value'] = \
        Decimal(tokens[0]['value'])
    if not isinstance(tokens[2], Op):
      tokens[2]['value'] =\
        Decimal(tokens[2]['value'])
    ret.left = tokens[0]
    ret.right = tokens[2]
    return [ret]
  else:
    for x in (tokens[0], tokens[2]):
      if not (isinstance(x, Op) or x['type'] == 'num'):
        raise ParseError(f"column {x.column}: unexpected token '{x.value}'")
    for x in (tokens[1], tokens[3]):
      if isinstance(x, Op) or x['type'] == 'num':
        raise ParseError(f"column {x.column}: unexpected token '{x.value}'")
  
    if '*/+-'.index(tokens[1]['value']) < '*/+-'.index(tokens[3]['value']):
      first = AST(tokens[0:3])
      return AST(first + tokens[3:])
    else:
      middle = AST(tokens[2:5])
      return AST(tokens[0:2] + middle + tokens[5:])
def evaluate(code):
  if isinstance(code, dict):
    return code['value']
  if isinstance(code.left, Op):
    code.left = evaluate(code.left)
  if isinstance(code.right, Op):
    code.right = evaluate(code.right)
  if isinstance(code.left, dict):
    code.left = code.left['value']
  if isinstance(code.right, dict):
    code.right = code.right['value']
  if code.kind == '+':
    return code.left + code.right
  elif code.kind == '-':
    return code.left - code.right
  elif code.kind == '*':
    return code.left * code.right
  else:
    return code.left / code.right

while True:
  try:
    text = input()
    if text.strip() == '':
      continue
    print(evaluate(AST(tokenize(text))[0]))
  except EOFError: pass
  except ParseError as e:
    msg = sub(r"column \d+: ", "", str(e))
    print(f"error: {msg}")
    col = int(match(r'column (\d+)', str(e)).group(1))
    part = (len(str(e)) - 2) - str(e).index("'")
    print(text)
    print((" " * (col-1)) + ('~' * part))
