a small utility to bootstrap conan recipes from library repositories (e.g. GitHub).
the project uses [GitHub GraphQL API](https://docs.github.com/en/graphql) to extract the metadata from the repository.
afterwards, it passes the metadata to the [conan new](https://docs.conan.io/en/latest/reference/commands/creator/new.html) command.
project uses [cci.templates](https://github.com/SSE4/cci.templates) to generate almost working recipe skeleton.
it also might be useful to run [cci.cmake_file_api](https://github.com/SSE4/cci.cmake-file-api) hook to generate missing components information.

## installtion

TODO : pip

## extracted metadata

- latest release (or tag, if there are no releases)
- release tarball url
- tarball sha256
- description
- homepage
- license
- topics

## TODO

### detect project type

right now, [cci.cmake](https://github.com/SSE4/cci.templates/tree/master/templates/command/new/cci.cmake) template is always used.
it would be nice to detect project type (e.g. by scanning the repository for typical files like `meson.build`, `CMakeLists.txt`, `configure`, `Makefile`, etc. to select the appropriate template).

### more project hostings

although MANY projects are hosted on GitHub, there are several other popular project hostings we would like to be able to extract metadata from.

- [BitBucket](https://bitbucket.org/)
- [GitLab](https://about.gitlab.com/)
- [GNU Savannah](https://savannah.gnu.org/)
- [SourceForge](https://sourceforge.net/)

### use without GITHUB_TOKEN

maybe it's possible to somehow don't require GITHUB_TOKEN environment variable?
could it be [Github Action](https://github.com/features/actions) or [GitHub App](https://docs.github.com/en/developers/apps/about-apps)?
or maybe just simple Web Form hosted somewhere?

### use GitHub actions to deploy to pip

it would be nice to use `pip install` to get the tool available.
