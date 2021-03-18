import sys
import signal


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def errorOut(message, error=None, code=1):
        """
        Prints the specified error and exits the program with the specified code

        :param str message: an error message to be displayed
        :param Exception error: the error caught
        :param int code: a code to exit the program with (set to 1 by default)
        """

        msg = f'ERROR: {message}. '
        if error:
            msg += f'Details: {error}.'
        sys.stderr.write(f'{msg}\n')
        sys.exit(code)

    @staticmethod
    def processPort(port):
        if not port.isdigit():
            Utils.errorOut(f'invalid port provided. [{port}] is not a valid port')
        casted = int(port)
        if not (casted in range(1, 65535)):
            Utils.errorOut(f'invalid port provided. Please enter an integer between 1 and 65535. [{port}] is not a valid port')
        return casted

    @staticmethod
    def processClientArgs():
        """
        Validates and processes the arguments required for the client program

        :return tuple[str, int, str]:
        """

        if len(sys.argv) != 4:
            Utils.errorOut(
                'invalid number of arguments provided. Please enter the host, port and file name in that particular order')

        return sys.argv[1], Utils.processPort(sys.argv[2]), sys.argv[3]