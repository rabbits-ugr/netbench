"""
Command for bandwidth testing.
"""

import os

import click
import iperf3
import pandas as pd
from netbench.config import Config
from netbench.types import IPaddress
from netbench.utils import write_results


@click.command()
@click.pass_obj
@click.option('-t', default=10, show_default=True, help='Duration of the benchmark in seconds')
@click.option('-u', default=False, is_flag=True, help='Use UDP instead of TCP.')
@click.argument('server_addr', type=IPaddress())
def bandwidth(config: Config, server_addr: str, t: int, u: bool):
    """
    Bandwidth benchmarking using iperf3.

    The remote server's IP address must be specified.
    """

    client = iperf3.Client()
    client.server_hostname = server_addr
    client.duration = t
    client.protocol = 'udp' if u else 'tcp'

    print('Starting iperf3 benchmark.')
    results = client.run().json

    print('Benchmark finished, saving results.')
    df = pd.DataFrame(columns=['bytes', 'seconds', 'bits_per_second'])
    for interval in results['intervals']:
        df = df.append(pd.DataFrame({
            'bytes': pd.Series([interval['sum']['bytes']], dtype='int'),
            'seconds': pd.Series([interval['sum']['seconds']], dtype='float'),
            'bits_per_second': pd.Series([interval['sum']['bits_per_second']], dtype='float')
        }), ignore_index=True)

    write_results(
        df,
        os.path.join(config.results_path, 'bandwidth'),
        client.protocol
    )