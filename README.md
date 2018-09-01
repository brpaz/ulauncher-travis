# Ulauncher Travis

> [ulauncher](https://ulauncher.io/) Extension to quicly see the build status of your [Travis](https://travis-ci.org/) projects.

## Usage

![demo](demo.gif)

## Features

* List your Travis CI repos.
* See the latest 5 builds for each repo.
* Open the repo page on Travis Website (Alt + Enter)

## Requirements

* [ulauncher](https://ulauncher.io/)
* Python >= 2.7
* A [Travis](https://travis-ci.org/) Account.
* [travis.rb](https://github.com/travis-ci/travis.rb) - Travis client needed to authenticate with Travis API.

## Install

Open ulauncher preferences window -> extensions -> add extension and paste the following url:

```https://github.com/brpaz/ulauncher-travis```

## Usage

1. Run ```travis login``` from command line to generate an access token.
2. Copy the generated access token into the plugin settings.
3. Profit
 
## Development

```
git clone https://github.com/brpaz/ulauncher-travis
cd ~/.cache/ulauncher_cache/extensions/ulauncher-travis
ln -s <repo_location> ulauncher-travis
```

To see your changes, stop ulauncher and run it from the command line with: ```ulauncher -v```.

## Todo

* Index user repositories in the background.

## License 

MIT
