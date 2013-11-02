#!/usr/bin/env python
#
# Entry point to Deployzilla
# 

if __name__ == '__main__':
    import inspect
    import os
    import sys

    # Construct the directory to our 'lib' folder, relative to this file, even
    # if we're a symlink (like to a post-receive file, fancy that)
    #
    # See: http://stackoverflow.com/a/6098238
    frame_file = inspect.getfile(inspect.currentframe())
    base_dir = os.path.split(os.path.realpath(frame_file))[0]
    deployzilla_dir = os.path.join(base_dir, "lib")

    if deployzilla_dir not in sys.path:
        sys.path.insert(0, deployzilla_dir)

    # import our object and run it
    from deployzilla import Deployzilla
    Deployzilla().main()
