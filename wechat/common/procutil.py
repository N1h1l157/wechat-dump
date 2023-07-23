# -*- coding: utf-8 -*-

import subprocess
import logging
logger = logging.getLogger(__name__)

def subproc_call(cmd, timeout=None):
    """
    Execute a command with timeout, and return STDOUT and STDERR

    Args:
        cmd(str): the command to execute.
        timeout(float): timeout in seconds.

    Returns:
        output(bytes), retcode(int). If timeout, retcode is -1.
    """
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT,
            shell=True, timeout=timeout)
        return output, 0
    except subprocess.TimeoutExpired as e:
        logger.warning("Command '{}' timeout!".format(cmd))
        if e.output:
            logger.warning(e.output.decode('utf-8'))
            return e.output, -1
        else:
            return "", -1
    except subprocess.CalledProcessError as e:
        logger.warning("Command '{}' failed, return code={}".format(cmd, e.returncode))
        logger.warning(e.output.decode('utf-8'))
        return e.output, e.returncode
    except Exception:
        logger.warning("Command '{}' failed to run.".format(cmd))
        return "", -2


def subproc_succ(cmd):
    """
    Like subproc_call, but expect the cmd to succeed.
    """
    output, ret = subproc_call(cmd)
    assert ret == 0
    return output



