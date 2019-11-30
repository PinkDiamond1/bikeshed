# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals
import io
import json
import os
import urllib2
from collections import OrderedDict
from contextlib import closing

from ..messages import *  # noqa


def update(path, dryRun=False):
    say("Downloading MDN Spec Links data...")
    specMapURL = "https://w3c.github.io/mdn-spec-links/SPECMAP.json"
    try:
        with closing(urllib2.urlopen(specMapURL)) as fh:
            jsonString = fh.read()
    except Exception as e:
        die("Couldn't download the MDN Spec Links data.\n{0}", e)
        return

    try:
        data = json.loads(unicode(jsonString), encoding="utf-8",
                          object_pairs_hook=OrderedDict)
    except Exception as e:
        die("The MDN Spec Links data wasn't valid JSON for some reason." +
            " Try downloading again?\n{0}", e)
        return
    writtenPaths = set()
    if not dryRun:
        try:
            p = os.path.join(path, "mdnspeclinks", "SPECMAP.json")
            writtenPaths.add(p)
            with io.open(p, 'w', encoding="utf-8") as fh:
                fh.write(unicode(json.dumps(data, indent=1, ensure_ascii=False,
                                            sort_keys=False)))
            # SPECMAP.json format:
            # {
            #     "https://compat.spec.whatwg.org/": "compat.json",
            #     "https://console.spec.whatwg.org/": "console.json",
            #     "https://dom.spec.whatwg.org/": "dom.json",
            #     ...
            # }
            for specFilename in data.values():
                p = os.path.join(path, "mdnspeclinks", specFilename)
                writtenPaths.add(p)
                mdnSpecLinksBaseURL = "https://w3c.github.io/mdn-spec-links/"
                try:
                    with closing(urllib2.urlopen(mdnSpecLinksBaseURL +
                                                 specFilename)) as fh:
                        fileContents = fh.read()
                except Exception as e:
                    die("Couldn't download the MDN Spec Links " + specFilename +
                        " file.\n{0}", e)
                    return
                with io.open(p, 'w', encoding='utf-8') as fh:
                    print "    " + specFilename
                    fh.write(unicode(fileContents))
        except Exception as e:
            die("Couldn't save MDN Spec Links data to disk.\n{0}", e)
            return
    say("Success!")
    return writtenPaths
