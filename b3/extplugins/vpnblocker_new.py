#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# VPN Blocker Plugin for BigBrotherBot(B3)
# Copyright (C) 2025
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

__author__ = 'B3 Community'
__version__ = '1.0.1'

import b3
import b3.plugin
import b3.events
import threading
import time
import json
import urllib.request
import urllib.parse
import urllib.error
import ipaddress
import re
from configparser import NoOptionError

class VpnblockerPlugin(b3.plugin.Plugin):
    """
    VPN Blocker Plugin for B3
    Detects and blocks VPN/Proxy connections using multiple detection methods
    """
    
    # Default settings
    _enabled = True
    _kick_on_vpn = True
    _ban_on_vpn = False
    _ban_duration = 7  # days
    _whitelist_level = 40  # admin level exempt from checks
    _check_timeout = 10  # seconds
    _cache_time = 3600  # 1 hour cache
    _max_retries = 3
    _log_detections = True
    _announce_kicks = True
    
    # API settings
    _use_proxycheck = True
    _proxycheck_api_key = ""
    _use_vpnapi = True
    _vpnapi_api_key = ""
    _use_ipqualityscore = False
    _ipqualityscore_api_key = ""
    
    # Cache for IP checks
    _ip_cache = {}
    _cache_lock = threading.Lock()
    
    # Known VPN/Proxy ranges (basic list)
    _known_vpn_ranges = []
    
    def __init__(self, console, config=None):
        """
        Object constructor.
        """
        b3.plugin.Plugin.__init__(self, console, config)
        
        # Register events
        self.registerEvent('EVT_CLIENT_CONNECT', self.onConnect)
        self.registerEvent('EVT_CLIENT_AUTH', self.onAuth)
        
    def onStartup(self):
        """
        Initialize plugin.
        """
        self.debug('VPN Blocker Plugin v%s starting up...' % __version__)
        
        # Load configuration
        self.loadConfig()
        
        # Load known VPN ranges
        self.loadVpnRanges()
        
        # Start cache cleanup thread
        cleanup_thread = threading.Thread(target=self._cleanupCache, daemon=True)
        cleanup_thread.start()
        
        self.info('VPN Blocker Plugin v%s started successfully' % __version__)
        
    def onLoadConfig(self):
        """
        Load plugin configuration.
        """
        self.loadConfig()
        
    def loadConfig(self, config=None):
        """
        Load configuration from file.
        """
        if not self.config:
            self.debug('No config available, using default values')
            return
            
        try:
            self._enabled = self.config.getboolean('settings', 'enabled')
        except (NoOptionError, ValueError, AttributeError):
            self.warning('Using default value for enabled: %s' % self._enabled)
            
        try:
            self._kick_on_vpn = self.config.getboolean('settings', 'kick_on_vpn')
        except (NoOptionError, ValueError, AttributeError):
            self.warning('Using default value for kick_on_vpn: %s' % self._kick_on_vpn)
            
        try:
            self._ban_on_vpn = self.config.getboolean('settings', 'ban_on_vpn')
        except (NoOptionError, ValueError, AttributeError):
            self.warning('Using default value for ban_on_vpn: %s' % self._ban_on_vpn)
            
        try:
            self._ban_duration = self.config.getint('settings', 'ban_duration')
        except (NoOptionError, ValueError, AttributeError):
            self.warning('Using default value for ban_duration: %s' % self._ban_duration)
            
        try:
            self._whitelist_level = self.config.getint('settings', 'whitelist_level')
        except (NoOptionError, ValueError, AttributeError):
            self.warning('Using default value for whitelist_level: %s' % self._whitelist_level)
            
        try:
            self._check_timeout = self.config.getint('settings', 'check_timeout')
        except (NoOptionError, ValueError, AttributeError):
            self.warning('Using default value for check_timeout: %s' % self._check_timeout)
            
        try:
            self._cache_time = self.config.getint('settings', 'cache_time')
        except (NoOptionError, ValueError, AttributeError):
            self.warning('Using default value for cache_time: %s' % self._cache_time)
            
        try:
            self._max_retries = self.config.getint('settings', 'max_retries')
        except (NoOptionError, ValueError, AttributeError):
            self.warning('Using default value for max_retries: %s' % self._max_retries)
            
        try:
            self._log_detections = self.config.getboolean('settings', 'log_detections')
        except (NoOptionError, ValueError, AttributeError):
            self.warning('Using default value for log_detections: %s' % self._log_detections)
            
        try:
            self._announce_kicks = self.config.getboolean('settings', 'announce_kicks')
        except (NoOptionError, ValueError, AttributeError):
            self.warning('Using default value for announce_kicks: %s' % self._announce_kicks)
            
        # API settings
        try:
            self._use_proxycheck = self.config.getboolean('apis', 'use_proxycheck')
        except (NoOptionError, ValueError, AttributeError):
            self.warning('Using default value for use_proxycheck: %s' % self._use_proxycheck)
            
        try:
            self._proxycheck_api_key = self.config.get('apis', 'proxycheck_api_key')
        except (NoOptionError, AttributeError):
            self._proxycheck_api_key = ""
            
        try:
            self._use_vpnapi = self.config.getboolean('apis', 'use_vpnapi')
        except (NoOptionError, ValueError, AttributeError):
            self.warning('Using default value for use_vpnapi: %s' % self._use_vpnapi)
            
        try:
            self._vpnapi_api_key = self.config.get('apis', 'vpnapi_api_key')
        except (NoOptionError, AttributeError):
            self._vpnapi_api_key = ""
            
        try:
            self._use_ipqualityscore = self.config.getboolean('apis', 'use_ipqualityscore')
        except (NoOptionError, ValueError, AttributeError):
            self.warning('Using default value for use_ipqualityscore: %s' % self._use_ipqualityscore)
            
        try:
            self._ipqualityscore_api_key = self.config.get('apis', 'ipqualityscore_api_key')
        except (NoOptionError, AttributeError):
            self._ipqualityscore_api_key = ""
            
        self.debug('Configuration loaded successfully')
        
    def loadVpnRanges(self):
        """
        Load known VPN/Proxy IP ranges.
        """
        # Basic list of known VPN providers' IP ranges
        # In a production environment, this should be loaded from a file or API
        self._known_vpn_ranges = [
            # Common VPN provider ranges (examples)
            # Add more ranges as needed
        ]
        
        self.debug('Loaded %d VPN IP ranges' % len(self._known_vpn_ranges))
        
    def onConnect(self, event):
        """
        Handle client connect event.
        """
        if not self._enabled:
            return
            
        client = event.client
        if not client or not client.ip:
            return
            
        # Skip check for whitelisted players
        if client.maxLevel >= self._whitelist_level:
            self.debug('Skipping VPN check for whitelisted player: %s (level %d)' % (client.name, client.maxLevel))
            return
            
        # Check IP in separate thread to avoid blocking
        check_thread = threading.Thread(target=self._checkClientIP, args=(client,), daemon=True)
        check_thread.start()
        
    def onAuth(self, event):
        """
        Handle client authentication event.
        """
        # Additional check on auth if needed
        pass
        
    def _checkClientIP(self, client):
        """
        Check if client IP is VPN/Proxy.
        """
        try:
            ip = client.ip
            if not ip or ip == '0.0.0.0':
                return
                
            self.debug('Checking IP %s for client %s' % (ip, client.name))
            
            # Check cache first
            cached_result = self._getCachedResult(ip)
            if cached_result is not None:
                self.debug('Using cached result for IP %s: %s' % (ip, cached_result))
                if cached_result:
                    self._handleVpnDetection(client, ip, "Cached result")
                return
                
            # Check against known ranges
            if self._checkKnownRanges(ip):
                self._cacheResult(ip, True)
                self._handleVpnDetection(client, ip, "Known VPN range")
                return
                
            # Check using APIs
            is_vpn = False
            detection_method = ""
            
            if self._use_proxycheck:
                result = self._checkProxyCheck(ip)
                if result:
                    is_vpn = True
                    detection_method = "ProxyCheck.io"
                    
            if not is_vpn and self._use_vpnapi:
                result = self._checkVpnAPI(ip)
                if result:
                    is_vpn = True
                    detection_method = "VPN-API.io"
                    
            if not is_vpn and self._use_ipqualityscore:
                result = self._checkIPQualityScore(ip)
                if result:
                    is_vpn = True
                    detection_method = "IPQualityScore"
                    
            # Cache result
            self._cacheResult(ip, is_vpn)
            
            if is_vpn:
                self._handleVpnDetection(client, ip, detection_method)
            else:
                self.debug('IP %s is clean' % ip)
                
        except Exception as e:
            self.error('Error checking IP %s: %s' % (client.ip, e))
            
    def _checkKnownRanges(self, ip):
        """
        Check IP against known VPN ranges.
        """
        try:
            ip_addr = ipaddress.ip_address(ip)
            for network in self._known_vpn_ranges:
                if ip_addr in network:
                    return True
        except Exception as e:
            self.debug('Error checking known ranges for %s: %s' % (ip, e))
        return False
        
    def _checkProxyCheck(self, ip):
        """
        Check IP using ProxyCheck.io API.
        """
        try:
            if self._proxycheck_api_key:
                url = f"http://proxycheck.io/v2/{ip}?key={self._proxycheck_api_key}&vpn=1&asn=1"
            else:
                url = f"http://proxycheck.io/v2/{ip}?vpn=1&asn=1"
                
            response = self._makeAPIRequest(url)
            if response:
                data = json.loads(response)
                if ip in data and 'proxy' in data[ip]:
                    return data[ip]['proxy'] == 'yes'
        except Exception as e:
            self.debug('ProxyCheck API error for %s: %s' % (ip, e))
        return False
        
    def _checkVpnAPI(self, ip):
        """
        Check IP using VPN-API.io.
        """
        try:
            if self._vpnapi_api_key:
                url = f"https://vpnapi.io/api/{ip}?key={self._vpnapi_api_key}"
            else:
                url = f"https://vpnapi.io/api/{ip}"
                
            response = self._makeAPIRequest(url)
            if response:
                data = json.loads(response)
                return data.get('security', {}).get('vpn', False) or data.get('security', {}).get('proxy', False)
        except Exception as e:
            self.debug('VPN-API error for %s: %s' % (ip, e))
        return False
        
    def _checkIPQualityScore(self, ip):
        """
        Check IP using IPQualityScore API.
        """
        try:
            if not self._ipqualityscore_api_key:
                return False
                
            url = f"https://ipqualityscore.com/api/json/ip/{self._ipqualityscore_api_key}/{ip}?strictness=1"
            response = self._makeAPIRequest(url)
            if response:
                data = json.loads(response)
                return data.get('vpn', False) or data.get('proxy', False) or data.get('tor', False)
        except Exception as e:
            self.debug('IPQualityScore API error for %s: %s' % (ip, e))
        return False
        
    def _makeAPIRequest(self, url):
        """
        Make HTTP API request with timeout and retries.
        """
        for attempt in range(self._max_retries):
            try:
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'B3-VPNBlocker/1.0')
                
                with urllib.request.urlopen(req, timeout=self._check_timeout) as response:
                    return response.read().decode('utf-8')
                    
            except Exception as e:
                self.debug('API request attempt %d failed: %s' % (attempt + 1, e))
                if attempt < self._max_retries - 1:
                    time.sleep(1)  # Wait before retry
                    
        return None
        
    def _getCachedResult(self, ip):
        """
        Get cached result for IP.
        """
        with self._cache_lock:
            if ip in self._ip_cache:
                result, timestamp = self._ip_cache[ip]
                if time.time() - timestamp < self._cache_time:
                    return result
                else:
                    del self._ip_cache[ip]
        return None
        
    def _cacheResult(self, ip, is_vpn):
        """
        Cache result for IP.
        """
        with self._cache_lock:
            self._ip_cache[ip] = (is_vpn, time.time())
            
    def _cleanupCache(self):
        """
        Cleanup expired cache entries.
        """
        while True:
            try:
                time.sleep(300)  # Check every 5 minutes
                current_time = time.time()
                
                with self._cache_lock:
                    expired_ips = []
                    for ip, (result, timestamp) in self._ip_cache.items():
                        if current_time - timestamp >= self._cache_time:
                            expired_ips.append(ip)
                            
                    for ip in expired_ips:
                        del self._ip_cache[ip]
                        
                    if expired_ips:
                        self.debug('Cleaned up %d expired cache entries' % len(expired_ips))
                        
            except Exception as e:
                self.error('Cache cleanup error: %s' % e)
                
    def _handleVpnDetection(self, client, ip, method):
        """
        Handle VPN detection.
        """
        message = "VPN/Proxy detected for %s (%s) via %s" % (client.name, ip, method)
        
        if self._log_detections:
            self.info(message)
            
        # Take action
        if self._ban_on_vpn:
            reason = "VPN/Proxy connection detected"
            if self._announce_kicks:
                self.console.say("^1%s ^7was banned for using VPN/Proxy" % client.name)
            client.tempban(reason, None, self._ban_duration * 24 * 60)  # Convert days to minutes
            
        elif self._kick_on_vpn:
            reason = "VPN/Proxy connections are not allowed"
            if self._announce_kicks:
                self.console.say("^1%s ^7was kicked for using VPN/Proxy" % client.name)
            client.kick(reason)
            
    # Admin commands
    def cmd_vpncheck(self, data, client, cmd=None):
        """
        <player> - Check if a player is using VPN/Proxy
        """
        if not data:
            client.message("^7Usage: !vpncheck <player>")
            return
            
        target = self._adminPlugin.findClientPrompt(data, client)
        if not target:
            return
            
        if not target.ip or target.ip == '0.0.0.0':
            client.message("^7Cannot check player %s: no IP available" % target.name)
            return
            
        client.message("^7Checking %s (%s)..." % (target.name, target.ip))
        
        # Check in separate thread
        def check_and_report():
            try:
                # Force fresh check (bypass cache)
                is_vpn = False
                methods = []
                
                if self._checkKnownRanges(target.ip):
                    is_vpn = True
                    methods.append("Known range")
                    
                if self._use_proxycheck and self._checkProxyCheck(target.ip):
                    is_vpn = True
                    methods.append("ProxyCheck")
                    
                if self._use_vpnapi and self._checkVpnAPI(target.ip):
                    is_vpn = True
                    methods.append("VPN-API")
                    
                if self._use_ipqualityscore and self._checkIPQualityScore(target.ip):
                    is_vpn = True
                    methods.append("IPQualityScore")
                    
                if is_vpn:
                    client.message("^1VPN/Proxy detected for %s via: %s" % (target.name, ", ".join(methods)))
                else:
                    client.message("^2No VPN/Proxy detected for %s" % target.name)
                    
            except Exception as e:
                client.message("^1Error checking %s: %s" % (target.name, e))
                
        check_thread = threading.Thread(target=check_and_report, daemon=True)
        check_thread.start()
        
    def cmd_vpnstatus(self, data, client, cmd=None):
        """
        Show VPN blocker status
        """
        status = "^7VPN Blocker Status:\n"
        status += "^7Enabled: ^2%s\n" % ("Yes" if self._enabled else "No")
        status += "^7Kick on VPN: ^2%s\n" % ("Yes" if self._kick_on_vpn else "No")
        status += "^7Ban on VPN: ^2%s ^7(%d days)\n" % (("Yes" if self._ban_on_vpn else "No"), self._ban_duration)
        status += "^7APIs: "
        
        apis = []
        if self._use_proxycheck:
            apis.append("ProxyCheck" + (" (with key)" if self._proxycheck_api_key else " (free)"))
        if self._use_vpnapi:
            apis.append("VPN-API" + (" (with key)" if self._vpnapi_api_key else " (free)"))
        if self._use_ipqualityscore:
            apis.append("IPQualityScore" + (" (with key)" if self._ipqualityscore_api_key else " (disabled)"))
            
        status += "^2%s\n" % (", ".join(apis) if apis else "None")
        status += "^7Cache entries: ^2%d" % len(self._ip_cache)
        
        client.message(status)
        
    def cmd_vpnclear(self, data, client, cmd=None):
        """
        Clear VPN cache
        """
        with self._cache_lock:
            cache_size = len(self._ip_cache)
            self._ip_cache.clear()
            
        client.message("^7Cleared ^2%d ^7VPN cache entries" % cache_size)
