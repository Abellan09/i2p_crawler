"""Custom Feed Exports extension."""
import os

from scrapy.extensions.feedexport import FileFeedStorage


class CustomFileFeedStorage(FileFeedStorage):
    """
    A File Feed Storage extension that overwrites existing files.

    See: https://github.com/scrapy/scrapy/blob/master/scrapy/extensions/feedexport.py#L79
    """

    def open(self, spider):
        """Return the opened file."""
        dirname = os.path.dirname(self.path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

        print "FILE to open ..." + self.path
        # changed from 'ab' to 'wb' to truncate file when it exists
        return open(self.path, 'wb')