from useragents import search_strings
import re
import logging
import traceback


class Middleware(object):
    @staticmethod
    def process_request(request):
        """Adds a "mobile" attribute to the request which is True or False
           depending on whether the request should be considered to come from a
           small-screen device such as a phone or a PDA"""

        request.mobile = False

        if 'HTTP_X_OPERAMINI_FEATURES' in request.META:
            #Then it's running opera mini. 'Nuff said.
            #Reference from:
            # http://dev.opera.com/articles/view/opera-mini-request-headers/
            request.mobile = True

        if not request.mobile and 'HTTP_ACCEPT' in request.META:
            s = request.META["HTTP_ACCEPT"].lower()
            if 'application/vnd.wap.xhtml+xml' in s:
                # Then it's a wap browser
                request.mobile = True

        request.devices = {}
        if 'HTTP_USER_AGENT' in request.META:
            # This takes the most processing. Surprisingly enough, when I
            # Experimented on my own machine, this was the most efficient
            # algorithm. Certainly more so than regexes.
            # Also, Caching didn't help much, with real-world caches.
            s = request.META["HTTP_USER_AGENT"].lower()
            if not request.mobile:
                for ua in search_strings:
                    if ua in s:
                        request.mobile = True
                        break

            device = {}
            facebook_app = False
            # also interested if it's a iPhone or Andriod,
            # e.g. something common
            try:
                # TODO: this really needs a lot of work, for now,
                # it should get the most common phone OS
                #
                # Check if we have entered via facebook app, rather than a
                # mobile browser
                found_device = None

                if s.find("iphone") > -1:
                    found_device = "iphone"
                    try:
                        device['iphone'] = "iphone " +\
                                re.search("os (\d_\d)", s).groups(0)[0]
                    except:
                        device['iphone'] = "iphone " +\
                                re.search("version/(\d\.\d)", s).groups(0)[0]

                elif s.find("ipad") > -1:
                    found_device = "ipad"
                    device['ipad'] = "ipad " +\
                            re.search("os (\d_\d)", s).groups(0)[0]

                elif s.find("ipod") > -1:
                    found_device = "ipod"
                    device['ipod'] = "ipod"

                elif s.find("android") > -1:
                    found_device = "android"
                    try:
                        device['android'] = "android " +\
                                re.search("android (\d\.\d)",
                                        s).groups(0)[0].translate(None, '.')
                    except:
                        try:
                            device['android'] = "android " +\
                                    re.search(r"rv:(\d+\.\d+)",
                                        s).groups(0)[0].translate(None, '.')
                        except:
                            device['android'] = 'android %s' % s

                elif s.find("symbianos/") > -1:
                    found_device = "nokia"
                    device['nokia'] = "symbian " +\
                            re.search("symbianos/(\d\.\d)", s).groups(0)[0]

                elif s.find("symbian/") > -1:
                    found_device = "nokia"
                    device['nokia'] = "symbian " +\
                            re.search("symbian/(\d)", s).groups(0)[0]

                elif (s.find("windows phone os 7") > -1 or
                      s.find("zunewp7") > -1):
                    found_device = "winphone7"
                    device[found_device] = found_device

                elif (s.find("windows phone 8") > -1):
                    found_device = "winphone8"
                    device[found_device] = found_device

                elif s.find("nokia") > -1:
                    found_device = "nokia"
                    try:
                        device['nokia'] = "nokia " +\
                                re.search("nokia([\sa-z0-9]+)", s).groups(0)[0]
                    except:
                        device['nokia'] = "nokia series-" +\
                                re.search("nokia/series-([\sa-z0-9]+)",
                                        s).groups(0)[0]

                elif s.find("blackberry") > -1:
                    found_device = "blackberry"
                    try:
                        device[found_device] = found_device + " " +\
                                re.search("blackberry(\d+)", s).groups(0)[0]
                    except:
                        try:
                            device[found_device] = found_device + " " +\
                                re.search("blackberry/(\d+).(/d+).(/d+)",
                                        s).groups(0)[0]
                        except:
                            device[found_device] = found_device

                elif s.find("hp ipaq-") > -1:
                    found_device = "hp"
                    device[found_device] = found_device + " " +\
                            re.search("hp ipaq ([a-z0-9]+)", s).groups(0)[0]

                elif s.find("samsung") > -1:
                    found_device = "samsung"
                    device[found_device] = found_device + " " +\
                            re.search("samsung-([a-z0-9\-]+)", s).groups(0)[0]

                elif s.find("sec-") > -1:
                    found_device = "samsung"
                    device[found_device] = found_device + " " +\
                            re.search("sec-([a-z0-9\-]+)", s).groups(0)[0]

                elif s.find("sie-") > -1:
                    found_device = "siemens"
                    device[found_device] = found_device + " " +\
                            re.search("sie-([a-z0-9]+)", s).groups(0)[0]

                elif s.find("sch-a950") > -1:
                    found_device = "samsung"
                    device[found_device] = found_device + " sch-a950"

                elif s.find("htc") > -1:
                    found_device = "htc"
                    device[found_device] = found_device

                elif s.find("sonyericsson") > -1:
                    found_device = "sonyericsson"
                    try:
                        device[found_device] = found_device + " " +\
                                re.search("sonyericsson ([a-z0-9\-]+)",
                                        s).groups(0)[0]
                    except:
                        device[found_device] = found_device + " " +\
                                re.search("sonyericsson([a-z0-9\-]+)",
                                        s).groups(0)[0]

                elif s.find("palm") > -1:
                    found_device = "palm"
                    device['palm'] = "palm"

                elif s.find("iemobile") > -1:
                    found_device = "winmo"
                    device['winmo'] = "winmo"

                elif s.find("mot-") > -1:
                    found_device = "motorola"
                    device[found_device] = found_device
                    try:
                        device[found_device] = found_device + " " +\
                                re.search("mot-([a-z0-9\-]+)", s).groups(0)[0]
                    except:
                        pass

                if s.find("fbdv") > -1:
                    facebook_app = True

            except Exception, e:
                logger = logging.getLogger(__name__)
                logger.error(e)
                logger.error(traceback.format_exc())
                logger.debug(s)

            if device == {} and request.mobile:
                # capture unknown devices for later analysis
                device['unknown'] = "mobile :" + s

            if not request.mobile:
                if s.find("msie") > -1:
                    try:
                        device['ie'] = "ie " +\
                                re.search("msie (\d+\.\d+)", s).groups(0)[0]
                    except:
                        pass

                else:
                    device['desktop'] = "desktop :" + s

            # spits out device names for CSS targeting, to be applied
            # to <html> or <body>.
            request.devices = device.values()
            request.is_facebook = facebook_app

        return None


def detect_mobile(view):
    """View Decorator that adds a "mobile" attribute to the request which is
       True or False depending on whether the request should be considered
       to come from a small-screen device such as a phone or a PDA"""

    def detected(request, *args, **kwargs):
        Middleware.process_request(request)
        return view(request, *args, **kwargs)

    detected.__doc__ = (view.__doc__ or '') + "\n"
    detected.__doc__ += "[Wrapped by detect_mobile which detects if the"
    detected.__doc__ += " request is from a phone]"

    return detected


__all__ = ['Middleware', 'detect_mobile']
#
