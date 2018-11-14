#from collections import defaultdict
#import urllib
#from html.parser import HTMLParser
#import astropy.coordinates as coord
#import astropy.units as u


class Source:
    """Contains the information of a radio source available in VLBI catalogs for
    calibrators
    """
    self.name = None
    self.oldname = None
    self.coordinates = None
    self.images = []
    self.radplots = []
    #self.nmes = None # To be implemented

    def __init__(self, name, oldname, coordinates):
        """Initialize a new source with a specific name (J2000) and its coordinates.
        Input
        -----
        - name : str
                Name of the source as povided in the J2000 catalog (e.g. J2045+5049)
        - oldname : str
                Name of the source as povided in the B1950 catalog (e.g. 2044+504)
        - coordinates : astropy.coordinates
                Coordinates of the source as provided by the astropy.coordinates package.
        """
        self.name = name.upper()
        self.oldname = oldname.upper()
        self.coordinates = coordinates
        # Search if it is available in catalogs
        self.images = defaultdict(list)
        self.radplots = defaultdict(list)
        image_vsop = get_source_in_vsop5GHz('image')
        if image_vsop is not None:
            self.images['C'] = [image_vsop]
        radplot_vsop = get_source_in_vsop5GHz('radplot')
        if radplot_vsop is not None:
            self.radplots['C'] = [radplot_vsop]
        rfc_images, rfc_radplots = get_source_in_rfc()
        for aband in rfc_images:
            self.images[aband].append(rfc_images[aband])
        for aband in rfc_radplots:
            self.radplots[aband].append(rfc_radplots[aband])



    def get_source_in_vsop5GHz(self, type_plot):
        """Get the images of the source available in the VSOP 5-GHz catalog:
                http://www.jive.nl/svlbi/vlbapls/index.htm
        There are two types of images available: the actual image of the source or the
        correlated flux density versus the projected baseline length plot (radplot).

        Inputs
        ------
        - type_plot : str
            Can take only two possible values:
                image - will take the image of the source at 5 GHz.
                radplot - will take the plot of the correlated flux density versus the projected baseline length.
        
        Outputs
        -------
        - url_to_image : str
            Returns the url where the requested image is located (usually is a gif file).
        """
        possible_url = 'http://www.jive.nl/svlbi/vlbapls/{}.htm'.format(self.name)
        if website_exists(possible_url):
            if type_plot == 'image':
                return 'http://www.jive.nl/svlbi/vlbapls/img/{}MAP.color.gif'.format(self.oldname)
            elif type_plot == 'radplot':
                return 'http://www.jive.nl/svlbi/vlbapls/img/{}MAP.radplot.gif'.format(self.oldname)
            else:
                raise ValueError('Only "image" or "radplot" are valid types for type_plot.')
        else:
            return None


     def get_source_in_rfc(self):
        """Get the images of the source available in the RFC catalog:
                http://astrogeo.org/vlbi/solutions/rfc_2017a
        There are two types of images available: the actual image of the source or the
        correlated flux density versus the projected baseline length plot (radplot).

        Inputs
        ------
        - band : str
            Frequency band at which the plots are requested. Possible values are:
                S, C, X, U, K, Q (in capital letters)
       
        Outputs
        -------
        - url_to_image : dict
            Returns the url where the requested images of the source are located (usually as ps files).
            It is a dictionary with the different bands as keys (S, C, X, U, K, Q).
        - url_to_radplot : dict
            Same as previous one but for plots of the correlated flux density vs projected baseline
            length is located (usually is a ps file).
        In both outputs, it will return an empty dict if there are not files for this particular source.
        """
        return get_rfclink_to_file(self.source)



def website_exists(url):
    """Returns True or False if the provided URL exists or not.

    - url : str
        An url to check if it exists or not.
    """
    try:
        theurl = urllib.request.urlopen(url).code
        return True
    except HTTPError:
        return False


class LinkParser(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self.links = iter([])

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, value in attrs:
                if name == 'href':
                    self.links = chain(self.links, [value])

def get_links(f, parser):
    encoding = f.headers.get_content_charset() or 'UTF-8'
    for line in f:
        parser.feed(line.decode(encoding))
        yield from parser.links

def get_rfclink_to_file(source):
    url = 'http://astrogeo.org/images/{}/'.format(source)
    parser = LinkParser()
    f = urllib.requests.urlopen(url)
    links = get_links(f, parser)
    url_image, url_radplot = {}, {}
    for alink in links:
        if 'pet_map.ps' in alink:
            # Get the band (the url name is SOURCE_BAND_EPOCH_...ps)
            band = alink[alink.index('_')+1]
            if band not in url_image:
                url_image[band] = alink
        elif 'pet_rad.ps' in alink:
            band = alink[alink.index('_')+1]
            if band not in url_radplot:
                url_radplot[band] = alink

    return url_image, url_radplot



