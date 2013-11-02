import select
import sh
import sys

class Deployzilla(object):
    def main(self):
        # check if we have stdin data
        if not select.select([sys.stdin,],[],[],0.0)[0]:
            print "ERROR: You need to invoke Deployzilla from a post-receive hook (no stdin)"
            return

        # read in our git data
        old, new, ref = str(sys.stdin.read()).split()

        print ref
