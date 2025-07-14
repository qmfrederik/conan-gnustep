import yaml
from pygit2 import Repository, BlobIO, Commit, Object
from pygit2.enums import SortMode

# Automatically calculates the package version (x.y.z-{prerelease}+{build}) for the package.
# 
# The build version is the number of commits to the recipe folder since a new upstream version was packaged.
# - The build version is reset every time a new version of an upstream is packaged.
# - Commits which do not modify the recipy are ignored.
#
# A prerelease tag is added if changes to the recipe were made on a branch
# - If we're on a branch, and the package was not changed on that branch, no prerelease tag is added
#
# Version and diagnostics data is saved in the package (version.yml), including
# - Package version
# - Recipe version
# - Recipe last meaningful commit
#
# If not built from a Git repo, the build version and prerelease version data is fetched from a cache file (version.yml)
#
# Workflows:
# - Local development
# - Runs on a CI server
# - Supports squash merges
# - Works for installed packages

package_name = "gnustep-gui"

with open(f"{package_name}/conandata.yml") as stream:
    version_data = yaml.safe_load(stream)

package_version = next(iter(version_data["sources"]))
revision_count = 0

repo = Repository('.git')

# Determine whether the tree for the current package was changed between the current branch
# and the main branch.
head_tree = repo.get(repo.head.target).tree
if head_tree.__contains__(package_name):
    head_package_tree = head_tree / package_name
else:
    head_package_tree = None

main_tree = repo.resolve_refish('main')[0].tree
if main_tree.__contains__(package_name):
    main_package_tree = main_tree / package_name
else:
    main_package_tree = None

is_prerelease = head_package_tree != main_package_tree

# Determine the number of recipes we've had for the current version of the package
previous_recipe_tree_id = None

for commit in repo.walk(repo.head.target, SortMode.TOPOLOGICAL):
    if len(commit.parents) > 0:
        parent_commit = commit.parents[0]
    else:
        parent_commit = None

    if commit.tree.__contains__(package_name):
        recipe_tree = commit.tree / package_name
        commit_package_version = None

        if recipe_tree.__contains__("conandata.yml"):
            commit_version_data_tree = recipe_tree / "conandata.yml"
            with BlobIO(commit_version_data_tree) as stream:
                commit_version_data = yaml.safe_load(stream)
                commit_package_version = next(iter(version_data["sources"]))

        if commit_package_version != package_version:
            break

        # If there are no changes for this recipe on the main branch
        if recipe_tree.id != previous_recipe_tree_id:
            revision_count += 1
            previous_recipe_tree_id = recipe_tree.id
            print(f">> recipe changed! Now at revision {revision_count}")

recipe_version = package_version

# If we're not building off main, then consider this a prerelease version
if is_prerelease:
    recipe_version = f"{recipe_version}-g{commit.short_id}"

# Add the revision count as a build version, this will force Conan to pick up newer builds
recipe_version = f"{recipe_version}+{revision_count}"

print(f"Done! Current version: {recipe_version}")
