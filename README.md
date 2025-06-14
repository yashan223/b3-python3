# BigBrotherBot (B3) - Python 3 Edition

![BigBrotherBot](https://github.com/BigBrotherBot/ArtWork/blob/master/layered-png/logo.png)

**Complete game server administration bot with Python 3 support and advanced security features**

## 🚀 What is B3?

BigBrotherBot (B3) is a comprehensive server administration package for online games. It automatically manages your server by monitoring player behavior, enforcing rules, and providing administrative tools through in-game commands.

## ✨ Key Features

### 🛡️ **Core Administration**
- **Automated moderation** - Warns, kicks, and bans disruptive players
- **Anti-spam protection** - Prevents chat flooding and spam
- **Team kill protection** - Automatically handles team killers
- **Language filtering** - Blocks offensive content with customizable word lists
- **Welcome system** - Greets players with custom messages

### 🌍 **Geolocation Features**
- **Country detection** - Shows player locations and flags
- **Geographic welcomes** - Location-based greeting messages
- **Location commands** - `!location` command to check player countries
- **Multi-provider support** - Uses multiple IP geolocation services

### 🔒 **Advanced Security**
- **VPN/Proxy blocker** - Automatically detects and blocks VPN/proxy users
- **Multi-API detection** - Uses multiple VPN detection services
- **Smart caching** - Reduces API calls with intelligent IP caching
- **Admin override** - Whitelist trusted players using VPNs

### 📊 **Statistics & Tracking**
- **XLRstats integration** - Detailed player statistics and rankings  
- **Skill tracking** - ELO-based skill rating system
- **Match history** - Comprehensive game statistics
- **Leaderboards** - Top player rankings and achievements

### 🎮 **Player Management**
- **Registration system** - Player account management
- **Admin levels** - Hierarchical permission system (0-100)
- **Temporary bans** - Time-based punishment system
- **Custom commands** - Create your own server commands
- **Ping monitoring** - Auto-kick high ping players

### 🔧 **Technical Features**
- **Python 3.8+ compatible** - Fully migrated from Python 2
- **Cross-platform** - Works on Windows, Linux, and macOS
- **Database support** - MySQL, PostgreSQL, SQLite
- **Plugin system** - 40+ built-in plugins, extensible architecture
- **Real-time monitoring** - Live game log parsing
- **RCON integration** - Direct server communication

## 🎯 Supported Games

**Call of Duty Series:**
- COD 1, 2, 4 (Modern Warfare), 5 (World at War)
- COD 6 (MW2), 7 (Black Ops), 8 (MW3)

**Battlefield Series:**
- Battlefield 3, 4, Bad Company 2, Hardline

**Urban Terror:**
- Urban Terror 4.1, 4.2, 4.3

**Other Games:**
- Counter-Strike: Global Offensive
- Medal of Honor (2010, Warfighter)
- Enemy Territory, Arma II/III, Insurgency
- And 20+ more games!

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Game server with RCON access
- Database (MySQL recommended)

### Installation
1. **Download B3:**
   ```bash
   git clone https://github.com/YourUsername/big-brother-bot.git
   cd big-brother-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure B3:**
   - Edit `b3/conf/b3.xml` with your server details
   - Update plugin configs in `b3/conf/`
   - Set database connection settings

4. **Run B3:**
   ```bash
   python b3_run.py
   ```

## 🎛️ Admin Commands

### Basic Commands
- `!kick <player>` - Kick a player
- `!ban <player>` - Ban a player  
- `!tempban <player> <duration>` - Temporary ban
- `!warn <player> <reason>` - Warn a player

### Information Commands
- `!leveltest <player>` - Check player admin level
- `!location <player>` - Show player's country
- `!stats <player>` - Show player statistics
- `!list` - List online players

### VPN Protection
- `!vpncheck <player>` - Check if player uses VPN
- `!vpnwhitelist <player>` - Allow VPN for trusted player
- `!vpnstats` - Show VPN blocker statistics

## 🔧 Configuration

### Main Config (`b3/conf/b3.xml`)
```xml
<configuration>
  <settings name="server">
    <set name="game">cod4x18</set>
    <set name="ip">127.0.0.1</set>
    <set name="port">28960</set>
    <set name="rcon_password">your_rcon_password</set>
  </settings>
  
  <plugins>
    <plugin name="admin" config="@conf/plugin_admin.ini"/>
    <plugin name="geolocation"/>
    <plugin name="vpnblocker" config="@b3/extplugins/conf/vpnblocker.ini"/>
    <!-- Add more plugins here -->
  </plugins>
</configuration>
```

### VPN Blocker Setup
Edit `b3/extplugins/conf/vpnblocker.ini`:
```ini
[settings]
enabled = True
action = kick
vpnapi_key = your_vpnapi_key
proxycheck_key = your_proxycheck_key
max_api_calls_per_minute = 30
```

## 🔌 Plugin System

B3 includes 40+ plugins:
- **admin** - Core admin commands
- **welcome** - Player greeting system  
- **spamcontrol** - Anti-spam protection
- **xlrstats** - Player statistics
- **geolocation** - Country detection
- **vpnblocker** - VPN/proxy protection
- **pingwatch** - Ping monitoring
- **tk** - Team kill management
- And many more!

## 🛠️ Development

### Python 3 Migration
This version has been fully migrated to Python 3.8+:
- All print statements converted to functions
- Fixed string/bytes handling
- Updated deprecated modules
- Modernized exception handling
- Fixed plugin loading system

### Creating Custom Plugins
```python
import b3.plugin

class MyPlugin(b3.plugin.Plugin):
    def onStartup(self):
        self.registerEvent('EVT_CLIENT_SAY', self.onSay)
    
    def onSay(self, event):
        # Handle player chat
        pass
```

## 📝 Recent Updates

- ✅ **Python 3.8+ compatibility** - Fully migrated from Python 2
- ✅ **VPN blocker plugin** - Advanced proxy/VPN detection  
- ✅ **Geolocation fixes** - Country detection now working
- ✅ **Plugin system fixes** - All 40+ plugins loading correctly
- ✅ **Database improvements** - Better error handling
- ✅ **Performance optimizations** - Faster startup and operation

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🏆 Hall of Fame

Thanks to all contributors who made B3 possible:
_[ThorN], [xlr8or], ttlogic, [Courgette], [Fenix], [Bakes], [spacepig], [Durzo], eire.32, [grosbedo], [Freelander], [82ndAB.Bravo17], [Just a baka], [Ozon]_ and many others!

---

**Ready to secure your game server? Install B3 today and experience professional-grade server administration!**

[ThorN]: https://github.com/six8
[xlr8or]: https://github.com/markweirath  
[Courgette]: https://github.com/thomasleveil
[Bakes]: https://github.com/j-baker
[spacepig]: https://github.com/spacepig
[Durzo]: https://github.com/durzo
[grosbedo]: https://github.com/grosbedo
[Freelander]: https://github.com/ozguruysal
[82ndAB.Bravo17]: https://github.com/82ndab-Bravo17
[Just a baka]: https://github.com/justabaka
[Fenix]: https://github.com/danielepantaleone
[Ozon]: https://github.com/ozon

[ThorN]: https://github.com/six8
[xlr8or]: https://github.com/markweirath
[Courgette]: https://github.com/thomasleveil
[Bakes]: https://github.com/j-baker
[spacepig]: https://github.com/spacepig
[Durzo]: https://github.com/durzo
[grosbedo]: https://github.com/grosbedo
[Freelander]: https://github.com/ozguruysal
[82ndAB.Bravo17]: https://github.com/82ndab-Bravo17
[Just a baka]: https://github.com/justabaka
[Fenix]: https://github.com/danielepantaleone
[Ozon]: https://github.com/ozon
