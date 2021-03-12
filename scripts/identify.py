#!/usr/bin/env python3
import errno
import os.path
import re
import shlex
import stat
import string
import sys
from typing import IO
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple


EXTENSIONS = {
    'adoc': {'text', 'asciidoc'},
    'asciidoc': {'text', 'asciidoc'},
    'apinotes': {'text', 'apinotes'},
    'asar': {'binary', 'asar'},
    'avif': {'binary', 'image', 'avif'},
    'bash': {'text', 'shell', 'bash'},
    'bat': {'text', 'batch'},
    'bib': {'text', 'bib'},
    'bmp': {'binary', 'image', 'bitmap'},
    'bz2': {'binary', 'bzip2'},
    'c': {'text', 'c'},
    'cc': {'text', 'c++'},
    'cfg': {'text'},
    'chs': {'text', 'c2hs'},
    'clj': {'text', 'clojure'},
    'cljc': {'text', 'clojure'},
    'cljs': {'text', 'clojure', 'clojurescript'},
    'cmake': {'text', 'cmake'},
    'cnf': {'text'},
    'coffee': {'text', 'coffee'},
    'conf': {'text'},
    'cpp': {'text', 'c++'},
    'crt': {'text', 'pem'},
    'cs': {'text', 'c#'},
    'csproj': {'text', 'xml', 'csproj'},
    'csh': {'text', 'shell', 'csh'},
    'cson': {'text', 'cson'},
    'css': {'text', 'css'},
    'csv': {'text', 'csv'},
    'cu': {'text', 'cuda'},
    'cxx': {'text', 'c++'},
    'dart': {'text', 'dart'},
    'def': {'text', 'def'},
    'dtd': {'text', 'dtd'},
    'ear': {'binary', 'zip', 'jar'},
    'edn': {'text', 'clojure', 'edn'},
    'ejs': {'text', 'ejs'},
    'eot': {'binary', 'eot'},
    'eps': {'binary', 'eps'},
    'erb': {'text', 'erb'},
    'exe': {'binary'},
    'eyaml': {'text', 'yaml'},
    'feature': {'text', 'gherkin'},
    'fish': {'text', 'fish'},
    'gd': {'text', 'gdscript'},
    'gemspec': {'text', 'ruby'},
    'gif': {'binary', 'image', 'gif'},
    'go': {'text', 'go'},
    'gotmpl': {'text', 'gotmpl'},
    'gpx': {'text', 'gpx', 'xml'},
    'graphql': {'text', 'graphql'},
    'gradle': {'text', 'groovy'},
    'groovy': {'text', 'groovy'},
    'gyb': {'text', 'gyb'},
    'gyp': {'text', 'gyp', 'python'},
    'gypi': {'text', 'gyp', 'python'},
    'gz': {'binary', 'gzip'},
    'h': {'text', 'header', 'c', 'c++'},
    'hpp': {'text', 'header', 'c++'},
    'hs': {'text', 'haskell'},
    'htm': {'text', 'html'},
    'html': {'text', 'html'},
    'hxx': {'text', 'header', 'c++'},
    'icns': {'binary', 'icns'},
    'ico': {'binary', 'icon'},
    'ics': {'text', 'icalendar'},
    'idl': {'text', 'idl'},
    'idr': {'text', 'idris'},
    'inc': {'text', 'inc'},
    'ini': {'text', 'ini'},
    'inx': {'text', 'xml', 'inx'},
    'ipynb': {'text', 'jupyter'},
    'j2': {'text', 'jinja'},
    'jade': {'text', 'jade'},
    'jar': {'binary', 'zip', 'jar'},
    'java': {'text', 'java'},
    'jenkinsfile': {'text', 'groovy'},
    'jinja': {'text', 'jinja'},
    'jinja2': {'text', 'jinja'},
    'jpeg': {'binary', 'image', 'jpeg'},
    'jpg': {'binary', 'image', 'jpeg'},
    'js': {'text', 'javascript'},
    'json': {'text', 'json'},
    'jsonnet': {'text', 'jsonnet'},
    'jsx': {'text', 'jsx'},
    'key': {'text', 'pem'},
    'kml': {'text', 'kml', 'xml'},
    'kt': {'text', 'kotlin'},
    'lean': {'text', 'lean'},
    'lektorproject': {'text', 'ini', 'lektorproject'},
    'less': {'text', 'less'},
    'lhs': {'text', 'literate-haskell'},
    'libsonnet': {'text', 'jsonnet'},
    'lidr': {'text', 'idris'},
    'lr': {'text', 'lektor'},
    'lua': {'text', 'lua'},
    'm': {'text', 'c', 'objective-c'},
    'manifest': {'text', 'manifest'},
    'map': {'text', 'map'},
    'markdown': {'text', 'markdown'},
    'md': {'text', 'markdown'},
    'mdx': {'text', 'mdx'},
    'mib': {'text', 'mib'},
    'mk': {'text', 'makefile'},
    'ml': {'text', 'ocaml'},
    'mli': {'text', 'ocaml'},
    'mm': {'text', 'c++', 'objective-c++'},
    'modulemap': {'text', 'modulemap'},
    'myst': {'text', 'myst'},
    'ngdoc': {'text', 'ngdoc'},
    'nim': {'text', 'nim'},
    'nims': {'text', 'nim'},
    'nimble': {'text', 'nimble'},
    'nix': {'text', 'nix'},
    'otf': {'binary', 'otf'},
    'p12': {'binary', 'p12'},
    'patch': {'text', 'diff'},
    'pdf': {'binary', 'pdf'},
    'pem': {'text', 'pem'},
    'php': {'text', 'php'},
    'php4': {'text', 'php'},
    'php5': {'text', 'php'},
    'phtml': {'text', 'php'},
    'pl': {'text', 'perl'},
    'plantuml': {'text', 'plantuml'},
    'pm': {'text', 'perl'},
    'png': {'binary', 'image', 'png'},
    'po': {'text', 'pofile'},
    'pp': {'text', 'puppet'},
    'properties': {'text', 'java-properties'},
    'proto': {'text', 'proto'},
    'puml': {'text', 'plantuml'},
    'purs': {'text', 'purescript'},
    'pxd': {'text', 'cython'},
    'pxi': {'text', 'cython'},
    'py': {'text', 'python'},
    'pyi': {'text', 'pyi'},
    'pyproj': {'text', 'xml', 'pyproj'},
    'pyx': {'text', 'cython'},
    'pyz': {'binary', 'pyz'},
    'pyzw': {'binary', 'pyz'},
    'r': {'text', 'r'},
    'rake': {'text', 'ruby'},
    'rb': {'text', 'ruby'},
    'rs': {'text', 'rust'},
    'rst': {'text', 'rst'},
    's': {'text', 'asm'},
    'sass': {'text', 'sass'},
    'sbt': {'text', 'sbt', 'scala'},
    'sc': {'text', 'scala'},
    'scala': {'text', 'scala'},
    'scm': {'text', 'scheme'},
    'scss': {'text', 'scss'},
    'sh': {'text', 'shell'},
    'sln': {'text', 'sln'},
    'sls': {'text', 'salt'},
    'so': {'binary'},
    'sol': {'text', 'solidity'},
    'spec': {'text', 'spec'},
    'sql': {'text', 'sql'},
    'ss': {'text', 'scheme'},
    'styl': {'text', 'stylus'},
    'sv': {'text', 'system-verilog'},
    'svg': {'text', 'image', 'svg', 'xml'},
    'svh': {'text', 'system-verilog'},
    'swf': {'binary', 'swf'},
    'swift': {'text', 'swift'},
    'swiftdeps': {'text', 'swiftdeps'},
    'tac': {'text', 'twisted', 'python'},
    'tar': {'binary', 'tar'},
    'tex': {'text', 'tex'},
    'tf': {'text', 'terraform'},
    'tfvars': {'text', 'terraform'},
    'tgz': {'binary', 'gzip'},
    'thrift': {'text', 'thrift'},
    'tiff': {'binary', 'image', 'tiff'},
    'toml': {'text', 'toml'},
    'ts': {'text', 'ts'},
    'tsx': {'text', 'tsx'},
    'ttf': {'binary', 'ttf'},
    'twig': {'text', 'twig'},
    'txsprofile': {'text', 'ini', 'txsprofile'},
    'txt': {'text', 'plain-text'},
    'v': {'text', 'verilog'},
    'vb': {'text', 'vb'},
    'vbproj': {'text', 'xml', 'vbproj'},
    'vcxproj': {'text', 'xml', 'vcxproj'},
    'vdx': {'text', 'vdx'},
    'vh': {'text', 'verilog'},
    'vhd': {'text', 'vhdl'},
    'vim': {'text', 'vim'},
    'vue': {'text', 'vue'},
    'war': {'binary', 'zip', 'jar'},
    'wav': {'binary', 'audio', 'wav'},
    'webp': {'binary', 'image', 'webp'},
    'whl': {'binary', 'wheel', 'zip'},
    'wkt': {'text', 'wkt'},
    'woff': {'binary', 'woff'},
    'woff2': {'binary', 'woff2'},
    'wsgi': {'text', 'wsgi', 'python'},
    'xhtml': {'text', 'xml', 'html', 'xhtml'},
    'xml': {'text', 'xml'},
    'xq': {'text', 'xquery'},
    'xql': {'text', 'xquery'},
    'xqm': {'text', 'xquery'},
    'xqu': {'text', 'xquery'},
    'xquery': {'text', 'xquery'},
    'xqy': {'text', 'xquery'},
    'xsd': {'text', 'xml', 'xsd'},
    'xsl': {'text', 'xml', 'xsl'},
    'yaml': {'text', 'yaml'},
    'yang': {'text', 'yang'},
    'yin': {'text', 'xml', 'yin'},
    'yml': {'text', 'yaml'},
    'zig': {'text', 'zig'},
    'zip': {'binary', 'zip'},
    'zsh': {'text', 'shell', 'zsh'},
}
EXTENSIONS_NEED_BINARY_CHECK = {
    'plist': {'plist'},
}

NAMES = {
    '.babelrc': EXTENSIONS['json'] | {'babelrc'},
    '.bash_aliases': EXTENSIONS['bash'],
    '.bash_profile': EXTENSIONS['bash'],
    '.bashrc': EXTENSIONS['bash'],
    '.bowerrc': EXTENSIONS['json'] | {'bowerrc'},
    '.browserslistrc': {'text', 'browserslistrc'},
    '.clang-format': EXTENSIONS['yaml'],
    '.clang-tidy': EXTENSIONS['yaml'],
    '.codespellrc': EXTENSIONS['ini'] | {'codespellrc'},
    '.coveragerc': EXTENSIONS['ini'] | {'coveragerc'},
    '.cshrc': EXTENSIONS['csh'],
    '.csslintrc': EXTENSIONS['json'] | {'csslintrc'},
    '.dockerignore': {'text', 'dockerignore'},
    '.editorconfig': {'text', 'editorconfig'},
    '.flake8': EXTENSIONS['ini'] | {'flake8'},
    '.gitattributes': {'text', 'gitattributes'},
    '.gitconfig': EXTENSIONS['ini'] | {'gitconfig'},
    '.gitignore': {'text', 'gitignore'},
    '.gitlint': EXTENSIONS['ini'] | {'gitlint'},
    '.gitmodules': {'text', 'gitmodules'},
    '.hgrc': EXTENSIONS['ini'] | {'hgrc'},
    '.jshintrc': EXTENSIONS['json'] | {'jshintrc'},
    '.mailmap': {'text', 'mailmap'},
    '.mention-bot': EXTENSIONS['json'] | {'mention-bot'},
    '.npmignore': {'text', 'npmignore'},
    '.pdbrc': EXTENSIONS['py'] | {'pdbrc'},
    '.pypirc': EXTENSIONS['ini'] | {'pypirc'},
    '.rstcheck.cfg': EXTENSIONS['ini'],
    '.yamllint': EXTENSIONS['yaml'] | {'yamllint'},
    '.zshrc': EXTENSIONS['zsh'],
    'AUTHORS': EXTENSIONS['txt'],
    'BUILD': {'text', 'bazel'},
    'BUILD.bazel': {'text', 'bazel'},
    'CMakeLists.txt': EXTENSIONS['cmake'],
    'CHANGELOG': EXTENSIONS['txt'],
    'CONTRIBUTING': EXTENSIONS['txt'],
    'COPYING': EXTENSIONS['txt'],
    'Dockerfile': {'text', 'dockerfile'},
    'Gemfile': EXTENSIONS['rb'],
    'Jenkinsfile': {'text', 'groovy'},
    'LICENSE': EXTENSIONS['txt'],
    'MAINTAINERS': EXTENSIONS['txt'],
    'Makefile': EXTENSIONS['mk'],
    'NEWS': EXTENSIONS['txt'],
    'NOTICE': EXTENSIONS['txt'],
    'PATENTS': EXTENSIONS['txt'],
    'Pipfile': EXTENSIONS['toml'],
    'Pipfile.lock': EXTENSIONS['json'],
    'PKGBUILD': {'text', 'bash', 'pkgbuild', 'alpm'},
    'pylintrc': EXTENSIONS['ini'] | {'pylintrc'},
    'README': EXTENSIONS['txt'],
    'Rakefile': EXTENSIONS['rb'],
    'setup.cfg': EXTENSIONS['ini'],
}

INTERPRETERS = {
    'ash': {'shell', 'ash'},
    'awk': {'awk'},
    'bash': {'shell', 'bash'},
    'bats': {'shell', 'bash', 'bats'},
    'csh': {'shell', 'csh'},
    'dash': {'shell', 'dash'},
    'expect': {'expect'},
    'ksh': {'shell', 'ksh'},
    'node': {'javascript'},
    'nodejs': {'javascript'},
    'perl': {'perl'},
    'python': {'python'},
    'python2': {'python', 'python2'},
    'python3': {'python', 'python3'},
    'ruby': {'ruby'},
    'sh': {'shell', 'sh'},
    'tcsh': {'shell', 'tcsh'},
    'zsh': {'shell', 'zsh'},
}


printable = frozenset(string.printable)

DIRECTORY = 'directory'
SYMLINK = 'symlink'
SOCKET = 'socket'
FILE = 'file'
EXECUTABLE = 'executable'
NON_EXECUTABLE = 'non-executable'
TEXT = 'text'
BINARY = 'binary'

TYPE_TAGS = frozenset((DIRECTORY, FILE, SYMLINK, SOCKET))
MODE_TAGS = frozenset((EXECUTABLE, NON_EXECUTABLE))
ENCODING_TAGS = frozenset((BINARY, TEXT))
_ALL_TAGS = {*TYPE_TAGS, *MODE_TAGS, *ENCODING_TAGS}
_ALL_TAGS.update(*EXTENSIONS.values())
_ALL_TAGS.update(*EXTENSIONS_NEED_BINARY_CHECK.values())
_ALL_TAGS.update(*NAMES.values())
_ALL_TAGS.update(*INTERPRETERS.values())
ALL_TAGS = frozenset(_ALL_TAGS)


def tags_from_path(path: str) -> Set[str]:
    try:
        sr = os.lstat(path)
    except (OSError, ValueError):  # same error-handling as `os.lexists()`
        raise ValueError(f'{path} does not exist.')

    mode = sr.st_mode
    if stat.S_ISDIR(mode):
        return {DIRECTORY}
    if stat.S_ISLNK(mode):
        return {SYMLINK}
    if stat.S_ISSOCK(mode):
        return {SOCKET}

    tags = {FILE}

    executable = os.access(path, os.X_OK)
    if executable:
        tags.add(EXECUTABLE)
    else:
        tags.add(NON_EXECUTABLE)

    # As an optimization, if we're able to read tags from the filename, then we
    # don't peek at the file contents.
    t = tags_from_filename(os.path.basename(path))
    if len(t) > 0:
        tags.update(t)
    else:
        if executable:
            shebang = parse_shebang_from_file(path)
            if len(shebang) > 0:
                tags.update(tags_from_interpreter(shebang[0]))

    # some can be both binary and text
    # see NEED_BINARY_CHECK
    if not ENCODING_TAGS & tags:
        if file_is_text(path):
            tags.add(TEXT)
        else:
            tags.add(BINARY)

    assert ENCODING_TAGS & tags, tags
    assert MODE_TAGS & tags, tags
    return tags


def tags_from_filename(path: str) -> Set[str]:
    _, filename = os.path.split(path)
    _, ext = os.path.splitext(filename)

    ret = set()

    # Allow e.g. "Dockerfile.xenial" to match "Dockerfile"
    for part in [filename] + filename.split('.'):
        if part in NAMES:
            ret.update(NAMES[part])
            break

    if len(ext) > 0:
        ext = ext[1:].lower()
        if ext in EXTENSIONS:
            ret.update(EXTENSIONS[ext])
        elif ext in EXTENSIONS_NEED_BINARY_CHECK:
            ret.update(EXTENSIONS_NEED_BINARY_CHECK[ext])

    return ret


def tags_from_interpreter(interpreter: str) -> Set[str]:
    _, _, interpreter = interpreter.rpartition('/')

    # Try "python3.5.2" => "python3.5" => "python3" until one matches.
    while interpreter:
        if interpreter in INTERPRETERS:
            return INTERPRETERS[interpreter]
        else:
            interpreter, _, _ = interpreter.rpartition('.')

    return set()


def is_text(bytesio: IO[bytes]) -> bool:
    """Return whether the first KB of contents seems to be binary.

    This is roughly based on libmagic's binary/text detection:
    https://github.com/file/file/blob/df74b09b9027676088c797528edcaae5a9ce9ad0/src/encoding.c#L203-L228
    """
    text_chars = (
        bytearray([7, 8, 9, 10, 11, 12, 13, 27]) +
        bytearray(range(0x20, 0x7F)) +
        bytearray(range(0x80, 0X100))
    )
    return not bool(bytesio.read(1024).translate(None, text_chars))


def file_is_text(path: str) -> bool:
    if not os.path.lexists(path):
        raise ValueError(f'{path} does not exist.')
    with open(path, 'rb') as f:
        return is_text(f)


def _shebang_split(line: str) -> List[str]:
    try:
        # shebangs aren't supposed to be quoted, though some tools such as
        # setuptools will write them with quotes so we'll best-guess parse
        # with shlex first
        return shlex.split(line)
    except ValueError:
        # failing that, we'll do a more "traditional" shebang parsing which
        # just involves splitting by whitespace
        return line.split()


def _parse_nix_shebang(
        bytesio: IO[bytes],
        cmd: Tuple[str, ...],
) -> Tuple[str, ...]:
    while bytesio.read(2) == b'#!':
        next_line_b = bytesio.readline()
        try:
            next_line = next_line_b.decode('UTF-8')
        except UnicodeDecodeError:
            return cmd

        for c in next_line:
            if c not in printable:
                return cmd

        line_tokens = tuple(_shebang_split(next_line.strip()))
        for i, token in enumerate(line_tokens[:-1]):
            if token != '-i':
                continue
            # the argument to -i flag
            cmd = (line_tokens[i + 1],)
    return cmd


def parse_shebang(bytesio: IO[bytes]) -> Tuple[str, ...]:
    """Parse the shebang from a file opened for reading binary."""
    if bytesio.read(2) != b'#!':
        return ()
    first_line_b = bytesio.readline()
    try:
        first_line = first_line_b.decode('UTF-8')
    except UnicodeDecodeError:
        return ()

    # Require only printable ascii
    for c in first_line:
        if c not in printable:
            return ()

    cmd = tuple(_shebang_split(first_line.strip()))
    if cmd and cmd[0] == '/usr/bin/env':
        cmd = cmd[1:]
        if cmd == ('nix-shell',):
            return _parse_nix_shebang(bytesio, cmd)
    return cmd


def parse_shebang_from_file(path: str) -> Tuple[str, ...]:
    """Parse the shebang given a file path."""
    if not os.path.lexists(path):
        raise ValueError(f'{path} does not exist.')
    if not os.access(path, os.X_OK):
        return ()

    try:
        with open(path, 'rb') as f:
            return parse_shebang(f)
    except OSError as e:
        if e.errno == errno.EINVAL:
            return ()
        else:
            raise

if __name__=='__main__':
    print(tags_from_filename(sys.argv[1]))
