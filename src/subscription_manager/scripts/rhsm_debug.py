# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

#
# Copyright (c) 2010 - 2012 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#

# hack to allow bytes/strings to be interpolated w/ unicode values (gettext gives us bytes)
# Without this, for example, "Формат: %s\n" % u"foobar" will fail with UnicodeDecodeError
# See http://stackoverflow.com/a/29832646/6124862 for more details
import six
import sys
if six.PY2:
    reload(sys)
    sys.setdefaultencoding('utf-8')
import os

from subscription_manager.i18n import configure_i18n, ugettext as _
configure_i18n()

from rhsm import logutil

logutil.init_logger()

from rhsm_debug.cli import RhsmDebugCLI
from subscription_manager.cli import system_exit


try:
    from subscription_manager.injectioninit import init_dep_injection
    init_dep_injection()

except KeyboardInterrupt:
    system_exit(0, "\nUser interrupted process.")
except ImportError as err:
    system_exit(2, "Unable to find Subscription Manager module.\n"
                   "Error: %s" % err)

# quick check to see if you are a super-user.
if os.getuid() != 0:
    sys.stderr.write('Error: this command requires root access to execute\n')
    sys.exit(8)


def main():
    return RhsmDebugCLI().main()


if __name__ == '__main__':
    try:
        sys.exit(abs(main() or 0))
    except SystemExit as sys_err:
        # This is a non-exceptional exception thrown by Python 2.4, just
        # re-raise, bypassing handle_exception
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except IOError:
            pass
        raise sys_err
    except KeyboardInterrupt:
        sys.stderr.write("\n" + _("User interrupted process."))
        sys.exit(0)
    except Exception as err:
        # rhsm-debug can be invoked from sosreport/libreport/abrt, so
        # letting exceptions all the up to the system excepthook
        # can cause chaos (abrt handler gets called, invokes sosreport, etc)
        sys.stderr.write("Error collecting rhsm-debug information: %s\n" % err)
        sys.exit(-1)
