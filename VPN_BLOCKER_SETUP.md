# VPN Blocker Plugin - Quick Setup Guide

## Overview
The VPN Blocker Plugin for BigBrotherBot (B3) detects and blocks players using VPN/Proxy connections. It supports multiple detection methods and APIs for comprehensive coverage.

## Features
- **Multi-API Support**: ProxyCheck.io, VPN-API.io, IPQualityScore
- **Smart Caching**: Reduces API calls and improves performance
- **Flexible Actions**: Kick or ban players using VPN/Proxy
- **Admin Commands**: Manual checking and management
- **Whitelist Support**: Exempt trusted players and admins

## Installation
1. The plugin is already installed in `b3/extplugins/vpnblocker.py`
2. Configuration is in `b3/extplugins/conf/vpnblocker.ini`
3. Plugin is enabled in `b3/conf/b3.xml`

## Configuration
Edit `b3/extplugins/conf/vpnblocker.ini`:

### Basic Settings
```ini
[settings]
enabled: yes                    # Enable/disable the plugin
kick_on_vpn: yes               # Kick players using VPN/Proxy
ban_on_vpn: no                 # Ban instead of kick (optional)
ban_duration: 7                # Ban duration in days
whitelist_level: 40            # Admin level exempt from checks
check_timeout: 10              # API request timeout (seconds)
cache_time: 3600              # Cache duration (seconds)
max_retries: 3                # API request retries
log_detections: yes           # Log detections to console
announce_kicks: yes           # Announce kicks to all players
```

### API Configuration
```ini
[apis]
# ProxyCheck.io (Free tier: 100 queries/day)
use_proxycheck: yes
proxycheck_api_key:           # Optional API key for more queries

# VPN-API.io (Free tier: 1000 queries/month)
use_vpnapi: yes
vpnapi_api_key:               # Optional API key for more queries

# IPQualityScore (Paid service)
use_ipqualityscore: no
ipqualityscore_api_key:       # Required API key
```

## API Keys (Optional but Recommended)
1. **ProxyCheck.io**: Visit https://proxycheck.io/ to get free API key
2. **VPN-API.io**: Visit https://vpnapi.io/ to get free API key  
3. **IPQualityScore**: Visit https://www.ipqualityscore.com/ for paid service

## Admin Commands
- `!vpncheck <player>` - Check if a player is using VPN/Proxy
- `!vpnstatus` - Show plugin status and statistics
- `!vpnclear` - Clear the VPN detection cache

## Testing
Run the test script to verify the plugin works:
```bash
python test_vpn_blocker.py
```

## How It Works
1. **On Player Connect**: Plugin checks the player's IP address
2. **Cache Check**: First checks if IP is already cached
3. **Known Ranges**: Checks against known VPN IP ranges
4. **API Checks**: Queries external APIs if needed
5. **Action**: Kicks or bans player if VPN/Proxy detected
6. **Whitelist**: Admins and trusted players are exempt

## Troubleshooting
- Check B3 logs for any error messages
- Verify API keys are correct if using paid services
- Ensure internet connection for API queries
- Use `!vpnstatus` command to check plugin status

## Performance Notes
- Results are cached to minimize API calls
- Free API tiers have daily/monthly limits
- Plugin runs checks in background threads
- Cache cleanup runs automatically every 5 minutes

## Customization
The plugin can be extended with:
- Additional API providers
- Custom VPN IP range lists
- Different actions (warnings, temporary restrictions)
- Custom messages and notifications

## Support
- Plugin version: 1.0.1
- Compatible with Python 3.8+
- Tested with B3 v1.10+
- For issues, check B3 logs and plugin configuration
