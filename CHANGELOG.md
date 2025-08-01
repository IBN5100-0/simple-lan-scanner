# Changelog

All notable changes to Simple LAN Scanner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-01

### Added
- Online-only filtering in both CLI and GUI interfaces
- Search functionality for filtering devices by MAC, IP, hostname, or manufacturer
- Context menu in GUI for copying device information
- Comprehensive test suite with 108 tests
- Full documentation for GitHub
- Scan Once button in GUI toolbar
- Device count display showing online status
- Advanced settings dialog with tabbed interface

### Fixed
- GUI online filter initialization and scoping issues
- Test failures due to string format changes
- Persistence functionality for device data
- Git history cleaned of accidentally committed device scan files

### Changed
- Updated from beta to stable release
- Improved device display format with table-like structure
- Enhanced CLI output with color-coded online status
- Standardized timestamp handling across the application

### Security
- Added .gitignore entries to prevent committing sensitive device data
- Removed accidentally committed device scan files from git history

## [0.2.0-beta] - 2025-07-31

### Added
- Modern GUI with professional interface
- Persistent device tracking
- JSON and CSV export functionality
- Automatic network detection
- Manufacturer identification via OUI database
- Continuous monitoring mode

### Changed
- Refactored core architecture
- Improved CLI interface with Click framework
- Enhanced error handling

## [0.1.0-alpha] - 2025-07-30

### Added
- Initial release
- Basic network scanning with nmap
- Simple CLI interface
- Device discovery functionality

[1.0.0]: https://github.com/IBN5100-0/simple-lan-scanner/releases/tag/v1.0.0
[0.2.0-beta]: https://github.com/IBN5100-0/simple-lan-scanner/releases/tag/v0.2.0-beta
[0.1.0-alpha]: https://github.com/IBN5100-0/simple-lan-scanner/releases/tag/v0.1.0-alpha