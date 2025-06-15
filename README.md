# BigBrotherBot (B3) - COD4X18 Edition

**Streamlined game server administration bot for Call of Duty 4X servers**

## 🎮 What is B3?

BigBrotherBot (B3) is a server administration tool that automatically manages your COD4X18 server by monitoring player behavior, enforcing rules, and providing administrative commands.

**⚠️ This version is specifically optimized and tested with COD4X18 servers only.**

## ✨ Core Features

- **Automated moderation** - Warns, kicks, and bans disruptive players
- **Anti-spam protection** - Prevents chat flooding
- **Team kill management** - Handles team killers automatically  
- **Language filtering** - Blocks offensive content
- **Player statistics** - XLRstats integration with skill tracking
- **Geolocation detection** - Shows player countries
- **VPN/Proxy blocking** - Automatically blocks VPN users
- **Custom commands** - Create server-specific commands
- **Admin system** - Hierarchical permission levels (0-100)
- **RCON integration** - Direct server communication

## 🎯 Supported Games

**Call of Duty Series:**
- COD 1, 2, 4 (Modern Warfare), 5 (World at War)
- COD 6 (MW2), 7 (Black Ops), 8 (MW3)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL database
- COD4X18 server with RCON enabled

### Installation

**Windows:**
```cmd
install_dependencies.bat
```

**Linux:**
```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### Configuration
1. Edit `b3/conf/b3.xml`:
   - Set your server IP, port, and RCON password
   - Configure database connection
   - Set game log path

2. **Run B3:**
   ```bash
   python b3_run.py
   ```

## 🎛️ Essential Commands

- `!kick <player>` - Kick a player
- `!ban <player>` - Ban a player  
- `!tempban <player> <duration>` - Temporary ban
- `!warn <player> <reason>` - Warn a player
- `!location <player>` - Show player's country
- `!stats <player>` - Show player statistics
- `!b3` - Show B3 version and status

## ⚙️ Included Plugins

**Core Plugins (12):**
- **admin** - Basic admin commands
- **welcome** - Player greeting system
- **spamcontrol** - Anti-spam protection
- **stats** - Player statistics
- **xlrstats** - Advanced stats with skill rating
- **location** - Geolocation services
- **geowelcome** - Location-based welcomes
- **customcommands** - Custom server commands
- **pingwatch** - Ping monitoring
- **adv** - Server advertisements
- **vpnblocker** - VPN/proxy detection
- **publist** - Server listing integration
## 🔧 Basic Configuration

Edit `b3/conf/b3.xml` with your COD4X18 server details:
```xml
<settings name="server">
  <set name="rcon_password">your_rcon_password</set>
  <set name="port">28960</set>
  <set name="public_ip">your_server_ip</set>
  <set name="game_log">path/to/games_mp.log</set>
</settings>

<settings name="b3">
  <set name="parser">cod4x18</set>
  <set name="database">mysql://user:pass@localhost/b3_db</set>
</settings>
```

## � Requirements

- **Python 3.8+**
- **MySQL Database**
- **COD4X18 Server**
- **RCON Access**

## ⚠️ Important Notes

- **This version is optimized and tested only with COD4X18 servers**
- **Python 3.8+ required** - Fully migrated from Python 2
- **Streamlined build** - Only essential plugins included
- **Production ready** - All major bugs fixed

---

**Ready to manage your COD4X18 server like a pro!** 🎮
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
