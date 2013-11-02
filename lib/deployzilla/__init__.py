import select
import sh
import sys

class Deployzilla(object):
    def main(self):
        # check if we have stdin data
        if not select.select([sys.stdin,],[],[],0.0)[0]:
            print "ERROR: You need to invoke Deployzilla from a post-receive" \
                  "hook (no stdin)"
            return

        # read in our git data
        try:
            input_data = sys.stdin.read()
            old, new, ref = input_data.split()
        except ValueError:
            print "ERROR: Oops. Either GIT **REALLY** messed up or someone is" \
                  "invoking Deployzilla by hand..."
            return

        ref = ref.lstrip("refs/heads/")
        self.check_deployment(ref)

    def check_deployment(self, ref):
        "Use git to check if we have a deploy.yaml config file"
        pass
