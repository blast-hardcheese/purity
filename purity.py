#!/usr/bin/env python

import os
import sys

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

def find_executable(executable, path=None):
    """Tries to find 'executable' in the directories listed in 'path'.

    A string listing directories separated by 'os.pathsep'; defaults to
    os.environ['PATH'].  Returns the complete filename or None if not found.
    """
    _, ext = os.path.splitext(executable)
    if (sys.platform == 'win32') and (ext != '.exe'):
        executable = executable + '.exe'

    if os.path.isfile(executable):
        return executable

    if path is None:
        path = os.environ.get('PATH', None)
        if path is None:
            try:
                path = os.confstr("CS_PATH")
            except (AttributeError, ValueError):
                # os.confstr() or CS_PATH is not available
                path = os.defpath
        # bpo-35755: Don't use os.defpath if the PATH environment variable is
        # set to an empty string

    # PATH='' doesn't match, whereas PATH=':' looks in the current directory
    if not path:
        return None

    paths = path.split(os.pathsep)
    for p in paths:
        f = os.path.join(p, executable)
        if os.path.isfile(f):
            # the file exists, we have a shot at spawn working
            return f
    return None

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
      path = find_executable(token)
      if token not in our_funcs:
        if not path and token not in builtins:
          print(token)


if __name__ == '__main__':
  main(*sys.argv[1:])
