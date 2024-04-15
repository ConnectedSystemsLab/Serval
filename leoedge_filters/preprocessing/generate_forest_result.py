from argparse import ArgumentParser
from xml.etree import ElementTree

import os
import pickle
import tqdm
import shapely



def main():
    parser = ArgumentParser()
    parser.add_argument('--image_file_list', type=str, default='data/all_images')
    parser.add_argument('--metadata_list', type=str, default='data/all_metadata')
    parser.add_argument('--historical_data_file', type=str, required=True)
    parser.add_argument('--output_folder', type=str, required=True)
    parser.add_argument('--job_id', type=int, default=0)
    parser.add_argument('--num_jobs', type=int, default=1)
    args = parser.parse_args()
    with open(args.image_file_list) as f:
        image_file_list = f.read().splitlines()
    with open(args.metadata_list) as f:
        metadata_list = f.read().splitlines()
    assert len(image_file_list) == len(metadata_list)
    historical_data = pickle.load(open(args.historical_data_file, "rb"))
    results = {}
    for image_file, metadata_file in tqdm.tqdm(zip(image_file_list[args.job_id::args.num_jobs], metadata_list[args.job_id::args.num_jobs]), total=len(image_file_list[args.job_id::args.num_jobs])):
        metadata = open(metadata_file).read()
        metadata = ElementTree.fromstring(metadata)
        position = metadata.find('.//gml:coordinates', namespaces={
            'gml': 'http://www.opengis.net/gml'})
        assert position is not None
        position = position.text
        x0, x1, y0, y1 = -180, 180, -180, 180
        points=[]
        for point in position.split(' '):
            x, y = point.split(',')
            x = float(x)
            y = float(y)
            points.append((x, y))
        boundary=shapely.geometry.Polygon(points)
        image_id=(image_file.split('/')[-1].split('.')[0])[:-len('_3B_AnalyticMS')]
        for points in historical_data:
            other_boundary=shapely.geometry.Polygon(points)
            if boundary.intersects(other_boundary):
                results[image_id]=[1,0]
                break
            else:
                results[image_id]=[0,0]
    pickle.dump(results, open(os.path.join(args.output_folder, f"forest_result_{args.job_id}.pkl"), "wb"))


if __name__ == '__main__':
    main()
