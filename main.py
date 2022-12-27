import matplotlib.pyplot as plt

from rigol import Rigol


def main():
    ip = ''

    print('Get I2C data from Rigol DS1000Z scope')
    print()

    scope = Rigol(ip)

    print(scope.get_instrument_string())

    for channel in [Rigol.Channel.Channel1, Rigol.Channel.Channel2]:
        data = scope.get_all_channel_data(channel)
        plt.plot(data)

    plt.show()


if __name__ == '__main__':
    main()
