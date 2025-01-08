#!/usr/bin/env python

""" Attempts to hit one of three soundboard server endpoints based on the status of the current pre-commit hook.

(Note: old code needs to be cleaned out)
"""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys

import requests


def parse_args():
    parser = argparse.ArgumentParser(description="Check URL accessibility")
    parser.add_argument("--url-alive", type=str, help="URL to check if alive")
    parser.add_argument("--url-fail", type=str, help="URL to check if fail")
    parser.add_argument("--url-pass", type=str, help="URL to check if pass")

    args = parser.parse_args()
    return args


def is_url_accessible(url, timeout):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False


# Example usage:
url = "http://SWORDFISH:22222"
timeout = 5  # seconds

args = parse_args()

url_alive = args.url_alive
url_fail = args.url_fail
url_pass = args.url_pass
url_error = args.url_error

print(f"url_alive: {url_alive}")
print(f"url_fail: {url_fail}")
print(f"url_pass: {url_pass}")
print(f"url_error: {url_error}")

missing_args = []

if not url_alive:
    missing_args.append("--url-alive")

if not url_fail:
    missing_args.append("--url-fail")

if not url_pass:
    missing_args.append("--url-fail")

if not url_error:
    missing_args.append("--url-error")

if missing_args:
    print(f"Missing required arguments: {missing_args}")
    exit(1)

is_alive = is_url_accessible(url_alive, timeout)
if not is_alive:
    print(f"URL {url_alive} is not accessible")
    exit(1)


# ##################################  old stuff vvv

script_filepath = os.path.abspath(__file__)

windows_player_path = ".pre-commit/make_some_noise/cmdmp3.exe"
osx_player_cmd = "afplay"
linux_player_cmd = "aplay"
pass_wav_path = ".pre-commit/make_some_noise/pass.wav"
fail_wav_path = ".pre-commit/make_some_noise/fail.wav"
error_wav_path = ".pre-commit/make_some_noise/error.wav"


def check_path(fname):
    script_filepath = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.join(script_filepath, fname)

    if os.path.isfile(absolute_path):
        return absolute_path
    else:
        # File doesn't exist, output an error with the absolute path
        print(f"Error: File not found at {absolute_path}")
        return ""


def check_executable(filepath):
    # Check if the file is executable
    if not os.access(filepath, os.X_OK):
        print(f"The file '{filepath}' is not executable by the current process.")
        return False

    # File is executable, return True or perform additional actions
    return True

def is_linux():
    system_platform = platform.system()
    return system_platform == "Linux"

def is_windows():
    system_platform = platform.system()
    return system_platform == "Windows"

def is_mac():
    system_platform = platform.system()
    return system_platform == "Darwin"


if not (is_windows() or is_mac() or is_linux()):
    print(
        "The current OS ("+platform.system()+") is not supported at this time. Failing"
    )
    sys.exit(5)

if is_windows():
    windows_player_path = check_path(windows_player_path)

pass_wav_path = check_path(pass_wav_path)
fail_wav_path = check_path(fail_wav_path)
error_wav_path = check_path(error_wav_path)

required_files_exist = True

if is_windows():
    required_files_exist &= windows_player_path != ""

required_files_exist &= pass_wav_path != ""
required_files_exist &= fail_wav_path != ""
required_files_exist &= error_wav_path != ""

if not required_files_exist:
    print("Required files are missing. Failing")
    sys.exit(3)

if is_windows() and not check_executable(windows_player_path):
    print("The soundplaying exe is not executable. Failing")
    sys.exit(4)


def play_sound(wav):
    if is_windows():
        res = subprocess.run(
            [windows_player_path, wav],
            capture_output=True,
        )
    if is_mac():
        res = subprocess.run(
            [osx_player_cmd, wav, "&"],
            capture_output=True,
        )
    if is_linux():
        res = subprocess.run(
            [linux_player_cmd, wav, "&"],
            capture_output=True,
        )


def play_pass():
    is_url_accessible(url_pass)

def play_fail():
    is_url_accessible(url_fail)

def play_error():
    is_url_accessible(url_error)

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

if(is_mac() or is_linux()): #linux and macs report reverse order?
    if idx != 0:
        print(
            f"This hook was not the last pre-commit hook installed, which it needs to be. failing"
        )
        play_error()
        sys.exit(7)
else:
    if idx != total - 1:
        print(
            f"This hook was not the last pre-commit hook installed, which it needs to be. Currently reporting {idx+1} out of {total}. failing"
        )
        play_error()
        sys.exit(6)

if retval == 0:
    play_pass()
else:
    play_fail()

sys.exit(0)
