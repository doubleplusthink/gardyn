import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def guarantee_dir(path):
    """
        split path by os.sep("/" or "\")
        loop from the beginning of paths 
        make sure each path exisits
        create one if not
    """
    paths = path.split(os.sep)
    try:
        for index in range(len(paths)):
            if not paths[index]:
                # use continue instead of break because the paths[0] may be empty sometimes
                continue
            curr = os.sep.join(paths[0:index+1])
            if not os.path.isdir(curr):
                os.mkdir(curr)
    except Exception:
        raise SystemError(message=path)
    finally:
        return path