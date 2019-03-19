#!/usr/bin/env python3
# Copyright 2019 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

import argparse
import re
import subprocess
from typing import List

from common import die


def main() -> None:
  args = create_parser().parse_args()
  run_isort(fix=args.fix)


def create_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description="Run isort over build-support to ensure valid import order.")
  parser.add_argument(
    "-f", "--fix",
    action="store_true",
    help="Instead of erroring on bad import sort orders, fix those files."
  )
  return parser


def run_isort(*, fix: bool) -> None:
  command = ["./pants", "--changed-parent=gh-pages", "fmt.isort"]
  if fix:
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
    return
  command.extend(["--", "--check-only"])
  result = subprocess.run(command, encoding="utf-8", stdout=subprocess.PIPE)
  stdout = result.stdout.strip()
  try:
    result.check_returncode()
  except subprocess.CalledProcessError:
    failing_targets = '\n'.join(parse_failing_targets(stdout))
    die("The following files have incorrect import orders. Fix by running "
        f"`./build-support/isort.py -f`.\n\n{failing_targets}")


def parse_failing_targets(stdout: str) -> List[str]:
  error_lines = (line for line in stdout.split("\n") if "ERROR" in line)
  prefix = r"(?<=setup/)"
  postfix = r'(?=\sImports)'
  parsed_files = (re.search(f"{prefix}.*{postfix}", line)[0] for line in error_lines)
  return sorted(parsed_files)


if __name__ == "__main__":
  main()
