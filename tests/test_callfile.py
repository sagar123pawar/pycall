"""Unit tests for `pycall.callfile`."""

from time import mktime
from getpass import getuser
from datetime import datetime
from unittest import TestCase

from path import Path

from pycall import Application, Call, CallFile, InvalidTimeError, \
    NoSpoolPermissionError, NoUserError, NoUserPermissionError, \
    ValidationError


class TestCallFile(TestCase):
    """Run tests on the `CallFile` class."""

    def setUp(self):
        """Setup some default variables for test usage."""
        self.call = Call('channel')
        self.action = Application('application', 'data')
        self.spool_dir = '/tmp'

    def test_attrs_stick(self):
        """Ensure attributes stick."""
        c = CallFile('call', 'action', 'archive', 'filename', 'tempdir',
                'user', 'spool_dir')
        self.assertEqual(c.call, 'call')
        self.assertEqual(c.action, 'action')
        self.assertEqual(c.archive, 'archive')
        self.assertEqual(c.filename, 'filename')
        self.assertEqual(c.tempdir, 'tempdir')
        self.assertEqual(c.user, 'user')
        self.assertEqual(c.spool_dir, 'spool_dir')

    def test_attrs_default_spool_dir(self):
        """Ensure default `spool_dir` attribute works."""
        c = CallFile(self.call, self.action)
        self.assertEqual(c.spool_dir, CallFile.DEFAULT_SPOOL_DIR)

    def test_attrs_default_filename(self):
        """Ensure default `filename` attribute works."""
        c = CallFile(self.call, self.action)
        self.assertTrue(c.filename)

    def test_attrs_default_tempdir(self):
        """Ensure default `tempdir` attribute works."""
        c = CallFile(self.call, self.action)
        self.assertTrue(c.tempdir)

    def test_str(self):
        """Ensure `__str__` works."""
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir)
        self.assertTrue('archive' in c.__str__() and 'user' in c.__str__() and
            'spool_dir' in c.__str__())

    def test_is_valid_valid_call(self):
        """Ensure `is_valid` works using a valid `call` attribute."""
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir)
        self.assertTrue(c.is_valid())

    def test_is_valid_valid_action(self):
        """Ensure `is_valid` works using a valid `action` attribute."""
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir)
        self.assertTrue(c.is_valid())

    def test_is_valid_valid_spool_dir(self):
        """Ensure `is_valid` works using a valid `spool_dir` attribute."""
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir)
        self.assertTrue(c.is_valid())

    def test_is_valid_valid_call_is_valid(self):
        """Ensure `is_valid` works when `call.is_valid()` works."""
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir)
        self.assertTrue(c.is_valid())

    def test_is_valid_invalid_call(self):
        """Ensure `is_valid` fails given an invalid `call` attribute."""
        c = CallFile('call', self.action, spool_dir=self.spool_dir)
        self.assertFalse(c.is_valid())

    def test_is_valid_invalid_action(self):
        """Ensure `is_valid` fails given an invalid `action` attribute."""
        c = CallFile(self.call, 'action', spool_dir=self.spool_dir)
        self.assertFalse(c.is_valid())

    def test_is_valid_invalid_spool_dir(self):
        """Ensure `is_valid` fails given an invalid `spool_dir` attribute."""
        c = CallFile(self.call, self.action, spool_dir='/woot')
        self.assertFalse(c.is_valid())

    def test_is_valid_invalid_call_is_valid(self):
        """Ensure `is_valid` fails when `call.is_valid()` fails."""
        c = CallFile(Call('channel', wait_time='10'), self.action,
                spool_dir=self.spool_dir)
        self.assertFalse(c.is_valid())

    def test_buildfile_is_valid(self):
        """Ensure `buildfile` works with well-formed attributes."""
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir)
        self.assertTrue(c.buildfile())

    def test_buildfile_raises_validation_error(self):
        """Ensure `buildfile` raises `ValidationError` if the `CallFile` can't
        be validated.
        """
        cf = CallFile(self.call, self.action, spool_dir='/woot')

        with self.assertRaises(ValidationError):
            cf.buildfile()

    def test_buildfile_valid_archive(self):
        """Ensure that `buildfile` works with a well-formed `archive`
        attribute.
        """
        c = CallFile(self.call, self.action, archive=True,
                spool_dir=self.spool_dir)
        self.assertTrue('Archive: yes' in ''.join(c.buildfile()))

    def test_buildfile_invalid_archive(self):
        """Ensure `buildfile` works when `archive` is false."""
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir)
        self.assertFalse('Archive:' in ''.join(c.buildfile()))

    def test_contents(self):
        """Ensure that the `contents` property works."""
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir)
        self.assertTrue('channel' in c.contents and
            'application' in c.contents and 'data' in c.contents)

    def test_writefile_creates_file(self):
        """Ensure that `writefile` actually generates a call file on the disk.
        """
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir)
        c.writefile()
        self.assertTrue((Path(c.tempdir) / Path(c.filename)).abspath().exists())

    def test_spool_no_time_no_user(self):
        """Ensure `spool` works when no `time` attribute is supplied, and no
        `user` attribute exists.
        """
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir)
        c.spool()
        self.assertTrue((Path(c.spool_dir) / Path(c.filename)).abspath().exists())

    def test_spool_no_time_no_spool_permission_error(self):
        """Ensure that `spool` raises `NoSpoolPermissionError` if the user
        doesn't have permissions to write to `spool_dir`.

        NOTE: This test WILL fail if the user account you run this test under
        has write access to the / directory on your local filesystem.
        """
        c = CallFile(self.call, self.action, spool_dir='/')

        with self.assertRaises(NoSpoolPermissionError):
            c.spool()

    def test_spool_no_time_user(self):
        """Ensure that `spool` works when no `time` attribute is specified, and
        a valid `user` attribute exists.
        """
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir,
                user=getuser())
        c.spool()

    def test_spool_no_time_no_user_error(self):
        """Ensure that `spool` raises `NoUserError` if the user attribute is
        not a real system user.
        """
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir,
                user='asjdfgkhkgaskqtjwhkjwetghqekjtbkwthbjkltwhwklt')

        with self.assertRaises(NoUserError):
            c.spool()

    def test_spool_no_time_no_user_permission_error(self):
        """Ensure that `spool` raises `NoUserPermissionError` if the user
        specified does not have permissions to write to the Asterisk spooling
        directory.
        """
        c = CallFile(self.call, self.action, spool_dir='/', user='root')

        with self.assertRaises(NoUserPermissionError):
            c.spool()

    def test_spool_time_no_user_invalid_time_error(self):
        """Ensure that `spool` raises `InvalidTimeError` if the user doesn't
        specify a valid `time` parameter.
        """
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir)

        with self.assertRaises(InvalidTimeError):
            c.spool(666)

    def test_spool_time_no_user(self):
        """Ensure that `spool` works when given a valid `time` parameter."""
        c = CallFile(self.call, self.action, spool_dir=self.spool_dir)
        d = datetime.now()
        c.spool(d)
        self.assertEqual((Path(c.tempdir) / Path(c.filename)).abspath().atime, mktime(d.timetuple()))
