# VPN Blocker Plugin for BigBrotherBot (B3)

A comprehensive VPN/Proxy detection and blocking plugin for B3 that uses multiple detection methods and APIs to identify and handle VPN/Proxy connections.

## Features

### Multi-Method Detection
- **Known IP Ranges**: Checks against known VPN provider IP ranges
- **ProxyCheck.io API**: Real-time proxy/VPN detection (free tier available)
- **VPN-API.io**: Comprehensive VPN detection service (free tier available)
- **IPQualityScore**: Advanced threat detection (paid service)

### Smart Caching
- Results are cached to reduce API calls and improve performance
- Configurable cache duration (default: 1 hour)
- Automatic cache cleanup to prevent memory bloat

### Flexible Actions
- **Kick**: Remove players using VPN/Proxy (default)
- **Temporary Ban**: Ban players for a configurable duration
- **Whitelist**: Exempt admins and trusted players from checks

### Admin Commands
- `!vpncheck <player>` - Manually check if a player is using VPN/Proxy
- `!vpnstatus` - Show plugin status and statistics
- `!vpnclear` - Clear the detection cache

## Installation

1. Copy `vpnblocker.py` to `b3/extplugins/`
2. Copy `vpnblocker.ini` to `b3/extplugins/conf/`
3. Add the plugin to your `b3.xml`:

```xml
<plugin name="vpnblocker" config="@b3/extplugins/conf/vpnblocker.ini"/>
```

4. Restart B3

## Configuration

### Basic Settings

```ini
[settings]
# Enable/disable the plugin
enabled: yes

# Action to take when VPN is detected
kick_on_vpn: yes
ban_on_vpn: no

# Ban duration in days (if ban_on_vpn is enabled)
ban_duration: 7

# Minimum level to be exempt from VPN checks
whitelist_level: 40

# API request timeout in seconds
check_timeout: 10

# Cache results for this many seconds
cache_time: 3600

# Log VPN detections to console
log_detections: yes

# Announce kicks/bans to all players
announce_kicks: yes
```

### API Configuration

```ini
[apis]
# ProxyCheck.io API (Free tier: 1000 queries/day)
use_proxycheck: yes
proxycheck_api_key: your_api_key_here

# VPN-API.io (Free tier: 1000 queries/month)
use_vpnapi: yes
vpnapi_api_key: your_api_key_here

# IPQualityScore (Paid service)
use_ipqualityscore: no
ipqualityscore_api_key: your_api_key_here
```

## API Setup

### ProxyCheck.io (Recommended)
1. Visit https://proxycheck.io/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add it to the configuration file
5. Free tier provides 1000 queries per day

### VPN-API.io
1. Visit https://vpnapi.io/
2. Sign up for a free account
3. Get your API key
4. Add it to the configuration file
5. Free tier provides 1000 queries per month

### IPQualityScore (Advanced)
1. Visit https://www.ipqualityscore.com/
2. Sign up for an account (paid service)
3. Get your API key
4. Enable in configuration and add API key

## How It Works

1. **Player Connects**: When a player connects, the plugin checks their IP address
2. **Whitelist Check**: Admins and trusted players (configurable level) are exempt
3. **Cache Check**: Previously checked IPs are served from cache for performance
4. **Range Check**: IP is checked against known VPN provider ranges
5. **API Checks**: If enabled, external APIs are queried for VPN detection
6. **Action**: If VPN is detected, player is kicked or banned based on configuration
7. **Logging**: Detection events are logged and optionally announced

## Commands

### !vpncheck <player>
Manually check if a player is using a VPN or proxy.
- **Permission**: Admin (level 40)
- **Example**: `!vpncheck badplayer`

### !vpnstatus
Show plugin status, enabled APIs, and cache statistics.
- **Permission**: Admin (level 40)
- **Example**: `!vpnstatus`

### !vpnclear
Clear the VPN detection cache (forces fresh checks).
- **Permission**: Full Admin (level 60)
- **Example**: `!vpnclear`

## Performance Notes

- **Caching**: Results are cached to minimize API usage
- **Threading**: API checks run in background threads to avoid blocking
- **Timeouts**: Configurable timeouts prevent hanging on slow APIs
- **Retries**: Failed API requests are retried with exponential backoff

## Privacy Considerations

- Only IP addresses are sent to external APIs
- No personal information is transmitted
- Consider your privacy policy and local laws
- Some APIs may log requests

## Troubleshooting

### Plugin Not Loading
- Check B3 logs for error messages
- Verify file paths in configuration
- Ensure Python dependencies are met

### False Positives
- Some legitimate users may use VPNs
- Consider adjusting API sensitivity settings
- Use whitelist feature for trusted players
- Monitor logs for patterns

### API Issues
- Check API key validity
- Verify network connectivity
- Monitor API quotas and limits
- Review API documentation for status codes

## Support

For support, issues, or feature requests:
1. Check B3 community forums
2. Review plugin logs for error messages
3. Test with debug logging enabled

## License

This plugin is released under the same license as BigBrotherBot (GPL v2).

## Version History

- **v1.0.0**: Initial release with multi-API support and caching
