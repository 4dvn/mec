# massExploitConsole
a collection of hacking tools with a cli ui

 [![Bless](https://cdn.rawgit.com/LunaGao/BlessYourCodeTag/master/tags/bacon.svg)](http://lunagao.github.io/BlessYourCodeTag/) 

> take a look at [mec-ng](https://github.com/jm33-m0/mec-ng "new mec, written in Go")

## screenshot

![](/screenshot/main.png)


## disclaimer

- please use this tool only on **authorized systems**, im not responsible for any damage caused by users who ignore my warning
- exploits are adapted from other sources, please refer to their author info
- please note, due to my limited programming experience (it's my first Python project), you can expect some silly bugs


## features

- [x] an easy-to-use cli ui
- [x] execute any adpated exploits with **process-level concurrency**
- [x] some built-in exploits (automated)
- [x] hide your ip addr using `proxychains4` and `ss-proxy` (built-in)
- [x] zoomeye host scan (10 threads)
- [x] a simple baidu crawler (multi-threaded)
- [x] censys host scan

## getting started

```bash
git clone https://github.com/jm33-m0/massExpConsole.git && cd massExpConsole && ./install.py
```

- when installing pypi deps, `apt-get install libncurses5-dev` (for Debian-based distros) might be needed
- now you should be good to go (if not, please report missing deps [here](https://github.com/jm33-m0/massExpConsole/issues))
- type `proxy` command to run a pre-configured [Shadowsocks](https://github.com/shadowsocks/shadowsocks-go) socks5 proxy in the background, `vim ./data/ss.json` to edit proxy config. and, `ss-proxy` exits with `mec.py`


## requirements

- GNU/Linux, WSL, MacOS (not tested), fully tested under [Arch Linux](https://www.archlinux.org), [Kali Linux (Rolling, 2018)](https://www.kali.org), Ubuntu Linux (16.04 LTS) and Fedora 25 (it will work on other distros too as long as you have dealt with all deps)
- Python 3.5 or later (or something might go wrong, [https://github.com/jm33-m0/massExpConsole/issues/7#issuecomment-305962655](https://github.com/jm33-m0/massExpConsole/issues/7#issuecomment-305962655))
- `proxychains4` (in `$PATH`), used by exploiter, requires a working socks5 proxy (you can modify its config in `mec.py`)
- Java is required when using Java deserialization exploits, you might want to install `openjdk-8-jre` if you haven't installed it yet
- **note** that you have to install all the deps of your exploits or tools as well


## usage

- just run `mec.py`, if it complains about missing modules, install them
- if you want to add your own exploit script (or binary file, whatever):
    - `cd exploits`, `mkdir <your_exploit_dir>`
    - your exploit should take the last argument passed to it as its target, dig into `mec.py` to know more
    - `chmod +x <exploit>` to make sure it can be executed by current user
    - use `attack` command then `m` to select your custom exploit
- type `help` in the console to see all available features
- `zoomeye` requires a valid user account config file `zoomeye.conf`


## how to contribute

- if you had any issues, please report them to *[https://github.com/jm33-m0/massExpConsole/issues](https://github.com/jm33-m0/massExpConsole/issues)*
- **report any unhandled exceptions** you encounter, 'coz i haven't fully tested it
- open a pull request when you have fixed any bugs or added any features
- i would appreciate you adding your own adapted exploits to this repo
- any suggestions are welcomed
