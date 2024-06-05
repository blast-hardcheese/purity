#!/usr/bin/env python

import sys
import distutils.spawn


import tree_sitter_bash as tsbash
from tree_sitter import Language, Parser

BASH_LANGUAGE = Language(tsbash.language())

builtins = set(x.strip() for x in '''
  !
  %
  .
  :
  @
  [
  alias
  alloc
  bg
  bind
  builtin
  bindkey
  break
  breaksw
  builtins
  case
  cd
  chdir
  command
  complete
  continue
  default
  dirs
  do
  done
  echo
  echotc
  elif
  else
  end
  endif
  endsw
  esac
  eval
  exec
  exit
  export
  false
  fc
  fg
  fi
  filetest
  for
  foreach
  getopts
  glob
  goto
  hash
  hashstat
  history
  hup
  if
  jobid
  jobs
  kill
  limit
  local
  log
  login
  logout
  ls-F
  nice
  nohup
  notify
  onintr
  popd
  printenv
  printf
  pushd
  pwd
  read
  readonly
  rehash
  repeat
  return
  sched
  set
  setenv
  settc
  setty
  setvar
  shift
  source
  stop
  suspend
  switch
  telltc
  test
  then
  time
  times
  trap
  true
  type
  ulimit
  umask
  unalias
  uncomplete
  unhash
  unlimit
  unset
  unsetenv
  until
  wait
  where
  which
  while
  {
  }
'''.split())


def main(file):
  parser = Parser(BASH_LANGUAGE)
  src = open(file).read().encode('utf-8')
  tree = parser.parse(src, encoding="utf8")
  # print(str(tree.root_node))
  funcs = BASH_LANGUAGE.query('(function_definition name: (word) @name)')
  our_funcs = set()
  for node, _name in funcs.captures(tree.root_node):
    (start, end) = node.byte_range
    token = src[start:end].decode('utf-8')
    if token not in our_funcs:
      our_funcs.add(token)

  query = BASH_LANGUAGE.query('(command_name (word) @name)')
  seen = set()
  for node, _name in query.captures(tree.root_node):
    (start, end) = node.byte_range
    token = src[start:end].decode('utf-8')
    if token not in seen:
      seen.add(token)
      path = distutils.spawn.find_executable(token)
      if token not in our_funcs:
        if not path and token not in builtins:
          print(token)


if __name__ == '__main__':
  main(*sys.argv[1:])
