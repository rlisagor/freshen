from freshen.test.pyunit import PyunitTestCase
from django.test import TransactionTestCase

DjangoNoseTestCase = make_pyunit_testcase_class(TransactionTestCase)
