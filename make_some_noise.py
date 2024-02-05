#!/usr/bin/env python

""" Attempts to play a good sound if all previous pre-commit hooks passed and a bad sound if they failed

Plays a third sound if the pre-requisites are bad.

This hook will only fail if its prerequisites arent met.  Which are currently:
    1. to have an unofficial fork of pre-commit installed
    2. to be the last hook installed for your repo
    3. if the required sound-playing exe or wavs are not at the expected path
    4. if the sound player is not executable by this process
    5. if the current OS is not windows

Fork available at https://github.com/breadbros/pre-commit/tree/new_environment_variables

Currently only works for windows

cmdmp3.exe from https://github.com/jimlawless/cmdmp3 and is used here under the MIT License
fail.wav and pass.wav are from Sully, A Very Serious RPG ( https://sullyrpg.com ) and are used here with permission from Breadbros Games
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys

script_filepath = os.path.abspath(__file__)

windows_player_path = ".pre-commit/make_some_noise/cmdmp3.exe"
pass_wav_path = ".pre-commit/make_some_noise/pass.wav"
fail_wav_path = ".pre-commit/make_some_noise/fail.wav"
error_wav_path = ".pre-commit/make_some_noise/error.wav"


def check_path(fname):
    script_filepath = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.join(script_filepath, fname)

    if os.path.isfile(absolute_path):
        return True
    else:
        # File doesn't exist, output an error with the absolute path
        print(f"Error: File not found at {absolute_path}")
        return False


def check_executable(filepath):
    # Check if the file is executable
    if not os.access(filepath, os.X_OK):
        print(f"The file '{filepath}' is not executable by the current process.")
        return false

    # File is executable, return True or perform additional actions
    return True


def is_windows():
    system_platform = platform.system()
    return system_platform == "Windows"


if not is_windows():
    print(
        "The current OS is not windows, which is the only supported OS at this time. Failing"
    )
    sys.exit(5)

required_files_exist = True
required_files_exist &= check_path(windows_player_path)
required_files_exist &= check_path(pass_wav_path)
required_files_exist &= check_path(fail_wav_path)
required_files_exist &= check_path(error_wav_path)

if not required_files_exist:
    print("Required files are missing. Failing")
    sys.exit(3)

if not check_executable(windows_player_path):
    print("The soundplaying exe is not executable. Failing")
    sys.exit(4)


def play_sound(wav):
    res = subprocess.run(
        [windows_player_path, wav],
        capture_output=True,
    )


def play_pass():
    play_sound(pass_wav_path)


def play_fail():
    play_sound(fail_wav_path)


def play_error():
    play_sound(error_wav_path)


def env_check(name):
    if name in os.environ:
        return True
    else:
        print(f"required env variable '{name}' missing")
        return False


is_valid = True
is_valid &= env_check("PRE_COMMIT_INDEX_OF_CURRENT_HOOK")
is_valid &= env_check("PRE_COMMIT_NUMBER_HOOKS_BEING_RUN")
is_valid &= env_check("PRE_COMMIT_SUMMED_RETVAL")

if not is_valid:
    print("Your pre-commit installed doesn't meet the requirements of this hook")
    print(
        "Please install https://github.com/breadbros/pre-commit/tree/new_environment_variables"
    )
    play_error()
    sys.exit(1)


def converter(name):
    try:
        return int(os.environ[name])
    except ValueError as e:
        print(f"Invalid value for env variable '${name}': should be a parsable int")
        return -1


idx = converter("PRE_COMMIT_INDEX_OF_CURRENT_HOOK")
total = converter("PRE_COMMIT_NUMBER_HOOKS_BEING_RUN")
retval = converter("PRE_COMMIT_SUMMED_RETVAL")

if idx == -1 or total == -1 or retval == -1:
    print("Invalid values from your pre-commit ENV variables. failing")
    play_error()
    sys.exit(2)

if idx != total - 1:
    print(
        f"This hook was not the past pre-commit hook installed, which it needs to be. Currently reporting {idx+1} out of {total}. failing"
    )
    play_error()
    sys.exit(6)

if retval == 0:
    play_pass()
else:
    play_fail()

sys.exit(0)
