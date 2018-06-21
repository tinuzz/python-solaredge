from .. import utils
import struct
import logging

class Device(object):

    def __init__(self, dev_id, data):
        self.logger = logging.getLogger(self.__module__)
        self.logger.info('Device %s instantiated' % self.__module__)
        self.dev_id = dev_id
        self.data = data

    # Parse() returns a list of data items, which should be the same length
    # as the list of labels. Can be overridden in subclasses if the standard
    # fmt <-> labels paradigm does not apply.
    def parse(self):
        length = struct.calcsize(self.fmt)
        parsed = [
            struct.unpack(self.fmt, self.data[:length])[i] for i in self.item_idx
        ]

        # If this parser has a post_process method, call it.
        # It acts as filter, i.e. it should return the modified data.
        # The post_process() method can access self.data if it wants to.
        try:
            parsed = self.post_process(parsed)
        except AttributeError:
            pass
        except Exception:
            raise
        return self.device_data(parsed)

    def device_data(self, parsed):
        result = {}
        result["dev_id"] = self.dev_id
        for i in range(len(self.labels)):
            if self.labels[i].lower() == 'date':
                result[self.labels[i]] = utils.format_datestamp(parsed[i])
            elif self.labels[i].lower() == 'time':
                result[self.labels[i]] = utils.format_timestamp(parsed[i])
            else:
                result[self.labels[i]] = parsed[i]
        self.logger.debug('Device data parse result: %s' % str(result))
        return result
