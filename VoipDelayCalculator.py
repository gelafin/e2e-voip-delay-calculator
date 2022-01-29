# Author: Mark Mendez
# Date: 01/29/2022


# TODO: this is copied from the utilization calculator except returns seconds not ms; merge into one class
def calculate_transmission_time_seconds(length_in_bytes: int | float, rate_in_Mbps: int | float) -> float:
    """
    Calculates network transmission time for a packet
    :param length_in_bytes: size of each packet --in bytes--
    :param rate_in_Mbps: transmission rate --in Mbps--
    :return: transmission time --in seconds--
    """
    packet_length = length_in_bytes
    rate = rate_in_Mbps

    # convert all applicable values to bits
    packet_length *= 8  # from bytes to bits
    rate *= 1000 * 1000  # from Mbps to Kbps to bps

    # calculate transmission time in seconds
    transmission_time_seconds = packet_length / rate

    return transmission_time_seconds


def calculate_propagation_delay_seconds(propagation_distance_km: int | float,
                                        propagation_speed_meters_per_second: dict
                                        ):
    """
    Calculates propagation delay
    :param propagation_distance_km:
    :param propagation_speed_meters_per_second:
    :return: propagation delay in seconds
    """
    # convert from km to meters
    propagation_distance_meters = propagation_distance_km * 1000

    # reconstruct from scientific notation like 2.5 * 10^8
    propagation_speed_mps_float = (propagation_speed_meters_per_second['significant_digits']
                                   * 10 ** propagation_speed_meters_per_second['exponent']
                                   )
    propagation_delay_seconds = propagation_distance_meters / propagation_speed_mps_float

    return propagation_delay_seconds


def calculate_end_to_end_voip_delay(known_data: dict):
    """
    Calculates end-to-end voip delay--that is, the time taken to convert and transmit one packet to another host.
    Assumes partial packets are not sent or de-converted.
    :param known_data: dict in the following form:
                       {
                        'conversion_rate_Kbps': int or float,
                        'link_transmission_rate_Mbps': int or float,
                        'packet_length_bytes': int or float,
                        'propagation_distance_km': int or float,
                        'propagation_speed_meters_per_second':
                            {'significant_digits': int or float, 'exponent': int or float}
                       }
    :return: time taken from when conversion begins to when de-conversion begins
    """
    # unpack known variables
    conversion_rate_bps = known_data['conversion_rate_Kbps'] * 1000  # convert to bps
    link_transmission_rate_Mbps = known_data['link_transmission_rate_Mbps']
    packet_length_bytes = known_data['packet_length_bytes']
    propagation_distance_km = known_data['propagation_distance_km']
    propagation_speed_meters_per_second = known_data['propagation_speed_meters_per_second']

    # propagation delay
    propagation_delay_seconds = calculate_propagation_delay_seconds(propagation_distance_km,
                                                                    propagation_speed_meters_per_second
                                                                    )

    # transmission delay
    transmission_delay_seconds = calculate_transmission_time_seconds(packet_length_bytes, link_transmission_rate_Mbps)

    # conversion delay
    packet_length_bits = packet_length_bytes * 8
    conversion_delay_seconds = packet_length_bits / conversion_rate_bps

    # end-to-end voip delay, from start of conversion to end of propagation
    voip_delay_seconds = conversion_delay_seconds + transmission_delay_seconds + propagation_delay_seconds

    # convert to ms
    voip_delay_ms = voip_delay_seconds * 1000

    return voip_delay_ms


if __name__ == '__main__':
    # test
    known_data = {
        'conversion_rate_Kbps': 65,
        'link_transmission_rate_Mbps': 1.8,
        'packet_length_bytes': 65,
        'propagation_distance_km': 712.7,
        'propagation_speed_meters_per_second':
            {'significant_digits': 2.5, 'exponent': 8}  # e.g., 2.5 * 10^8,
        #                                                 where 2.5 is the significant digits, and 8 is the exponent
    }

    result = calculate_end_to_end_voip_delay(known_data)
    print('\nend-to-end voip delay: ', result)

