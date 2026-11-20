#!/usr/bin/env bash
# Generates locks/conan.lock, a single lockfile for the external (not locally built) dependencies of both
# the Linux and Windows profiles (the per-profile lockfiles are merged).
#
# Packages which are built from this repository are excluded, so use the lockfile with --lockfile-partial.
set -euo pipefail

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# The recipes use gnustep-helpers as a python_require; exporting it is enough.
conan export gnustep-helpers

exclude_args=(
    --requires="getopt/*"
    --requires="gnustep/*"
    --requires="gnustep-back/*"
    --requires="gnustep-base/*"
    --requires="gnustep-gui/*"
    --requires="gnustep-headless/*"
    --requires="gnustep-make/*"
    --requires="gnustep-systempreferences/*"
    --requires="gnustep-winuxtheme/*"
    --requires="libdispatch/*"
    --requires="libobjc2/*"
    --build-requires="gnustep-make/*"
    --build-requires="libdispatch/*"
    --build-requires="libobjc2/*"
    --python-requires="gnustep-helpers/*"
)

# generate_lockfile <profile> <lockfile>
generate_lockfile() {
    conan workspace super-install --profile:a="profiles/$1" -c tools.build:skip_test=True --build=never \
        -cc core.version_ranges:resolve_prereleases=True \
        --output-folder="$work/output" --lockfile-out="$work/full.lock"
    conan lock remove --lockfile="$work/full.lock" --lockfile-out="$2" "${exclude_args[@]}"
}

generate_lockfile "linux-clang-nodist" "$work/linux.lock"
generate_lockfile "windows-clang-vs2022" "$work/windows.lock"

conan lock merge --lockfile="$work/linux.lock" --lockfile="$work/windows.lock" --lockfile-out=conan.lock
