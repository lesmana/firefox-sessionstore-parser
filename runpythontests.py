#! /usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'testhelpers'))

import unittestchooser

import pytests

if __name__ == '__main__': # pragma: no cover
  unittestchooser.main()
