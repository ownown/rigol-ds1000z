from enum import IntEnum
from telnetlib import Telnet
from typing import List

class Rigol:
    class Command:
        QUERY_ID_STRING         = '*IDN?\r\n'
        WAVEFORM_PREAMBLE       = ':WAVEFORM:PREAMBLE?\r\n'
        STOP_SCOPE              = ':STOP\r\n'
        WAVEFORM_SET_CHANNEL    = ':WAVEFORM:SOURCE {channel}\r\n'
        WAVEFORM_SET_MODE       = ':WAVEFORM:MODE {mode}\r\n'
        WAVEFORM_SET_FORMAT     = ':WAVEFORM:FORMAT {format}\r\n'
        WAVEFORM_SET_START      = ':WAVEFORM:START {start}\r\n'
        WAVEFORM_SET_STOP       = ':WAVEFORM:STOP {stop}\r\n'
        WAVEFORM_QUERY_DATA     = ':WAVEFORM:DATA?\r\n'


    class Channel:
        Channel1 = 'CHAN1'
        Channel2 = 'CHAN2'
        Channel3 = 'CHAN3'
        Channel4 = 'CHAN4'


    class Waveform:
        class Format(IntEnum):
            BYTE    = 0
            WORD    = 1
            ASCII   = 2


        class Mode(IntEnum):
            NORMAL  = 0
            MAXIMUM = 1
            RAW     = 2


        class MaximumPointsPerRead(IntEnum):
            BYTE    = 250000
            WORD    = 125000
            ASCII   = 15625 # Does this need special handling?


    def __init__(self, ip, port = 5555):
        self._telnet = Telnet(ip, port)
    

    def __send_command(self, command) -> None:
        self._telnet.write(command.encode('ascii'))
    

    def __send_query(self, query) -> str:
        self._telnet.write(query.encode('ascii'))
        return self._telnet.read_until(b'\n', 2).decode('ascii').strip()


    def __data_query(self, query) -> List[int]:
        self._telnet.write(query.encode('ascii'))
        return [x for x in self._telnet.read_until(b'\n', 1)]


    def get_instrument_string(self) -> str:
        keys = ['Make', 'Model', 'Serial #', 'SW Version']
        return '\n'.join([f'{k:>10} : {v}' for k,v in zip(keys, self.__send_query(self.Command.QUERY_ID_STRING).split(','))])
    

    def get_waveform_info(self) -> List[int]:
        return list(map(int, self.__send_query(self.Command.WAVEFORM_PREAMBLE).split(',')[:3]))


    def stop(self) -> None:
        self.__send_command(self.Command.STOP_SCOPE)


    def set_channel(self, channel) -> None:
        self.__send_command(self.Command.WAVEFORM_SET_CHANNEL.format(channel=channel))


    def set_waveform_format(self, format) -> None:
        self.__send_command(self.Command.WAVEFORM_SET_FORMAT.format(format=format))
    

    def set_waveform_mode(self, mode) -> None:
        self.__send_command(self.Command.WAVEFORM_SET_MODE.format(mode=mode))


    def get_data(self, start_point, stop_point) -> List[int]:
        self.__send_command(self.Command.WAVEFORM_SET_START.format(start=start_point))
        self.__send_command(self.Command.WAVEFORM_SET_STOP.format(stop=stop_point))
        return self.__data_query(self.Command.WAVEFORM_QUERY_DATA)


    def get_all_channel_data(self, channel) -> List[int]:
        self.stop()
        self.set_channel(channel)

        format, mode, points = self.get_waveform_info()

        if format != Rigol.Waveform.Format.BYTE:
            self.set_waveform_format('BYTE')

        if mode != Rigol.Waveform.Mode.RAW:
            self.set_waveform_mode('RAW')

        data = []

        for i in range(1, (points + 1), Rigol.Waveform.MaximumPointsPerRead.BYTE):
            byte_data = self.get_data(i, (i + Rigol.Waveform.MaximumPointsPerRead.BYTE - 1))
            data.extend([x for x in byte_data])

        return data
