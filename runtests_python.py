#! /usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'helpers'))

import unittestchooser

import tests

if __name__ == '__main__': # pragma: no cover
  unittestchooser.main()
