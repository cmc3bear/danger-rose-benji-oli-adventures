# [1.12.0](https://github.com/svange/danger-rose/compare/v1.11.0...v1.12.0) (2025-08-03)


### Major Features

* **BPM Traffic System (Issue #18)**: Complete implementation of beat-synchronized traffic spawning and hazards ([d217f3c](https://github.com/svange/danger-rose/commit/d217f3c))
  - Rhythmic traffic controller with music synchronization
  - Beat-synchronized hazard spawning (oil slicks, debris)
  - Visual BPM overlay (toggle with B key)
  - Speed modulation based on rhythm intensity
  - Graceful fallback when disabled

* **Hacker Typing Minigame (Issue #27)**: Complete Matrix-themed typing challenge ([d217f3c](https://github.com/svange/danger-rose/commit/d217f3c))
  - Interactive laptop entity in hub world
  - Progressive difficulty system (passwords → commands → scripts)
  - Terminal interface with retro CRT aesthetics
  - Full scene lifecycle with proper navigation
  - Challenge content management system

* **Comprehensive Sound System (Issue #33)**: 49+ high-quality sound effects generated ([d217f3c](https://github.com/svange/danger-rose/commit/d217f3c))
  - Hub character voices (Danger, Rose, Dad)
  - Complete Drive scene audio (vehicle, collision, traffic)
  - UI feedback sounds for enhanced interaction
  - 11labs API integration for professional quality
  - Retro sound processing pipeline

* **Character Expansion (Issue #28)**: New playable characters added ([d217f3c](https://github.com/svange/danger-rose/commit/d217f3c))
  - Benji: Complete sprite sets for all 5 scenes
  - Olive: Complete sprite sets for all 5 scenes
  - Enhanced Dad, Danger, Rose sprite coverage
  - Animation metadata system implementation


### Bug Fixes

* resolve Drive scene crash and music bleed-through issues ([56e7bc3](https://github.com/svange/danger-rose/commit/56e7bc3))
  - Fixed BPMTrafficIntegration constructor parameter mismatch
  - Enhanced music cleanup on scene exit
  - Added missing screen_height parameter to BMP system

* fix hub world door overlap preventing proper interaction ([56e7bc3](https://github.com/svange/danger-rose/commit/56e7bc3))
  - Improved collision detection for minigame access
  - Enhanced player movement near interactive elements


### Development Tools

* add comprehensive asset audit tool ([d217f3c](https://github.com/svange/danger-rose/commit/d217f3c))
* create placeholder music generator to prevent crashes ([d217f3c](https://github.com/svange/danger-rose/commit/d217f3c))
* implement character animation guide and sprite organization ([d217f3c](https://github.com/svange/danger-rose/commit/d217f3c))
* enhance development workflow with new automation tools ([302a399](https://github.com/svange/danger-rose/commit/302a399))

# [1.11.0](https://github.com/svange/danger-rose/compare/v1.10.0...v1.11.0) (2025-08-03)


### Bug Fixes

* resolve Drive scene crash and music bleed-through issues ([56e7bc3](https://github.com/svange/danger-rose/commit/56e7bc3))
* fix hub world door overlap preventing proper interaction ([56e7bc3](https://github.com/svange/danger-rose/commit/56e7bc3))


### Features

* add comprehensive asset audit tool ([d217f3c](https://github.com/svange/danger-rose/commit/d217f3c))
* create placeholder music generator to prevent crashes ([d217f3c](https://github.com/svange/danger-rose/commit/d217f3c))
* implement character animation guide and sprite organization ([d217f3c](https://github.com/svange/danger-rose/commit/d217f3c))
* enhance development workflow with new automation tools ([302a399](https://github.com/svange/danger-rose/commit/302a399))

# [1.10.0](https://github.com/svange/danger-rose/compare/v1.9.0...v1.10.0) (2025-08-01)


### Bug Fixes

* consolidate pre-commit and ruff configurations (closes [#97](https://github.com/svange/danger-rose/issues/97)) ([#98](https://github.com/svange/danger-rose/issues/98)) ([f7dfe70](https://github.com/svange/danger-rose/commit/f7dfe70c5f827efe93693260cecf456cef847b24))


### Features

* add pygame-game-developer Claude subagent ([#96](https://github.com/svange/danger-rose/issues/96)) ([b7fa540](https://github.com/svange/danger-rose/commit/b7fa5407e2f17624cd75e3f3f18ad270e38cd81b)), closes [#95](https://github.com/svange/danger-rose/issues/95)

# [1.9.0](https://github.com/svange/danger-rose/compare/v1.8.0...v1.9.0) (2025-07-31)


### Features

* add comprehensive Docker development environment ([#93](https://github.com/svange/danger-rose/issues/93)) ([29b646d](https://github.com/svange/danger-rose/commit/29b646d14c88edb047f1395d041ad44d3c6f69f4))

# [1.8.0](https://github.com/svange/danger-rose/compare/v1.7.0...v1.8.0) (2025-07-29)


### Features

* implement Vegas Sphere boss with phases ([#89](https://github.com/svange/danger-rose/issues/89)) ([aad45e9](https://github.com/svange/danger-rose/commit/aad45e9f8a6d9e4e8e2199d8c9a133fda930deb6)), closes [#25](https://github.com/svange/danger-rose/issues/25) [#31](https://github.com/svange/danger-rose/issues/31)

# [1.7.0](https://github.com/svange/danger-rose/compare/v1.6.0...v1.7.0) (2025-07-29)


### Features

* complete high score tracking system for pool game ([#88](https://github.com/svange/danger-rose/issues/88)) ([7d49e4e](https://github.com/svange/danger-rose/commit/7d49e4e04ee94ab8ede39c5e1ef020662e861ffe)), closes [#25](https://github.com/svange/danger-rose/issues/25)

# [1.6.0](https://github.com/svange/danger-rose/compare/v1.5.0...v1.6.0) (2025-07-29)


### Features

* implement trophy shelf with score display functionality ([#86](https://github.com/svange/danger-rose/issues/86)) ([a81da89](https://github.com/svange/danger-rose/commit/a81da894c23006d40010abf912644c35799026e2)), closes [#29](https://github.com/svange/danger-rose/issues/29) [#29](https://github.com/svange/danger-rose/issues/29) [#15](https://github.com/svange/danger-rose/issues/15)

# [1.5.0](https://github.com/svange/danger-rose/compare/v1.4.0...v1.5.0) (2025-07-29)


### Features

* implement moving targets for pool game ([#85](https://github.com/svange/danger-rose/issues/85)) ([877ec07](https://github.com/svange/danger-rose/commit/877ec0789478de6b1e4d99c469bd17c86afa9d08)), closes [#29](https://github.com/svange/danger-rose/issues/29) [#29](https://github.com/svange/danger-rose/issues/29) [#28](https://github.com/svange/danger-rose/issues/28)

# [1.4.0](https://github.com/svange/danger-rose/compare/v1.3.0...v1.4.0) (2025-07-29)


### Features

* implement power-up system for pool game ([#84](https://github.com/svange/danger-rose/issues/84)) ([4941658](https://github.com/svange/danger-rose/commit/49416587d8d5a93c7a09d2a02cb9f8faad63dbc3)), closes [#29](https://github.com/svange/danger-rose/issues/29) [#29](https://github.com/svange/danger-rose/issues/29)

# [1.3.0](https://github.com/svange/danger-rose/compare/v1.2.0...v1.3.0) (2025-07-29)


### Features

* implement game settings scene closes [#10](https://github.com/svange/danger-rose/issues/10) ([#82](https://github.com/svange/danger-rose/issues/82)) ([0816dd9](https://github.com/svange/danger-rose/commit/0816dd91c04ca4d4db56db12c53deb0615f1bfc3))

# [1.2.0](https://github.com/svange/danger-rose/compare/v1.1.1...v1.2.0) (2025-07-29)


### Features

* implement hub world save point system closes [#16](https://github.com/svange/danger-rose/issues/16) ([#81](https://github.com/svange/danger-rose/issues/81)) ([9dde62e](https://github.com/svange/danger-rose/commit/9dde62ee3b4bc5e32e787d91457298d35c4ae05f))

## [1.1.1](https://github.com/svange/danger-rose/compare/v1.1.0...v1.1.1) (2025-07-29)


### Bug Fixes

* simplify auto-merge to use direct merge ([#79](https://github.com/svange/danger-rose/issues/79)) ([da40562](https://github.com/svange/danger-rose/commit/da4056226a53404b7a95a6edd4264eaf4710dafa)), closes [#24](https://github.com/svange/danger-rose/issues/24)

# [1.1.0](https://github.com/svange/danger-rose/compare/v1.0.5...v1.1.0) (2025-07-29)


### Features

* implement pause menu functionality ([#78](https://github.com/svange/danger-rose/issues/78)) ([42913b5](https://github.com/svange/danger-rose/commit/42913b5842911159844094cd523c676235538667)), closes [#24](https://github.com/svange/danger-rose/issues/24)

## [1.0.5](https://github.com/svange/danger-rose/compare/v1.0.4...v1.0.5) (2025-07-29)


### Bug Fixes

* use GH_TOKEN for auto-merge workflow permissions ([#77](https://github.com/svange/danger-rose/issues/77)) ([f68bcee](https://github.com/svange/danger-rose/commit/f68bcee42303f2e10e1ed14f708d74a951ca8f34))

## [1.0.4](https://github.com/svange/danger-rose/compare/v1.0.3...v1.0.4) (2025-07-29)


### Bug Fixes

* remove non-existent LICENSE file from Windows installer ([#76](https://github.com/svange/danger-rose/issues/76)) ([0141904](https://github.com/svange/danger-rose/commit/01419044bde1273e37471ab08005290e2c228f37))

## [1.0.3](https://github.com/svange/danger-rose/compare/v1.0.2...v1.0.3) (2025-07-28)


### Bug Fixes

* comment out SetupIconFile to fix Windows installer build ([#75](https://github.com/svange/danger-rose/issues/75)) ([e165e55](https://github.com/svange/danger-rose/commit/e165e55648b470a56c4705373dabcf5fee1b8d5d))

## [1.0.2](https://github.com/svange/danger-rose/compare/v1.0.1...v1.0.2) (2025-07-28)


### Bug Fixes

* correct semantic-release output variable names to use underscores ([#74](https://github.com/svange/danger-rose/issues/74)) ([e8b4a19](https://github.com/svange/danger-rose/commit/e8b4a19f3897ecbc7e8b48b79fe63e8de01046f3))

## [1.0.1](https://github.com/svange/danger-rose/compare/v1.0.0...v1.0.1) (2025-07-28)


### Bug Fixes

* use GH_TOKEN for semantic-release and fix Windows installer condition ([#73](https://github.com/svange/danger-rose/issues/73)) ([e6fb176](https://github.com/svange/danger-rose/commit/e6fb1760e63e48014d0ea7e47b92d0cdfae0f73b))

# 1.0.0 (2025-07-28)


### Bug Fixes

* add .claude/settings.local.json to .gitignore and remove from tracking ([8a982a6](https://github.com/svange/danger-rose/commit/8a982a6404e1ed94916f0b27b89156dc91864692))
* add delta time parameter to scene update methods ([4076239](https://github.com/svange/danger-rose/commit/4076239b1c8d2872cd14e7a002f16023f5e7bd1b))
* add Poetry to PATH on Windows runners ([#68](https://github.com/svange/danger-rose/issues/68)) ([33584da](https://github.com/svange/danger-rose/commit/33584dad3cf0b51b99ceb65a94fb184edc469f57))
* allow obstacles at safe zone boundaries in test ([df719f9](https://github.com/svange/danger-rose/commit/df719f98f2ccff1a634c1a8bbab7dbefc9400df6))
* apply pre-commit formatting and linting fixes ([606130a](https://github.com/svange/danger-rose/commit/606130a613c6a2201dd6f3ce7dccb5e544ac3fd9))
* handle edge case in test_chunk_generation_and_removal ([79a0cea](https://github.com/svange/danger-rose/commit/79a0cea155f277321bd49b1837c382a0f1a45628))
* lazy load sprites and correct chunk positioning in slope generator ([54ce195](https://github.com/svange/danger-rose/commit/54ce195fe4177e0a50f9fe1db3409cd2d29e01a9)), closes [#18](https://github.com/svange/danger-rose/issues/18)
* make SettingsScene.update() dt parameter optional ([6af7d2d](https://github.com/svange/danger-rose/commit/6af7d2dccbc438820a28533987ae7b3898fb318b))
* optimize CI/CD to trigger only on pull requests ([1129e32](https://github.com/svange/danger-rose/commit/1129e32d6d80d4cab20e5d82405e5f9f15c821f2))
* remove black formatter and use ruff-format exclusively ([6eb6c63](https://github.com/svange/danger-rose/commit/6eb6c63120153c7ca840b22e949b25deff058394))
* remove implementation detail assertion from chunk generation test ([bc631a8](https://github.com/svange/danger-rose/commit/bc631a8612d3a586e212203b3a29c9defa353010))
* resolve E712 linting errors in test files ([2089b68](https://github.com/svange/danger-rose/commit/2089b68c8789fc1eaeb29d91de1176082b5fc5aa))
* restore push trigger for main branch merges ([52930cd](https://github.com/svange/danger-rose/commit/52930cd70369dd280ccbe6f2131ed7d2cc9dc130))
* skip audio-dependent tests in CI and fix slope generator test expectations ([db054ac](https://github.com/svange/danger-rose/commit/db054acbeec84bbd35556d65b8b37bfe359eada4))
* temporarily disable Windows CI runner due to Poetry installation issue ([9aa7b7a](https://github.com/svange/danger-rose/commit/9aa7b7a0d0ef992ebeb562b5fb81336619289dc6)), closes [#54](https://github.com/svange/danger-rose/issues/54)
* temporarily lower coverage requirement to 35% ([607e8aa](https://github.com/svange/danger-rose/commit/607e8aa4deebe8a96593891adc3baa7ff835bea4))
* update ruff to v0.12.3 and apply consistent formatting ([8015f31](https://github.com/svange/danger-rose/commit/8015f31120529cb94dfdaa69f4c07b007fd84585))
* use GH_TOKEN for semantic-release to bypass repository rulesets ([#72](https://github.com/svange/danger-rose/issues/72)) ([1f6d23b](https://github.com/svange/danger-rose/commit/1f6d23b9d1b5f31f33c261ff2bd89e2adc1b6def))
* use realistic scroll speeds in test_chunk_generation_and_removal ([32cd0d7](https://github.com/svange/danger-rose/commit/32cd0d7753e951f1cc7359bb9c603d23d93db840))


### Features

* add asset validation tool for development ([f3035fd](https://github.com/svange/danger-rose/commit/f3035fd4eb906b27286923943e798e2c42f5cdd0))
* add auto-merge job to game CI/CD pipeline ([cb20e39](https://github.com/svange/danger-rose/commit/cb20e397791cba86f66c1df2b8253c8b9309e132))
* add Dad AI with rubber-band movement to ski game closes [#21](https://github.com/svange/danger-rose/issues/21) ([ecda618](https://github.com/svange/danger-rose/commit/ecda61808ea980fce6fcd91421fda7603e495afa))
* add game setup documentation and asset management tools ([68105b8](https://github.com/svange/danger-rose/commit/68105b8ad69b949460f84aad6baeee49c7b7d747))
* add GitHub release workflow with Windows installer ([#63](https://github.com/svange/danger-rose/issues/63)) ([d4f228f](https://github.com/svange/danger-rose/commit/d4f228f5be844c549e18d43b6e63cd2771c088b5))
* create sound manager for music and SFX ([fcb01f6](https://github.com/svange/danger-rose/commit/fcb01f64da81dfb15ac4bd2e47eef617ff39da82)), closes [#23](https://github.com/svange/danger-rose/issues/23)
* implement basic hub world scene ([1846afd](https://github.com/svange/danger-rose/commit/1846afdb25fc3bcbb715d6f3158bb30e24235dcc)), closes [#12](https://github.com/svange/danger-rose/issues/12)
* implement basic ski minigame scene structure ([b2d5d52](https://github.com/svange/danger-rose/commit/b2d5d5204a1e1f90819be3638bd38a9b69411348)), closes [#17](https://github.com/svange/danger-rose/issues/17)
* implement collision detection and lives system for ski game closes [#19](https://github.com/svange/danger-rose/issues/19) ([6c7cf07](https://github.com/svange/danger-rose/commit/6c7cf0706428f71ef7c82eba2e5c5c20344ecd4d))
* implement configuration system with constants and settings ([469c7b0](https://github.com/svange/danger-rose/commit/469c7b0797ea956517588b3d66df6e66771d5b41)), closes [#3](https://github.com/svange/danger-rose/issues/3)
* implement door interaction system for minigame access ([5472c6a](https://github.com/svange/danger-rose/commit/5472c6a89534ce757793a9a16d1aec8090b38ebb)), closes [#14](https://github.com/svange/danger-rose/issues/14)
* implement player movement and collision detection (closes [#13](https://github.com/svange/danger-rose/issues/13)) ([6cc1e89](https://github.com/svange/danger-rose/commit/6cc1e890d1c71d48c5bbc2ebe8aa47b12f32ffee))
* implement pool minigame with water balloon shooting closes [#26](https://github.com/svange/danger-rose/issues/26) closes [#27](https://github.com/svange/danger-rose/issues/27) ([baa56cd](https://github.com/svange/danger-rose/commit/baa56cd9ffd1ab3b5d7747b7cd239c9252ded9ba))
* implement procedural slope generation for ski game closes [#18](https://github.com/svange/danger-rose/issues/18) ([6a9ead6](https://github.com/svange/danger-rose/commit/6a9ead60d35762a1fcce227e1a9244f026bf55df))
* implement save/load system with JSON persistence ([5cc8a39](https://github.com/svange/danger-rose/commit/5cc8a39239405bbbb83dcbeee372f1750be46fe6)), closes [#22](https://github.com/svange/danger-rose/issues/22)
* implement save/load system with JSON persistence ([#60](https://github.com/svange/danger-rose/issues/60)) ([7094e9b](https://github.com/svange/danger-rose/commit/7094e9bd3032551534e694a21e6e5c7df4a6204b))
* implement semantic-release with automated Windows installer ([#70](https://github.com/svange/danger-rose/issues/70)) ([bd11e78](https://github.com/svange/danger-rose/commit/bd11e78a42be7d92509053041539a7005b9d7dfb))
* implement side-scrolling Vegas scene ([297776d](https://github.com/svange/danger-rose/commit/297776db9c37de0e1eefe525a049b9b639b55290)), closes [#30](https://github.com/svange/danger-rose/issues/30)
* implement snowflake collection mechanics for ski game closes [#20](https://github.com/svange/danger-rose/issues/20) ([93aa142](https://github.com/svange/danger-rose/commit/93aa14215013feaa28a5b0074cfb56933e4aea05))
* integrate hub world into scene manager ([d70940d](https://github.com/svange/danger-rose/commit/d70940d3c3e7cbc19787e431c7474b8f52cb5197)), closes [#12](https://github.com/svange/danger-rose/issues/12)
* set up game CI/CD pipeline and PyInstaller builds ([07d37e9](https://github.com/svange/danger-rose/commit/07d37e98338ea4f965c02a79808af7199e3b6193))
* title screen and broken sprites BABY! It's coming to life! ([8a62dfa](https://github.com/svange/danger-rose/commit/8a62dfa680e64f00418de8c58c906fc238775371))
