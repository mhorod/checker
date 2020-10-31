## About
A simple tester, useful for testing programs through stdin/stdout.
Created mainly for remote programming contests.

## Prerequisites
Python 3.6+ 
`python` and `pip` should be available from command line.
If that's not the case, update your `PATH` variable.

## Installation

Simply run 
```
python3 setup.py
```

## Usage

### Basics
To run tests on your program execute:
```
python3 run-tests.py [options]
```
You can skip options to run with default values

### Test structure
The default assumed structure of `tests` directory is
```
tests/
├── group1
└── group2
...
```
Directory structure in group is ignored.
Instead, checker requires `.in` and `.out` files to be present.
The only naming requirement is that lexicographic sorting should preserve matching.

### Configuration
Currently available options are:

| Option  | Description                  | Default     | Notes |
|:-------:|:----------------------------:|:-----------:|:---:|
| `-h`    | display help                 | unset       | |
| `-p`    | path to the program          | `./main`    | |
| `-d`    | path to test directory       | `tests`     | | 
| `-g`    | list of groups regexes       | unset (all) | |
| `-b`    | break on error               | `true`      | |
| `-t`    | timeout                      | unset       | |
| `--sha` | calculate sha-256 of outputs | unset       | skips output verification |

### Example
Suppose you have the following test structure:
```
tests/
├── medium1
├── medium2
├── tiny1
└── tiny2
```
If you want to run program `./first` on all `tiny` tests with `0.5s` timeout:
```
python3 run-tests.py -p first -g tiny.* -t 0.5
```
If you have no access to a verified output and you want to check program's behavior
you can run
```
python3 run-tests.py -p first -g tiny.* -t 0.5 --sha
```
The checksum can be then used to compare all answers at once without the need to generate (possibly large) output.

## License
Distributed under MIT license.

