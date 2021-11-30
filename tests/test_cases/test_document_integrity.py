# -*- coding: utf-8 -*-

# -*- mode: python -*-
#
# elf_diff
#
# Copyright (C) 2021  Noseglasses (shinynoseglasses@gmail.com)
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#

from elf_diff_test.test_in_subdirs import TestCaseWithSubdirs
from elf_diff_test.elf_diff_execution import ElfDiffExecutionMixin
from elf_diff_test.test_binaries import TESTING_DIR

from deepdiff import DeepDiff  # type: ignore # Make mypy ignore this module
from pprint import pformat
import json
import os
from typing import Dict
from bs4 import BeautifulSoup  # type: ignore # Make mypy ignore this module


def traverse(soup):
    dom_dictionary = {}

    if soup.name is not None:
        dom_dictionary["name"] = soup.name
    else:
        dom_dictionary["value"] = soup.string

    if hasattr(soup, "attrs"):
        dom_dictionary["attrs"] = soup.attrs
    if hasattr(soup, "children"):
        dom_dictionary["children"] = [
            traverse(child) for child in soup.children
        ]  # if child.name is not None]

    return dom_dictionary


def htmlDictFromFile(filename: str) -> Dict:
    with open(filename, "r") as f:
        # soup = BeautifulSoup(f, 'html.parser')
        soup = BeautifulSoup(f, "html5lib")
        # print(soup)
        # print(soup.__dict__)
        return traverse(soup)


class TestDocumentIntegrity(ElfDiffExecutionMixin, TestCaseWithSubdirs):
    def test_document_simple_json(self):
        output_file = "output.json"
        self.runSimpleTest([("json_file", output_file)])

        # The output file is generated in the current directory
        if not os.path.exists(output_file):
            raise Exception(f"Missing output file '{output_file}'")
        test_tree: Dict
        with open(output_file, "r") as f:
            test_tree = json.load(f)

        reference_document: str = os.path.join(
            TESTING_DIR, "x86_64", "reference_document.json"
        )
        if not os.path.exists(reference_document):
            raise Exception(f"Missing reference document file '{reference_document}'")
        reference_tree: Dict
        with open(reference_document, "r") as f:
            reference_tree = json.load(f)

        exclude_paths = [
            "root['document']['files']['input']['new']['binary_path']",
            "root['document']['files']['input']['old']['binary_path']",
            "root['document']['general']['elf_diff_repo_root']",
            "root['document']['general']['elf_diff_version']",
            "root['document']['general']['generation_date']",
        ]
        diff = DeepDiff(reference_tree, test_tree, exclude_paths=exclude_paths)

        if len(diff) > 0:
            diff_str: str = pformat(diff, indent=2)
            raise Exception("documents differ:\n%s" % diff_str)

    def test_document_simple_html(self):
        output_file = "output.html"
        self.runSimpleTestBase(
            args=[("html_file", output_file)], output_file=output_file
        )

        # The output file is generated in the current directory
        if not os.path.exists(output_file):
            raise Exception(f"Missing output file '{output_file}'")
        test_tree: Dict = htmlDictFromFile(output_file)

        reference_document: str = os.path.join(
            TESTING_DIR, "x86_64", "reference_document.html"
        )
        if not os.path.exists(reference_document):
            raise Exception(f"Missing reference document file '{reference_document}'")
        reference_tree: Dict = htmlDictFromFile(reference_document)

        exclude_paths = [
            "root['children'][1]['children'][2]['children'][3]['children'][1]['children'][1]['children'][3]['children'][0]['value']"
        ]
        diff = DeepDiff(reference_tree, test_tree, exclude_paths=exclude_paths)

        if len(diff) > 0:
            diff_str: str = pformat(diff, indent=2)
            raise Exception("documents differ:\n%s" % diff_str)