'''
zettahost urlresolver plugin
(C) 2015 by Bit
based on 180upload by anilkuj

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
from urlresolver import common
from lib import jsunpack
import re, urllib2, os, xbmcgui, xbmc


net = Net()

#SET ERROR_LOGO# THANKS TO VOINAGE, BSTRDMKR, ELDORADO
error_logo = os.path.join(common.addon_path, 'resources', 'images', 'redx.png')

class ZettahostResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "zettahost"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    
    def get_media_url(self, host, media_id):
        web_url = 'http://zettahost.tv/embed-%s-720x480.html' % media_id
       
        try:
            html = net.http_GET(web_url).content
            # Check for file not found
            if re.search('File Not Found', html):
                common.addon.log_error(self.name + ' - File Not Found')
                xbmc.executebuiltin('XBMC.Notification([B][COLOR white]zettahost[/COLOR][/B],[COLOR red]File has been deleted[/COLOR],8000,'+error_logo+')')
                return self.unresolvable(code=1, msg='File Not Found') 

            #check for the packed data filename and extract it if
            #we do

            packed = re.search('id="player_code".*?(eval.*?\)\)\))', html,re.DOTALL)
            if packed:
                js = jsunpack.unpack(packed.group(1))
                #we now just have to extract the file: part
                link = re.search('file:"(.+?)"', js.replace('\\',''))
                if link:
                    return link.group(1)
            #doesn't seem to have the usual format
            raise Exception('Unable to resolve zettahost Link')            

        except urllib2.URLError, e:
            common.addon.log_error(self.name + ': got http error %d fetching %s' %
                                   (e.code, web_url))
            common.addon.show_small_popup('Error','Http error: '+str(e), 5000, error_logo)
            return self.unresolvable(code=3, msg=e)
        except Exception, e:
            common.addon.log_error('**** zettahost Error occured: %s' % e)
            common.addon.show_small_popup(title='[B][COLOR white]zettahost[/COLOR][/B]', msg='[COLOR red]%s[/COLOR]' % e, delay=5000, image=error_logo)
            return self.unresolvable(code=0, msg=e)

        
    def get_url(self, host, media_id):
        return 'http://www.zettahost.tv/%s' % media_id 
        
        
    def get_host_and_id(self, url):
        r = re.search('http://(.+?)/embed-([\w]+)-', url)
        if r:
            return r.groups()
        else:
            r = re.search('//(.+?)/([\w]+)', url)
            if r:
                return r.groups()
            else:
                return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return (re.match('http://(www.)?zettahost.tv/' +
                         '[0-9A-Za-z]+', url) or
                         'zettahost' in host)
