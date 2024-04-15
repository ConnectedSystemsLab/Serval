from datetime import datetime
import os
import pickle
from argparse import ArgumentParser
from xml.etree import ElementTree as ET
import tqdm


def main():
    parser = ArgumentParser()
    parser.add_argument('--data_dir', default='results/filter_results/forest_model')
    parser.add_argument('--cutoff_datetime', default='2021-07-10T00:00:00+00:00',
                        type=lambda s: datetime.fromisoformat(s))
    parser.add_argument(
        '--output_file', default='results/forest_historical_data.pkl')
    parser.add_argument('--metadata_list_file',
                        default='data/all_metadata')
    args = parser.parse_args()
    # aggregate all forest data
    forest_data = {}
    for result_file in os.listdir(args.data_dir):
        if result_file.endswith('.pkl'):
            with open(os.path.join(args.data_dir, result_file), 'rb') as f:
                forest_data.update(pickle.load(f))
    # aggregate metadata
    positive_boundaries=[]
    with open(args.metadata_list_file, 'r') as f:
        for line in tqdm.tqdm(f.readlines()):
            metadata_file = line.strip()
            metadata = open(metadata_file).read()
            metadata = ET.fromstring(metadata)
            asset_id = metadata.find('.//eop:identifier', namespaces={
                'eop': 'http://earth.esa.int/eop'})
            assert asset_id is not None
            asset_id = asset_id.text
            image_id = asset_id[:-len('_3B_AnalyticMS')]  # remove suffix
            if image_id not in forest_data or forest_data[image_id][0] < 0.5:
                continue
            capture_time = metadata.find('.//eop:acquisitionDate', namespaces={
                'eop': 'http://earth.esa.int/eop'})
            assert capture_time is not None
            capture_time = datetime.fromisoformat(capture_time.text)
            if capture_time > args.cutoff_datetime:
                continue
            position = metadata.find('.//gml:coordinates', namespaces={
                'gml': 'http://www.opengis.net/gml'})
            assert position is not None
            position = position.text
            points = []
            for point in position.split(' '):
                x, y = point.split(',')
                x = float(x)
                y = float(y)
                points.append((x, y))
            positive_boundaries.append(points)

    with open(args.output_file, 'wb') as f:
        pickle.dump(positive_boundaries, f)


if __name__ == '__main__':
    main()
